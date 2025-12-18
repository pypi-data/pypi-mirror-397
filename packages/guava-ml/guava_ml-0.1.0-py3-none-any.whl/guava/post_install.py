import platform, sys

def run():
    # Only run on Windows
    if platform.system() != "Windows":
        return

    try:
        import wmi  # OHM interface
        return
    except:
        pass

    print("🔧 Guava: Installing OpenHardwareMonitor (Windows CPU telemetry)...")

    import os, subprocess, urllib.request, zipfile, tempfile

    url = "https://openhardwaremonitor.org/files/openhardwaremonitor-v0.9.6.zip"
    tmp = tempfile.mkdtemp()
    zip_path = os.path.join(tmp, "ohm.zip")

    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("C:/OpenHardwareMonitor")

    exe = r"C:/OpenHardwareMonitor/OpenHardwareMonitor.exe"
    subprocess.Popen([exe])

    print("✅ OHM installed and running")
