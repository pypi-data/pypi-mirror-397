import platform

try:
    from OHM import Computer
except Exception:
    Computer = None

def read_cpu_temp_windows():
    if platform.system() != "Windows" or Computer is None:
        return None

    try:
        pc = Computer()
        pc.CPUEnabled = True
        pc.Open()

        temp_vals = []
        for hw in pc.Hardware:
            if hw.HardwareType == "CPU":
                hw.Update()
                for s in hw.Sensors:
                    if s.SensorType == "Temperature":
                        temp_vals.append(s.Value)

        return sum(temp_vals)/len(temp_vals) if temp_vals else None
    except:
        return None
