"""System info utilities using psutil and nvidia-smi."""
from typing import Dict, Any, List
import psutil


def cpu_percent() -> float:
    return psutil.cpu_percent(interval=0.5)


def ram_info() -> Dict[str, Any]:
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "total_gb": round(mem.total / (1024 ** 3), 2),
    }


def gpu_info() -> List[Dict[str, Any]]:
    """Query GPU info via nvidia-smi or pynvml. Returns empty list if unavailable."""
    # Try nvidia-smi with dmi (comma-separated) format for reliability
    try:
        import subprocess
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
            parsed = []
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 5:
                    parsed.append({
                        "name": parts[0],
                        "utilization": float(parts[1]) if parts[1] else 0.0,
                        "memory_used_mb": float(parts[2]) if parts[2] else 0.0,
                        "memory_total_mb": float(parts[3]) if parts[3] else 0.0,
                        "temperature_c": float(parts[4]) if parts[4] else 0.0,
                        "power_draw": float(parts[5]) if len(parts) > 5 and parts[5] else 0.0,
                    })
            return parsed
    except Exception:
        pass

    # Fallback to pynvml
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        results = []
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            except Exception:
                power = 0.0
            name_str = name.decode() if isinstance(name, bytes) else str(name)
            results.append({
                "name": name_str,
                "utilization": float(util.gpu),
                "memory_used_mb": round(mem_info.used / (1024 ** 2), 1),
                "memory_total_mb": round(mem_info.total / (1024 ** 2), 1),
                "temperature_c": float(temp),
                "power_draw": round(power, 1),
            })
        pynvml.nvmlShutdown()
        return results
    except Exception:
        return []

    return []


def system_snapshot() -> Dict[str, Any]:
    ram = ram_info()
    return {
        "cpu_percent": cpu_percent(),
        "ram_percent": ram["percent"],
        "ram_used_gb": ram["used_gb"],
        "ram_total_gb": ram["total_gb"],
        "gpu": gpu_info(),
    }