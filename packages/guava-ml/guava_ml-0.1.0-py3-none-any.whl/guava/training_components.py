"""Utilities for building training-time components from configuration."""

from __future__ import annotations

import copy
import importlib
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Union

import torch

ComponentSpecType = Union[str, Mapping[str, Any], Callable[..., Any]]


def _import_from_string(target: str) -> Any:
    """Import an object from a fully qualified ``target`` string."""
    module_name, _, attr_name = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Component target '{target}' is missing a module path")
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr_name)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Component target '{target}' does not define '{attr_name}'") from exc


@dataclass
class LossHandler:
    """Thin wrapper that standardises how we invoke user-provided loss callables."""

    loss: Callable[..., torch.Tensor]
    label_key: Optional[Union[str, Sequence[str]]] = "labels"
    logits_transform: str = "flatten_last_dim"
    labels_transform: str = "flatten"
    call_mode: str = "logits_labels"
    device: Optional[torch.device] = None

    def set_device(self, device: Union[str, torch.device, None]) -> "LossHandler":
        if device is None:
            self.device = None
            return self
        self.device = torch.device(device)
        if hasattr(self.loss, "to"):
            try:
                self.loss = self.loss.to(self.device)  # type: ignore[assignment]
            except Exception:  # pragma: no cover - some callables don't implement ``to``
                pass
        return self

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def __call__(self, predictions: torch.Tensor, batch: Optional[Mapping[str, Any]] = None,
                 *, device: Optional[torch.device] = None) -> Optional[torch.Tensor]:
        return self.compute(predictions, batch=batch, device=device)

    def compute(self, predictions: torch.Tensor, batch: Optional[Mapping[str, Any]] = None,
                *, device: Optional[torch.device] = None) -> Optional[torch.Tensor]:
        batch = batch or {}
        target_device = device or self.device
        if isinstance(predictions, torch.Tensor) and target_device is not None:
            predictions = predictions.to(target_device)

        if self.call_mode == "batch_only":
            return self.loss(batch)  # type: ignore[arg-type]

        labels = self._extract_labels(batch, target_device)
        if labels is None and self.call_mode == "logits_labels":
            return None

        if isinstance(predictions, torch.Tensor):
            preds_view = self._transform_logits(predictions)
        elif self.call_mode == "logits_labels":
            raise TypeError(
                "LossHandler expected tensor predictions for 'logits_labels' mode"
            )
        else:
            preds_view = predictions

        labels_view = self._transform_labels(labels, preds_view)

        if self.call_mode == "logits_labels":
            return self.loss(preds_view, labels_view)
        if self.call_mode == "predictions_batch":
            return self.loss(preds_view, batch)
        if self.call_mode == "labels_batch":
            return self.loss(labels_view, batch)
        raise ValueError(f"Unsupported call_mode '{self.call_mode}'")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _extract_labels(self, batch: Mapping[str, Any], target_device: Optional[torch.device]) -> Optional[Any]:
        if self.label_key is None:
            return None
        if isinstance(self.label_key, (tuple, list)):
            values = [batch.get(key) for key in self.label_key]
            if any(v is None for v in values):
                return None
            return tuple(self._tensorize(v, target_device) for v in values)
        raw = batch.get(self.label_key)
        if raw is None:
            return None
        return self._tensorize(raw, target_device)

    def _tensorize(self, value: Any, target_device: Optional[torch.device]) -> Any:
        if isinstance(value, torch.Tensor):
            if target_device is not None:
                return value.to(target_device, non_blocking=True)
            return value
        if isinstance(value, (tuple, list)):
            tensor = torch.as_tensor(value)
        else:
            tensor = torch.as_tensor(value)
        if target_device is not None:
            tensor = tensor.to(target_device)
        return tensor

    def _transform_logits(self, logits: torch.Tensor) -> torch.Tensor:
        if not isinstance(logits, torch.Tensor):
            raise TypeError("LossHandler expects model outputs to be torch.Tensor")
        if self.logits_transform in (None, "none"):
            return logits
        if self.logits_transform == "flatten_last_dim":
            if logits.ndim <= 1:
                return logits
            return logits.view(-1, logits.size(-1))
        if self.logits_transform == "flatten":
            return logits.view(-1)
        raise ValueError(f"Unsupported logits_transform '{self.logits_transform}'")

    def _transform_labels(self, labels: Optional[Any], logits: torch.Tensor) -> Optional[Any]:
        if labels is None:
            return None
        if self.labels_transform in (None, "none"):
            return labels
        if isinstance(labels, tuple):
            return tuple(self._transform_labels(item, logits) for item in labels)
        if not isinstance(labels, torch.Tensor):
            return labels
        if self.labels_transform == "flatten":
            return labels.view(-1)
        if self.labels_transform == "match_logits":
            if isinstance(logits, torch.Tensor):
                return labels.view_as(logits)
            raise TypeError("'match_logits' labels_transform requires tensor predictions")
        raise ValueError(f"Unsupported labels_transform '{self.labels_transform}'")


# ----------------------------------------------------------------------------
# Component instantiation helpers
# ----------------------------------------------------------------------------

def instantiate_component(spec: ComponentSpecType, *, positional_args: Sequence[Any] = (),
                          extra_kwargs: Optional[Mapping[str, Any]] = None,
                          allow_partial: bool = True) -> Any:
    """Instantiate a component described by ``spec``."""
    if spec is None:
        return None

    if callable(spec) and not isinstance(spec, Mapping):
        if positional_args or extra_kwargs:
            kwargs = dict(extra_kwargs or {})
            return spec(*positional_args, **kwargs)
        return spec

    if isinstance(spec, str):
        target = spec
        params: Dict[str, Any] = {}
    elif isinstance(spec, Mapping):
        target = spec.get("target")
        if not target:
            callable_obj = spec.get("callable")
            if callable_obj:
                return instantiate_component(callable_obj, positional_args=positional_args,
                                             extra_kwargs=extra_kwargs, allow_partial=allow_partial)
            raise ValueError("Component spec dictionary requires a 'target' or 'callable'")
        params = dict(spec.get("params", {}))
    else:
        raise TypeError(f"Unsupported component spec type: {type(spec)!r}")

    kwargs = dict(params)
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    target_obj = _import_from_string(target)

    if isinstance(target_obj, type):
        return target_obj(*positional_args, **kwargs)

    if positional_args or not allow_partial:
        return target_obj(*positional_args, **kwargs)

    if kwargs:
        return partial(target_obj, **kwargs)
    return target_obj


def build_loss_handler(config: Any, *, device: Optional[Union[str, torch.device]] = None) -> LossHandler:
    """Create a :class:`LossHandler` from ``config.loss`` description."""
    loss_cfg = copy.deepcopy(getattr(config, "loss", None)) or {}
    label_key = loss_cfg.pop("label_key", "labels")
    logits_transform = loss_cfg.pop("logits_transform", "flatten_last_dim")
    labels_transform = loss_cfg.pop("labels_transform", "flatten")
    call_mode = loss_cfg.pop("call_mode", "logits_labels")

    loss_callable = instantiate_component(loss_cfg or "torch.nn.CrossEntropyLoss")
    handler = LossHandler(
        loss=loss_callable,
        label_key=label_key,
        logits_transform=logits_transform,
        labels_transform=labels_transform,
        call_mode=call_mode,
    )
    return handler.set_device(device)


def build_optimizer(config: Any, parameters: Iterable[torch.nn.Parameter]) -> torch.optim.Optimizer:
    """Instantiate the optimiser described in the configuration."""
    opt_cfg = copy.deepcopy(getattr(config, "optimizer", None)) or {}
    default_kwargs: Dict[str, Any] = {}
    if getattr(config, "learning_rate", None) is not None:
        default_kwargs.setdefault("lr", config.learning_rate)
    if getattr(config, "weight_decay", None) is not None:
        default_kwargs.setdefault("weight_decay", config.weight_decay)

    if isinstance(opt_cfg, Mapping):
        params_cfg = dict(opt_cfg.get("params", {}))
        default_kwargs.update(params_cfg)

    optimizer = instantiate_component(
        opt_cfg or "torch.optim.AdamW",
        positional_args=(parameters,),
        extra_kwargs=default_kwargs,
        allow_partial=False,
    )
    if not isinstance(optimizer, torch.optim.Optimizer):  # pragma: no cover - safety
        raise TypeError(
            f"Configured optimizer must be a torch.optim.Optimizer instance, got {type(optimizer)!r}"
        )
    return optimizer


def build_scheduler(config: Any, optimizer: torch.optim.Optimizer) -> Optional[Any]:
    """Instantiate an optional LR scheduler if ``config.scheduler`` is provided."""
    sched_cfg = copy.deepcopy(getattr(config, "scheduler", None))
    if not sched_cfg:
        return None
    schedule = instantiate_component(
        sched_cfg,
        positional_args=(optimizer,),
        allow_partial=False,
    )
    return schedule