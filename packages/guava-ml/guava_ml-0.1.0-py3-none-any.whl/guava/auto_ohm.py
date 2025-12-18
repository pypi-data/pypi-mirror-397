import os, subprocess, time, shutil, zipfile, tempfile, requests

OHM_DIR = r"C:\Program Files\OpenHardwareMonitor"
OHM_EXE = os.path.join(OHM_DIR, "OpenHardwareMonitor.exe")
OHM_ZIP_URL = "https://openhardwaremonitor.org/files/openhardwaremonitor-v0.9.6.zip"

def is_ohm_installed():
    return os.path.isfile(OHM_EXE)

def is_ohm_running():
    try:
        out = subprocess.check_output("tasklist", creationflags=subprocess.CREATE_NO_WINDOW)
        return b"OpenHardwareMonitor.exe" in out
    except Exception:
        return False

def install_ohm():
    print("[OHM] Installing OpenHardwareMonitor…")
    tmpdir = tempfile.mkdtemp()
    zip_path = os.path.join(tmpdir, "ohm.zip")
    
    r = requests.get(OHM_ZIP_URL)
    with open(zip_path, "wb") as f:
        f.write(r.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(tmpdir)

    os.makedirs(OHM_DIR, exist_ok=True)
    extracted = os.path.join(tmpdir, "OpenHardwareMonitor")
    for f in os.listdir(extracted):
        shutil.move(os.path.join(extracted, f), OHM_DIR)

    shutil.rmtree(tmpdir, ignore_errors=True)
    print("[OHM] Installed ✅")

def launch_ohm():
    # If already installed & running → do nothing
    if is_ohm_installed() and is_ohm_running():
        return

    # Install if missing
    if not is_ohm_installed():
        install_ohm()

    # Launch if not running
    if not is_ohm_running():
        print("[OHM] Launching background monitor…")
        subprocess.Popen([OHM_EXE], creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(2)
        print("[OHM] Live ✅")
