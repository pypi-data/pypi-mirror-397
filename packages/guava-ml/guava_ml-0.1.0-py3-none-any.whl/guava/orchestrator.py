#!/usr/bin/env python3
"""
orchestrator.py

Central coordinator ("master" / "brain").

Responsibilities:
- Listen for worker connections
- Send commands/batches to workers (data-parallel or pipeline-parallel)
- Receive gradients / metrics / checkpoints on PERSISTENT channels
- Run the top-level training loop
- Coordinate full multi-stage backward across all pipeline shards
- Aggregate inference results from workers (port +9)

Network contract (all TCP):
- Control / registration / ACKs / BACKWARD_READY : master_port+0 (long-lived socket per worker)
- Metrics upload:                                 master_port+1 (short-lived per send)
- Gradients upload:                               master_port+2 (PERSISTENT per worker)
- Activation uplink / relay:                      master_port+3 (reserved / future)
- Activation ACK / heartbeat:                     master_port+4 (reserved / future)
- Resend probe / heartbeat:                       master_port+5 (reserved / future)
- Command ACK legacy port:                        master_port+6 (unused now; ACKs come on +0)
- Checkpoints upload:                             master_port+7 (PERSISTENT per worker)
- Inference result uploads:                       master_port+9 (short-lived per request)

All control messages use MessageProtocol and Message/MessageType.
We run on CPU and act as the source of truth for weights.
"""

from __future__ import annotations

import os
import socket
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple, Iterable

import torch
import torch.nn as nn

from .config import DistributedConfig
from .socket_utils import optimize_socket_for_network
from .protocol import MessageType, Message, MessageProtocol, MessageCorruptedError
from .energy_monitor import get_error_tracker, ErrorSeverity, track_errors  # noqa: F401
from .training_components import build_loss_handler, build_optimizer, build_scheduler


class Orchestrator:
    """
    Orchestrator holds:
    - Authoritative full model weights
    - Optimizer
    - Training scheduler for data-parallel or pipeline-parallel
    - Control sockets for each worker
    - PERSISTENT gradient + checkpoint sockets for each worker
    - Gradient + metric buffers
    - BACKWARD_READY queues for upstream grad handoff between shards

    We support TRUE multi-stage backward for pipeline/model-parallel:
    - Last shard computes CE loss, backward(), uploads grads, and sends BACKWARD_READY
      containing upstream_grad for previous shard.
    - Orchestrator walks upstream shard-by-shard with CONTROL_PIPELINE_BACKWARD,
      feeding that upstream_grad back, causing each shard to backward() and upload
      its own grads and produce the next upstream_grad.
    - After all shards have contributed grads, we average all and step once.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def __init__(self, config: DistributedConfig, mode: str = "orchestrator"):
        # Auto-allocate master_port range if not provided
        if not hasattr(config, "master_port") or config.master_port is None:
            from .autodiscovery_port_manager import AutoDiscoveryPortManager
            job_name = getattr(config, "job_name", None)
            if job_name is None:
                job_name = f"guava_train_{time.strftime('%Y%m%d_%H%M%S')}"
                config.job_name = job_name
            pm = AutoDiscoveryPortManager()
            allocated_port = pm.allocate_port_range(job_id=job_name)
            if allocated_port is None:
                raise RuntimeError("❌ Could not allocate ports for training!")
            config.master_port = allocated_port
            self._port_manager = pm
            print(f"🎯 Auto-allocated ports for job '{job_name}': {allocated_port}-{allocated_port+9}")
        else:
            self._port_manager = None
            print(f"📌 Using manually specified port: {config.master_port}")

        self.cfg = config
        self.mode = mode

        # Model, optimizer, scheduler
        self.model: Optional[nn.Module] = None
        self.optimizer: Optional[torch.optim.Optimizer] = None
        self.scheduler: Optional[Any] = None
        self.loss_handler = build_loss_handler(self.cfg, device=torch.device("cpu"))

        # Global position
        self.global_step = 0
        self.epoch_idx = 0

        # Threads / shutdown
        self._listener_threads: List[threading.Thread] = []
        self._shutdown_flag = threading.Event()

        # Worker registry
        # gpu_id -> { gpu_id, start_layer, end_layer, hostname, ... }
        self.registered_workers: Dict[int, Dict[str, Any]] = {}

        # Control sockets (long-lived)
        self.ctrl_sockets: Dict[int, socket.socket] = {}

        # Persistent gradient sockets
        self.grad_sockets: Dict[int, socket.socket] = {}
        self.grad_sockets_lock = threading.Lock()

        # Persistent checkpoint sockets
        self.chkpt_sockets: Dict[int, socket.socket] = {}
        self.chkpt_sockets_lock = threading.Lock()

        # Gradient and metrics buffers
        self.gradients_lock = threading.Lock()
        self.collected_gradients: Dict[int, Dict[str, torch.Tensor]] = {}
        self.metrics_lock = threading.Lock()
        self.collected_metrics: List[Dict[str, Any]] = []
        self.worker_reconnect_count: Dict[int, int] = {}

        # Inference aggregation (NEW)
        self._inference_results_lock = threading.Lock()
        self._inference_results: Dict[int, List[Dict[str, Any]]] = {}
        self._inference_waiters: Dict[int, Tuple[threading.Event, int]] = {}
        self._inference_step = 0

        # BACKWARD_READY queues
        self._backward_lock = threading.Lock()
        self._backward_ready_queues: Dict[int, List[Message]] = {}

        # Bring up background listener servers (+0, +1, +2, +7, +9)
        self._start_listener_threads()

    def __enter__(self):
        """Allow 'with Orchestrator(cfg) as orch:' usage."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure graceful shutdown and do not suppress exceptions."""
        self.shutdown()
        return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register_model(self, model: nn.Module) -> None:
        """
        Attach the authoritative (full) model and create the optimizer.
        """
        self.model = model
        self.model.train(True)
        self.optimizer = build_optimizer(self.cfg, self.model.parameters())
        self.scheduler = build_scheduler(self.cfg, self.optimizer)

        try:
            first_param = next(self.model.parameters())
            self.loss_handler.set_device(first_param.device)
        except StopIteration:
            self.loss_handler.set_device(torch.device("cpu"))

    def wait_for_workers(
        self,
        expected: Optional[int] = None,
        timeout: Optional[float] = None,
        poll_interval: float = 0.1,
    ) -> None:
        """
        Block until N workers are registered and control sockets are live.

        Args:
            expected: number of workers expected (default = cfg.num_workers)
            timeout: seconds to wait (None = forever)
            poll_interval: polling sleep seconds
        """
        target = expected if expected is not None else self.cfg.num_workers
        start_ts = time.time()
        while len(self.registered_workers) < target:
            if timeout is not None and (time.time() - start_ts) > timeout:
                raise TimeoutError(
                    f"Timed out waiting for {target} workers; "
                    f"only {len(self.registered_workers)} registered"
                )
            time.sleep(poll_interval)

    def start_training(
        self,
        train_loader: Iterable,
        val_loader: Optional[Iterable] = None,
        num_epochs: int = 1,
        val_interval: int = 100,
    ) -> None:
        """
        Main training driver.
        - Pipeline/model-parallel => pipeline scheduler with multi-stage backward
        - Else => synchronous data-parallel
        """
        assert self.model is not None, "call register_model(model) first"
        assert self.optimizer is not None, "optimizer not created"

        print("======================================================================")
        print("GUAVA ORCHESTRATOR TRAIN LOOP")
        print(f"num_workers: {self.cfg.num_workers}")
        print(
            "parallelism: "
            f"data={self.cfg.data_parallel}, "
            f"model={self.cfg.model_parallel}, "
            f"pipeline={self.cfg.pipeline_parallel}"
        )
        print("======================================================================")

        if self.cfg.pipeline_parallel or self.cfg.model_parallel:
            self._start_training_pipeline_parallel(
                train_loader=train_loader,
                val_loader=val_loader,
                num_epochs=num_epochs,
                val_interval=val_interval,
            )
        else:
            self._start_training_data_parallel(
                train_loader=train_loader,
                val_loader=val_loader,
                num_epochs=num_epochs,
                val_interval=val_interval,
            )

        print("Training loop finished.")

    # ------------------------------------------------------------------
    # Inference (NEW)
    # ------------------------------------------------------------------
    def run_inference(
        self,
        data_loader: Iterable,
        *,
        timeout: float = 60.0,
        expect_workers: Optional[int] = None,
    ) -> List[List[Dict[str, Any]]]:
        """
        Dispatch inference batches to connected workers and collect results.

        Returns a list over batches, where each batch entry is a list of
        per-worker results dicts sorted by gpu_id:
        [{gpu_id, step, logits, token_count, timestamp}, ...]
        """
        if data_loader is None:
            return []

        if self.model is not None:
            self.model.eval()

        all_results: List[List[Dict[str, Any]]] = []

        for batch in data_loader:
            self._inference_step += 1
            step_id = self._inference_step

            input_tensor = self._normalize_inference_inputs(batch)
            payload_inputs = input_tensor.detach().cpu().tolist()

            msg = Message(
                msg_type=MessageType.CONTROL_INFERENCE_STEP,
                payload={"input_ids": payload_inputs},
                metadata={"ack_required": True},
                step=step_id,
                phase="infer",
            )

            self._broadcast_ctrl(msg)

            expected = expect_workers
            if expected is None:
                expected = max(len(self.ctrl_sockets), 1)

            try:
                step_results = self._wait_for_inference_results(
                    step_id,
                    expected=expected,
                    timeout=timeout,
                )
            except TimeoutError:
                raise TimeoutError(
                    f"Timed out waiting for inference results (step {step_id}, expected={expected})"
                )

            all_results.append(step_results)

        return all_results

    def _normalize_inference_inputs(self, batch: Any) -> torch.Tensor:
        """Extract an input tensor from various dataloader batch formats."""
        candidate: Any = batch
        if isinstance(batch, dict):
            if "input_ids" not in batch:
                raise ValueError("Inference batch dict must contain 'input_ids'")
            candidate = batch["input_ids"]
        elif isinstance(batch, (list, tuple)):
            if not batch:
                raise ValueError("Empty batch provided for inference")
            candidate = batch[0]

        if isinstance(candidate, torch.Tensor):
            tensor = candidate
        else:
            tensor = torch.as_tensor(candidate, dtype=torch.long)

        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)

        return tensor

    def _wait_for_inference_results(
        self,
        step: int,
        *,
        expected: int,
        timeout: float,
    ) -> List[Dict[str, Any]]:
        """Wait until we have at least `expected` results for this step."""
        event = threading.Event()
        expected = max(1, int(expected))

        with self._inference_results_lock:
            existing = self._inference_results.get(step, [])
            if len(existing) >= expected:
                results = self._inference_results.pop(step, existing)
                return self._sort_inference_results(list(results))

            self._inference_waiters[step] = (event, expected)

        if not event.wait(timeout):
            with self._inference_results_lock:
                self._inference_waiters.pop(step, None)
                results = self._inference_results.pop(step, [])
            raise TimeoutError("Inference results timed out")

        with self._inference_results_lock:
            results = self._inference_results.pop(step, [])
            self._inference_waiters.pop(step, None)

        return self._sort_inference_results(list(results))

    @staticmethod
    def _sort_inference_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(results, key=lambda item: item.get("gpu_id", -1))

    # ------------------------------------------------------------------
    # Checkpoint save
    # ------------------------------------------------------------------
    @track_errors(severity=ErrorSeverity.WARNING, reraise=False)
    def save_checkpoint(self, path: str) -> None:
        """Save orchestrator's authoritative model weights to disk."""
        if self.model is None:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"[orchestrator] checkpoint saved -> {path}")

    # ------------------------------------------------------------------
    # Data-parallel training loop
    # ------------------------------------------------------------------
    def _start_training_data_parallel(
        self,
        train_loader: Iterable,
        val_loader: Optional[Iterable],
        num_epochs: int,
        val_interval: int,
    ) -> None:
        """Data-parallel training with worker failure detection, recovery, and resend logic."""
        for epoch in range(num_epochs):
            self.epoch_idx = epoch
            print(f"[Epoch {epoch+1}/{num_epochs}] (data-parallel)")

            for _, batch in enumerate(train_loader):
                self.global_step += 1
                input_ids, labels = batch

                # Build step message
                step_msg = Message(
                    msg_type=MessageType.CONTROL_DATA_PARALLEL_STEP,
                    payload={
                        "input_ids": input_ids.tolist() if isinstance(input_ids, torch.Tensor) else input_ids,
                        "labels": labels.tolist() if isinstance(labels, torch.Tensor) else labels,
                    },
                    metadata={"ack_required": True},
                    step=self.global_step,
                    phase="train",
                )

                max_send_attempts = 3
                step_success = False

                for send_attempt in range(max_send_attempts):
                    # Check if any workers flagged corruption and need resend
                    with self._backward_lock:
                        resend_needed = getattr(self, "_resend_needed", set())
                        if resend_needed:
                            print(f"[orchestrator] 🔄 Attempt {send_attempt+1}: Resending batch to GPUs: {resend_needed}")
                            self._resend_needed = set()

                    # Broadcast to all workers with small retry
                    broadcast_success = False
                    for broadcast_attempt in range(3):
                        try:
                            self._broadcast_ctrl(step_msg)
                            broadcast_success = True
                            break
                        except Exception as e:
                            print(f"[orchestrator] ⚠️ Broadcast sub-attempt {broadcast_attempt+1}/3 failed: {e}")
                            if broadcast_attempt < 2:
                                print(f"[orchestrator] 🔄 Retrying broadcast in 3s...")
                                time.sleep(3)
                            else:
                                print(f"[orchestrator] ❌ Broadcast failed after 3 sub-attempts")

                    if not broadcast_success:
                        print("[orchestrator] ❌ Cannot send batch to workers")
                        if send_attempt == max_send_attempts - 1:
                            print("[orchestrator] ❌ All broadcast attempts exhausted, emergency checkpoint")
                            self._emergency_checkpoint()
                            return
                        else:
                            print(f"[orchestrator] 🔄 Will retry entire send (attempt {send_attempt+2}/{max_send_attempts})...")
                            time.sleep(5)
                            continue

                    # Wait for gradients + step
                    success = self._aggregate_and_step(pipeline_mode=False)

                    if success:
                        step_success = True
                        break

                    print(f"[orchestrator] ⚠️ Step failed on attempt {send_attempt+1}/{max_send_attempts}")

                    # If corruption, retry
                    with self._backward_lock:
                        resend_needed = getattr(self, "_resend_needed", set())
                        if resend_needed and send_attempt < max_send_attempts - 1:
                            print(f"[orchestrator] 🔄 Corruption detected, will resend to {resend_needed}...")
                            time.sleep(2)
                            continue

                    # Otherwise, wait for recovery and try again (unless final attempt)
                    if send_attempt < max_send_attempts - 1:
                        print("[orchestrator] ⏳ Waiting 15s for workers to recover...")
                        time.sleep(15)
                        alive_count = len([s for s in self.ctrl_sockets.values() if s is not None])

                        if alive_count == 0:
                            print("[orchestrator] ❌ No workers alive, aborting training")
                            self._emergency_checkpoint()
                            return
                        elif alive_count < self.cfg.num_workers:
                            print(f"[orchestrator] ⚠️ Only {alive_count}/{self.cfg.num_workers} workers alive")
                            print(f"[orchestrator] 🔄 Attempting retry with partial worker set...")
                            continue
                        else:
                            print(f"[orchestrator] ✅ All {alive_count} workers alive, retrying...")
                            continue
                    else:
                        # Final attempt failed
                        print("[orchestrator] ❌ All send attempts exhausted")
                        print("[orchestrator] ⏳ Final 30s grace period for workers...")
                        time.sleep(30)
                        alive_count = len([s for s in self.ctrl_sockets.values() if s is not None])
                        if alive_count == 0:
                            print("[orchestrator] ❌ No workers alive, aborting training")
                            self._emergency_checkpoint()
                            return
                        else:
                            print(f"[orchestrator] ⚠️ {alive_count} workers alive but step failed, continuing to next batch...")
                            break

                if not step_success:
                    print(f"[orchestrator] ⚠️ Step {self.global_step} failed after all attempts, skipping...")
                    continue

                # Drain metrics
                for m in self._drain_metrics():
                    if m.get("loss") is not None:
                        try:
                            print(f"[step {m['step']}] gpu{m['gpu_id']} loss={m['loss']:.4f}")
                        except Exception:
                            print(f"[step {m.get('step','?')}] gpu{m.get('gpu_id','?')} loss={m.get('loss')}")

                # Validation
                if val_loader is not None and (self.global_step % val_interval == 0):
                    try:
                        val_loss = self._run_validation(val_loader)
                        print(f"[val @ step {self.global_step}] loss={val_loss:.4f}")
                    except Exception as e:
                        print(f"[orchestrator] ⚠️ Validation failed: {e}")

            print(f"[orchestrator] ✅ Epoch {epoch+1} completed")

    @track_errors(severity=ErrorSeverity.CRITICAL, reraise=False)
    def _emergency_checkpoint(self) -> None:
        """Save model state when training is interrupted and shut down."""
        if self.model is None:
            return
        os.makedirs(self.cfg.checkpoint_dir, exist_ok=True)
        ckpt_path = os.path.join(
            self.cfg.checkpoint_dir,
            f"emergency_step{self.global_step}.pt",
        )
        self.save_checkpoint(ckpt_path)
        print(f"[orchestrator] 💾 Emergency checkpoint saved: {ckpt_path}")
        self.shutdown()

    # ------------------------------------------------------------------
    # Pipeline/model-parallel training
    # ------------------------------------------------------------------
    def _start_training_pipeline_parallel(
        self,
        train_loader: Iterable,
        val_loader: Optional[Iterable],
        num_epochs: int,
        val_interval: int,
    ) -> None:
        """
        Full pipeline/model-parallel with true multi-stage backward.
        """
        for epoch in range(num_epochs):
            self.epoch_idx = epoch
            print(f"[Epoch {epoch+1}/{num_epochs}] (pipeline/model-parallel)")

            for _, batch in enumerate(train_loader):
                self.global_step += 1
                input_ids, labels = batch

                self._pipeline_single_step(
                    input_ids=input_ids,
                    labels=labels,
                    step=self.global_step,
                    phase="train",
                )

                # Metrics from all shards (loss only printed from last shard)
                for m in self._drain_metrics():
                    if m.get("loss") is not None:
                        print(
                            f"[step {m['step']}] "
                            f"gpu{m['gpu_id']} loss={m['loss']:.4f}"
                        )

                # Validation on orchestrator model every val_interval
                if val_loader is not None and (self.global_step % val_interval == 0):
                    val_loss = self._run_validation(val_loader)
                    print(f"[val @ step {self.global_step}] loss={val_loss:.4f}")

    @track_errors(severity=ErrorSeverity.CRITICAL)
    def _pipeline_single_step(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor,
        step: int,
        phase: str,
    ) -> None:
        """
        Execute ONE full pipeline step with upstream gradient chaining.

        Steps:
        (1) Broadcast CONTROL_PIPELINE_PHASE1 → all shards run forward slice.
        (2) Send CONTROL_PIPELINE_PHASE2 ONLY to LAST shard → CE + backward init.
        (3) Iteratively walk upstream with CONTROL_PIPELINE_BACKWARD for each
            previous shard using upstream_grad handed back in BACKWARD_READY.
        (4) After all shards uploaded GRADIENTS_UPLOAD, average & step.
        """
        last_gpu = self.cfg.num_workers - 1
        micro_batches = int(self.cfg.micro_batches)

        # Phase 1: forward across shards
        phase1_msg = Message(
            msg_type=MessageType.CONTROL_PIPELINE_PHASE1,
            payload={
                "input_ids": input_ids.tolist(),
            },
            metadata={
                "ack_required": True,
                "micro_batches": micro_batches,
            },
            step=step,
            phase=phase,
        )
        self._broadcast_ctrl(phase1_msg)

        # Phase 2: start backward on LAST shard (needs labels)
        phase2_msg = Message(
            msg_type=MessageType.CONTROL_PIPELINE_PHASE2,
            payload={
                "labels": labels.tolist(),
            },
            metadata={
                "ack_required": True,
                "micro_batches": micro_batches,
            },
            step=step,
            phase=phase,
        )
        self._send_ctrl_to(last_gpu, phase2_msg)

        # Last shard does CE + backward + upload grads + BACKWARD_READY with upstream_grad
        upstream_grad = self._wait_backward_ready(gpu_id=last_gpu, step=step)

        # Backward chain upstream
        for gid in range(last_gpu - 1, -1, -1):
            back_msg = Message(
                msg_type=MessageType.CONTROL_PIPELINE_BACKWARD,
                payload={"upstream_grad": upstream_grad},
                metadata={"ack_required": True},
                step=step,
                phase=phase,
                gpu_id=gid,
            )
            self._send_ctrl_to(gid, back_msg)
            upstream_grad = self._wait_backward_ready(gpu_id=gid, step=step)

        # Aggregate all grads and step
        self._aggregate_and_step(pipeline_mode=True)

    # ------------------------------------------------------------------
    # Validation (on orchestrator CPU copy)
    # ------------------------------------------------------------------
    @track_errors(severity=ErrorSeverity.WARNING, reraise=False)
    @torch.no_grad()
    def _run_validation(self, val_loader: Iterable) -> float:
        """
        Simple validation on the orchestrator model.
        Computes average next-token cross-entropy.
        """
        assert self.model is not None
        self.model.eval()

        total_loss = 0.0
        total_tokens = 0

        label_key = getattr(self.loss_handler, "label_key", "labels") if self.loss_handler else "labels"

        for (inp_ids, lbls) in val_loader:
            logits = self.model(inp_ids)  # [B,T,V]
            batch = {}
            if lbls is not None:
                batch[label_key] = lbls
                if isinstance(lbls, torch.Tensor):
                    n_tok = lbls.numel()
                else:
                    n_tok = torch.as_tensor(lbls).numel()
            else:
                if isinstance(inp_ids, torch.Tensor):
                    n_tok = inp_ids.numel()
                else:
                    n_tok = torch.as_tensor(inp_ids).numel()

            loss = None
            if self.loss_handler is not None:
                loss = self.loss_handler.compute(logits, batch, device=logits.device)

            if loss is None:
                continue

            total_loss += float(loss.detach().item()) * n_tok
            total_tokens += n_tok

        self.model.train(True)

        return 0.0 if total_tokens == 0 else (total_loss / total_tokens)

    # ------------------------------------------------------------------
    # Background listener servers
    # ------------------------------------------------------------------
    def _start_listener_threads(self) -> None:
        """
        Spin up background servers:
          +0 : control/register/ACKs/BACKWARD_READY  (long-lived per worker)
          +1 : metrics uploads (METRICS_STEP)
          +2 : gradient uploads (PERSISTENT per worker)
          +7 : checkpoint uploads (PERSISTENT per worker)
          +9 : inference result uploads (short-lived per request)

        Ports +3,+4,+5,+6 are reserved (activation relay, heartbeats, etc.).
        """
        t0 = threading.Thread(target=self._ctrl_server, daemon=True)
        t1 = threading.Thread(target=self._metrics_server, daemon=True)
        t2 = threading.Thread(target=self._grad_server, daemon=True)
        t7 = threading.Thread(target=self._checkpoint_server, daemon=True)
        t9 = threading.Thread(target=self._inference_server, daemon=True)

        self._listener_threads = [t0, t1, t2, t7, t9]
        for t in self._listener_threads:
            t.start()

    def _bind_listen(self, port_offset: int) -> socket.socket:
        """
        Bind and listen on (cfg.master_port + port_offset).
        """
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        optimize_socket_for_network(lsock)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # macOS: SO_REUSEPORT allows reuse of ports after crash
        if hasattr(socket, "SO_REUSEPORT"):
            try:
                lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass  # Not available on all platforms

        lsock.bind((self.cfg.master_ip, self.cfg.master_port + port_offset))
        lsock.listen()
        return lsock

    # ------------------------------------------------------------------
    # CONTROL / REGISTRATION SERVER (master_port+0)
    # ------------------------------------------------------------------
    def _ctrl_server(self) -> None:
        """
        Accept worker control sockets on master_port+0.

        Per new worker connection:
          1. First message MUST be CONTROL_HELLO with:
             {gpu_id,start_layer,end_layer,hostname}
          2. Store socket in ctrl_sockets[gpu_id] and init BACKWARD_READY queue.
          3. Reply CONTROL_ACK(status="registered").
          4. Then poll forever for:
             - CONTROL_ACK   (barrier ACKs)
             - CONTROL_HEARTBEAT
             - BACKWARD_READY (contains upstream_grad after backward())
             - CONTROL_RESEND_REQUEST (worker asks for resend due to corruption)
        """
        lsock = self._bind_listen(0)
        print(
            f"[orchestrator] ctrl_server listening on "
            f"{self.cfg.master_ip}:{self.cfg.master_port}+0"
        )

        while not self._shutdown_flag.is_set():
            try:
                conn, addr = lsock.accept()
            except OSError:
                break

            threading.Thread(
                target=self._handle_ctrl_connection,
                args=(conn, addr),
                daemon=True,
            ).start()

    def _handle_ctrl_connection(
        self,
        conn: socket.socket,
        addr: Tuple[str, int],
    ) -> None:
        """Manage a single worker's control socket for its lifetime."""
        optimize_socket_for_network(conn)

        try:
            # Expect CONTROL_HELLO to register the worker
            hello_msg = MessageProtocol.receive_message(
                conn, timeout=None, channel_name="orchestrator-ctrl-hello"
            )
            if hello_msg is None or hello_msg.msg_type != MessageType.CONTROL_HELLO:
                conn.close()
                return

            hello = hello_msg.payload
            gpu_id = int(hello["gpu_id"])
            is_reconnect = hello.get("reconnect", False)
            worker_last_step = hello.get("last_step", -1)

            if is_reconnect:
                print(f"[orchestrator] 🔄 GPU{gpu_id} RECONNECTING from {addr} (was at step {worker_last_step})")

                # Track reconnection count
                self.worker_reconnect_count[gpu_id] = self.worker_reconnect_count.get(gpu_id, 0) + 1
                print(f"[orchestrator] 🔄 GPU{gpu_id} reconnection #{self.worker_reconnect_count[gpu_id]}")

                # Clean up stale state for this worker
                with self.gradients_lock:
                    old_grads = self.collected_gradients.pop(gpu_id, None)
                    if old_grads:
                        print(f"[orchestrator] 🧹 Cleared {len(old_grads)} stale gradients for GPU{gpu_id}")

                with self._backward_lock:
                    if gpu_id in self._backward_ready_queues:
                        old_count = len(self._backward_ready_queues[gpu_id])
                        self._backward_ready_queues[gpu_id].clear()
                        if old_count > 0:
                            print(f"[orchestrator] 🧹 Cleared {old_count} stale BACKWARD_READY msgs for GPU{gpu_id}")
                    if hasattr(self, "_resend_needed"):
                        if gpu_id in self._resend_needed:
                            self._resend_needed.discard(gpu_id)
                            print(f"[orchestrator] 🧹 Removed GPU{gpu_id} from resend list")

                print(f"[orchestrator] ✅ GPU{gpu_id} state cleaned for reconnection")
            else:
                print(f"[orchestrator] ✅ GPU{gpu_id} initial registration from {addr}")

            # Record/Update worker info and socket
            self.registered_workers[gpu_id] = hello
            self.ctrl_sockets[gpu_id] = conn

            # Init/reset BACKWARD_READY queue
            with self._backward_lock:
                self._backward_ready_queues[gpu_id] = []

            # ACK payload (also ships dynamic model config if needed)
            model_config_payload = {
                "d_model": self.cfg.d_model,
                "n_layers": self.cfg.n_layers,
                "n_heads": self.cfg.n_heads,
                "vocab_size": self.cfg.vocab_size,
                "max_seq_len": self.cfg.max_seq_len,
                "dropout": self.cfg.dropout,
                "batch_size": self.cfg.batch_size,
                "max_grad_norm": self.cfg.max_grad_norm,
            }

            model_class_name = getattr(self.cfg, "model_class_name", None)
            model_source_code = getattr(self.cfg, "model_source_code", None)
            model_init_kwargs = getattr(self.cfg, "model_init_kwargs", None)

            ack_msg = Message(
                msg_type=MessageType.CONTROL_ACK,
                payload={
                    "status": "registered",
                    "gpu_id": gpu_id,
                    "model_config": model_config_payload,
                    "model_class_name": model_class_name,
                    "model_source_code": model_source_code,
                    "model_init_kwargs": model_init_kwargs,
                    "current_step": self.global_step,
                    "is_reconnect": is_reconnect,
                },
                gpu_id=gpu_id,
            )
            MessageProtocol.send_message(conn, ack_msg)

            if is_reconnect:
                print(f"[orchestrator] 📡 Sent reconnection ACK to GPU{gpu_id} (current step: {self.global_step})")
                try:
                    ready_msg = MessageProtocol.receive_message(conn, timeout=30.0)
                    if ready_msg and ready_msg.msg_type == MessageType.CONTROL_ACK:
                        print(f"[orchestrator] ✅ GPU{gpu_id} confirmed ready after reconnection")
                    else:
                        print(f"[orchestrator] ⚠️ GPU{gpu_id} did not confirm readiness")
                except Exception as e:
                    print(f"[orchestrator] ⚠️ GPU{gpu_id} readiness check failed: {e}")

            # Enter control receive loop
            conn.settimeout(0.1)
            while not self._shutdown_flag.is_set():
                try:
                    in_msg = MessageProtocol.receive_message(
                        conn, timeout=0.1, channel_name=f"orchestrator-ctrl[GPU{gpu_id}]"
                    )

                    if in_msg is None:
                        # Worker closed cleanly
                        break

                    if in_msg.msg_type == MessageType.CONTROL_ACK:
                        # Barrier ACK after broadcasted control command
                        pass

                    elif in_msg.msg_type == MessageType.CONTROL_HEARTBEAT:
                        # liveness ping (no-op)
                        pass

                    elif in_msg.msg_type == MessageType.BACKWARD_READY:
                        with self._backward_lock:
                            self._backward_ready_queues[gpu_id].append(in_msg)

                    elif in_msg.msg_type == MessageType.CONTROL_RESEND_REQUEST:
                        reason = in_msg.payload.get("reason", "unknown") if in_msg.payload else "unknown"
                        step = in_msg.step if in_msg.step is not None else "?"
                        print(f"[orchestrator] 🔄 GPU{gpu_id} requests resend for step {step} (reason: {reason})")
                        with self._backward_lock:
                            if not hasattr(self, "_resend_needed"):
                                self._resend_needed = set()
                            self._resend_needed.add(gpu_id)
                        with self.gradients_lock:
                            self.collected_gradients.pop(gpu_id, None)

                    else:
                        # future message types
                        pass

                except socket.timeout:
                    continue
                except MessageCorruptedError:
                    print(f"[orchestrator] ⚠️ Corrupt data from GPU{gpu_id}, ignoring")
                    continue
                except (ConnectionResetError, ConnectionAbortedError):
                    break

        finally:
            # Do not close here; ctrl_sockets[gpu_id] is the live channel.
            pass

    # ------------------------------------------------------------------
    # METRICS SERVER (+1)
    # ------------------------------------------------------------------
    def _metrics_server(self) -> None:
        """Workers connect, send one METRICS_STEP Message, then close."""
        lsock = self._bind_listen(1)
        print(
            f"[orchestrator] metrics_server listening on "
            f"{self.cfg.master_ip}:{self.cfg.master_port}+1"
        )

        while not self._shutdown_flag.is_set():
            try:
                conn, _ = lsock.accept()
            except OSError:
                break

            threading.Thread(
                target=self._handle_metrics_conn,
                args=(conn,),
                daemon=True,
            ).start()

    def _handle_metrics_conn(self, conn: socket.socket) -> None:
        try:
            msg = MessageProtocol.receive_message(conn, timeout=None, channel_name="orchestrator-metrics")
            if msg is not None and msg.msg_type == MessageType.METRICS_STEP:
                with self.metrics_lock:
                    self.collected_metrics.append(msg.payload)
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # GRADIENT SERVER (+2) - PERSISTENT
    # ------------------------------------------------------------------
    def _grad_server(self) -> None:
        """
        Accept PERSISTENT gradient upload connections.
        Each worker connects once at startup, sends hello, then connection
        stays open for the entire training session.
        """
        lsock = self._bind_listen(2)
        print(
            f"[orchestrator] grad_server (persistent) listening on "
            f"{self.cfg.master_ip}:{self.cfg.master_port}+2"
        )

        while not self._shutdown_flag.is_set():
            try:
                conn, addr = lsock.accept()
            except OSError:
                break

            threading.Thread(
                target=self._handle_grad_conn_persistent,
                args=(conn, addr),
                daemon=True,
            ).start()

    def _handle_grad_conn_persistent(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """
        Handle ONE worker's persistent gradient upload channel.

        Flow:
        1. Receive hello handshake with gpu_id (GRADIENTS_UPLOAD with payload.hello==True)
        2. Store socket in self.grad_sockets[gpu_id]
        3. Loop receiving GRADIENTS_UPLOAD messages (grad dicts)
        4. On connection close/error, cleanup
        """
        optimize_socket_for_network(conn)
        gpu_id = None

        try:
            conn.settimeout(10.0)
            hello_msg = MessageProtocol.receive_message(conn, timeout=10.0, channel_name="orchestrator-gradients-hello")

            if hello_msg is None or hello_msg.msg_type != MessageType.GRADIENTS_UPLOAD:
                print(f"[orchestrator] grad channel from {addr}: invalid hello")
                conn.close()
                return

            if isinstance(hello_msg.payload, dict) and hello_msg.payload.get("hello"):
                gpu_id = int(hello_msg.gpu_id if hello_msg.gpu_id is not None else -1)
            else:
                print(f"[orchestrator] grad channel from {addr}: missing hello flag")
                conn.close()
                return

            with self.grad_sockets_lock:
                self.grad_sockets[gpu_id] = conn

            print(f"[orchestrator] ✅ persistent gradient channel established for GPU{gpu_id} from {addr}")

            conn.settimeout(0.5)
            while not self._shutdown_flag.is_set():
                try:
                    msg = MessageProtocol.receive_message(conn, timeout=0.5, channel_name=f"orchestrator-gradients[GPU{gpu_id}]")

                    if msg is None:
                        print(f"[orchestrator] GPU{gpu_id} gradient channel closed by worker")
                        break

                    if msg.msg_type == MessageType.GRADIENTS_UPLOAD:
                        grads_dict = msg.payload.get("gradients", {}) if msg.payload else {}
                        with self.gradients_lock:
                            self.collected_gradients[gpu_id] = grads_dict

                    elif msg.msg_type == MessageType.CONTROL_HEARTBEAT:
                        pass

                except socket.timeout:
                    continue
                except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                    print(f"[orchestrator] GPU{gpu_id} gradient channel error: {e}")
                    break

        except Exception as e:
            print(f"[orchestrator] gradient channel exception from {addr}: {e}")

        finally:
            if gpu_id is not None:
                with self.grad_sockets_lock:
                    self.grad_sockets.pop(gpu_id, None)
                print(f"[orchestrator] GPU{gpu_id} gradient channel cleaned up")

            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # CHECKPOINT SERVER (+7) - PERSISTENT
    # ------------------------------------------------------------------
    def _checkpoint_server(self) -> None:
        """Accept PERSISTENT checkpoint upload connections."""
        lsock = self._bind_listen(7)
        print(
            f"[orchestrator] checkpoint_server (persistent) listening on "
            f"{self.cfg.master_ip}:{self.cfg.master_port}+7"
        )

        while not self._shutdown_flag.is_set():
            try:
                conn, addr = lsock.accept()
            except OSError:
                break

            threading.Thread(
                target=self._handle_checkpoint_conn_persistent,
                args=(conn, addr),
                daemon=True,
            ).start()

    def _handle_checkpoint_conn_persistent(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle ONE worker's persistent checkpoint upload channel (with reconnection)."""
        optimize_socket_for_network(conn)
        gpu_id = None

        try:
            conn.settimeout(10.0)
            hello_msg = MessageProtocol.receive_message(conn, timeout=10.0, channel_name="orchestrator-checkpoint-hello")

            if hello_msg is None or hello_msg.msg_type != MessageType.CHECKPOINT_SHARD_UPLOAD:
                print(f"[orchestrator] checkpoint channel from {addr}: invalid hello")
                conn.close()
                return

            if isinstance(hello_msg.payload, dict) and hello_msg.payload.get("hello"):
                gpu_id = int(hello_msg.gpu_id if hello_msg.gpu_id is not None else -1)
                is_reconnect = hello_msg.payload.get("reconnect", False)
            else:
                print(f"[orchestrator] checkpoint channel from {addr}: missing hello flag")
                conn.close()
                return

            if is_reconnect:
                print(f"[orchestrator] 🔄 GPU{gpu_id} checkpoint channel RECONNECTING from {addr}")

            with self.chkpt_sockets_lock:
                old_sock = self.chkpt_sockets.get(gpu_id)
                if old_sock is not None and old_sock is not conn:
                    try:
                        old_sock.close()
                        print(f"[orchestrator] 🧹 Closed stale checkpoint socket for GPU{gpu_id}")
                    except Exception:
                        pass
                self.chkpt_sockets[gpu_id] = conn

            status = "reconnected" if is_reconnect else "established"
            print(f"[orchestrator] ✅ checkpoint channel {status} for GPU{gpu_id} from {addr}")

            conn.settimeout(0.5)
            while not self._shutdown_flag.is_set():
                try:
                    msg = MessageProtocol.receive_message(conn, timeout=0.5, channel_name=f"orchestrator-checkpoint[GPU{gpu_id}]")

                    if msg is None:
                        print(f"[orchestrator] GPU{gpu_id} checkpoint channel closed by worker")
                        break

                    if msg.msg_type == MessageType.CHECKPOINT_SHARD_UPLOAD:
                        payload = msg.payload or {}
                        filename = payload.get("filename", f"worker{gpu_id}_final.pt")
                        state_dict = payload.get("state_dict")
                        if state_dict is not None:
                            os.makedirs(self.cfg.checkpoint_dir, exist_ok=True)
                            out_path = os.path.join(self.cfg.checkpoint_dir, filename)
                            torch.save(state_dict, out_path)
                            print(f"[orchestrator] checkpoint from GPU{gpu_id} -> {out_path}")
                            try:
                                conn.sendall(b"\x01")
                            except Exception:
                                pass

                    elif msg.msg_type == MessageType.CONTROL_HEARTBEAT:
                        pass

                except socket.timeout:
                    continue
                except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                    print(f"[orchestrator] GPU{gpu_id} checkpoint channel error: {e}")
                    break

        except Exception as e:
            print(f"[orchestrator] checkpoint channel exception from {addr}: {e}")

        finally:
            if gpu_id is not None:
                with self.chkpt_sockets_lock:
                    self.chkpt_sockets.pop(gpu_id, None)
                print(f"[orchestrator] GPU{gpu_id} checkpoint channel cleaned up")

            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # INFERENCE RESULT SERVER (+9)  (NEW)
    # ------------------------------------------------------------------
    def _inference_server(self) -> None:
        """Listen for inference result uploads from workers."""
        lsock = self._bind_listen(9)
        print(
            f"[orchestrator] inference_server listening on "
            f"{self.cfg.master_ip}:{self.cfg.master_port}+9"
        )

        while not self._shutdown_flag.is_set():
            try:
                conn, addr = lsock.accept()
            except OSError:
                break

            threading.Thread(
                target=self._handle_inference_conn,
                args=(conn, addr),
                daemon=True,
            ).start()

    def _handle_inference_conn(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle a single inference result upload connection."""
        optimize_socket_for_network(conn)
        try:
            msg = MessageProtocol.receive_message(
                conn,
                timeout=None,
                channel_name="orchestrator-inference",
            )

            if msg is None:
                return

            if msg.msg_type != MessageType.INFERENCE_RESULT_UPLOAD:
                print(
                    f"[orchestrator] ⚠️ Unexpected message on inference channel from {addr}: {msg.msg_type}"
                )
                return

            payload = msg.payload or {}
            gpu_id = int(msg.gpu_id if msg.gpu_id is not None else payload.get("gpu_id", -1))
            step = msg.step if msg.step is not None else payload.get("step")

            if step is None:
                print(
                    f"[orchestrator] ⚠️ Inference result from GPU{gpu_id} missing step identifier"
                )
                return

            logits = payload.get("logits")
            if isinstance(logits, torch.Tensor):
                logits = logits.clone()

            result_entry = {
                "gpu_id": gpu_id,
                "step": int(step),
                "logits": logits,
                "token_count": payload.get("token_count"),
                "timestamp": payload.get("timestamp"),
            }

            with self._inference_results_lock:
                bucket = self._inference_results.setdefault(int(step), [])
                bucket.append(result_entry)

                waiter = self._inference_waiters.get(int(step))
                if waiter is not None:
                    event, expected = waiter
                    if len(bucket) >= expected:
                        event.set()

        except Exception as e:
            print(f"[orchestrator] ⚠️ Inference channel error from {addr}: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Training helpers
    # ------------------------------------------------------------------
    @track_errors(context="orchestrator.broadcast_ctrl", severity=ErrorSeverity.CRITICAL)
    def _broadcast_ctrl(self, msg: Message) -> None:
        """
        Send the same Message to EVERY registered worker via its control socket.
        If a socket is dead, drop that worker.
        """
        dead = []
        for gpu_id, sock in list(self.ctrl_sockets.items()):
            try:
                MessageProtocol.send_message(sock, msg, compress=True)
            except Exception as e:
                print(f"[orchestrator] failed to send cmd to GPU{gpu_id}: {e}")
                dead.append(gpu_id)

        for gpu_id in dead:
            self.ctrl_sockets.pop(gpu_id, None)
            self.registered_workers.pop(gpu_id, None)

    @track_errors(context="orchestrator.send_ctrl_to", severity=ErrorSeverity.CRITICAL)
    def _send_ctrl_to(self, gpu_id: int, msg: Message) -> None:
        """
        Send one Message to one specific worker (used for:
        - PHASE2 to last shard
        - CONTROL_PIPELINE_BACKWARD during upstream walk).
        """
        sock = self.ctrl_sockets.get(gpu_id)
        if sock is None:
            raise RuntimeError(f"No control socket for GPU{gpu_id}")
        try:
            MessageProtocol.send_message(sock, msg, compress=True)
        except Exception as e:
            raise RuntimeError(f"Failed to send ctrl msg to GPU{gpu_id}: {e}")

    def _wait_backward_ready(self, gpu_id: int, step: int) -> Any:
        """
        Block until worker `gpu_id` reports BACKWARD_READY for this `step`.
        Returns upstream_grad (None for shard0).
        """
        while True:
            with self._backward_lock:
                q = self._backward_ready_queues.get(gpu_id, [])
                for i, m in enumerate(q):
                    if m.step == step:
                        msg = q.pop(i)
                        upstream_grad = None
                        if isinstance(msg.payload, dict):
                            upstream_grad = msg.payload.get("upstream_grad", None)
                        return upstream_grad
            time.sleep(0.01)

    def _expected_grad_senders(self, pipeline_mode: bool) -> int:
        """
        How many workers should upload gradients for this global step?
        Both data-parallel and full pipeline backward expect all workers.
        """
        return max(self.cfg.num_workers, 1)

    @track_errors(context="orchestrator.aggregate_and_step", severity=ErrorSeverity.ERROR)
    def _aggregate_and_step(self, pipeline_mode: bool = False, timeout: float = 300.0, max_retries: int = 3) -> bool:
        """
        Gradient sync + optimizer step with timeout and retry logic for missing workers.

        Returns True on success, False if step should be aborted.
        """
        assert self.model is not None
        assert self.optimizer is not None

        expected_workers = self._expected_grad_senders(pipeline_mode)

        for retry_attempt in range(max_retries):
            start_time = time.time()
            timed_out = False

            while True:
                with self.gradients_lock:
                    ready = len(self.collected_gradients) >= expected_workers
                    current_count = len(self.collected_gradients)

                if ready:
                    break

                elapsed = time.time() - start_time
                if elapsed > timeout:
                    print(f"[orchestrator] ⚠️ TIMEOUT on retry {retry_attempt + 1}/{max_retries} after {elapsed:.1f}s")
                    print(f"[orchestrator] Expected {expected_workers} workers, got {current_count}")

                    with self.gradients_lock:
                        present = set(self.collected_gradients.keys())
                    expected_set = set(range(self.cfg.num_workers))
                    missing = expected_set - present
                    print(f"[orchestrator] Missing gradients from GPUs: {missing}")

                    # Probe liveness of missing workers
                    dead_workers = []
                    alive_workers = []
                    for gpu_id in missing:
                        sock = self.ctrl_sockets.get(gpu_id)
                        if sock is None:
                            dead_workers.append(gpu_id)
                            continue
                        try:
                            ping = Message(msg_type=MessageType.CONTROL_HEARTBEAT, gpu_id=gpu_id)
                            MessageProtocol.send_message(sock, ping, compress=False)
                            alive_workers.append(gpu_id)
                        except Exception as e:
                            print(f"[orchestrator] Failed to ping GPU{gpu_id}: {e}")
                            dead_workers.append(gpu_id)

                    if dead_workers:
                        print(f"[orchestrator] 💀 Dead workers detected: {dead_workers}")
                        if retry_attempt < max_retries - 1:
                            wait_time = min(15 * (retry_attempt + 1), 120)
                            print(f"[orchestrator] ⏳ Waiting {wait_time}s for workers to reconnect...")
                            time.sleep(wait_time)
                        else:
                            print(f"[orchestrator] 🔄 Clearing stale gradients and waiting for reconnection...")
                            with self.gradients_lock:
                                self.collected_gradients.clear()
                            wait_time = min(5 * (retry_attempt + 1), 30)
                            print(f"[orchestrator] ⏳ Waiting {wait_time}s for workers to reconnect...")
                            time.sleep(wait_time)
                            timed_out = True
                            break
                    else:
                        print(f"[orchestrator] Workers {alive_workers} are alive but slow, extending wait...")
                        time.sleep(2.0)
                        continue

                time.sleep(0.01)

            if timed_out:
                continue

            # SUCCESS: have all gradients
            break
        else:
            print(f"[orchestrator] ❌ Failed to collect gradients after {max_retries} retries")
            return False

        # Aggregate
        with self.gradients_lock:
            per_gpu_grads = self.collected_gradients
            self.collected_gradients = {}

        print(f"[orchestrator] ✅ Collected gradients from {len(per_gpu_grads)} workers")

        # Group grads by param name
        stacked: Dict[str, List[torch.Tensor]] = {}
        for gpu_id, grad_dict in per_gpu_grads.items():
            for pname, g in grad_dict.items():
                stacked.setdefault(pname, []).append(g)

        # Average
        avg_grads: Dict[str, torch.Tensor] = {}
        for pname, lst in stacked.items():
            try:
                avg_grads[pname] = torch.stack(lst).mean(dim=0)
            except Exception:
                # Fallback: sum / len to avoid shape mismatches crashing
                s = None
                for t in lst:
                    s = (t if s is None else s + t)
                avg_grads[pname] = s / max(len(lst), 1)

        # Load averaged grads and step
        self.optimizer.zero_grad(set_to_none=True)
        for (pname, param) in self.model.named_parameters():
            if pname in avg_grads:
                param.grad = avg_grads[pname].to(param.device).clone()

        self.optimizer.step()
        if self.scheduler is not None:
            try:
                self.scheduler.step()
            except TypeError:
                self.scheduler.step(self.global_step)

        return True

    def _drain_metrics(self) -> List[Dict[str, Any]]:
        """Return and clear buffered metrics from workers."""
        with self.metrics_lock:
            out = self.collected_metrics
            self.collected_metrics = []
        return out

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        """
        Graceful shutdown - release ports, close sockets, stop threads.
        """
        print(f"[orchestrator] 🛑 Starting graceful shutdown...")

        # Release ports
        if self._port_manager is not None:
            job_name = getattr(self.cfg, "job_name", "unknown")
            try:
                self._port_manager.release_port_range(job_name)
                print(f"[orchestrator] 🔓 Ports released for job '{job_name}'")
            except Exception as e:
                print(f"[orchestrator] ⚠️ Port release failed: {e}")

        # Signal threads
        self._shutdown_flag.set()

        # Close control sockets
        for gpu_id, sock in list(self.ctrl_sockets.items()):
            try:
                sock.close()
                print(f"[orchestrator] Closed control socket for GPU{gpu_id}")
            except Exception as e:
                print(f"[orchestrator] Error closing ctrl socket GPU{gpu_id}: {e}")

        # Close persistent gradient sockets
        with self.grad_sockets_lock:
            for gpu_id, sock in list(self.grad_sockets.items()):
                try:
                    sock.close()
                    print(f"[orchestrator] Closed gradient socket for GPU{gpu_id}")
                except Exception as e:
                    print(f"[orchestrator] Error closing grad socket GPU{gpu_id}: {e}")

        # Close persistent checkpoint sockets
        with self.chkpt_sockets_lock:
            for gpu_id, sock in list(self.chkpt_sockets.items()):
                try:
                    sock.close()
                    print(f"[orchestrator] Closed checkpoint socket for GPU{gpu_id}")
                except Exception as e:
                    print(f"[orchestrator] Error closing chkpt socket GPU{gpu_id}: {e}")

        # Join threads
        for t in self._listener_threads:
            if t.is_alive():
                t.join(timeout=5.0)

        print(f"[orchestrator] ✅ Graceful shutdown complete")
