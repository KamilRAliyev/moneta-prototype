import platform
import os
import time
import psutil


def get_health_info():
    return {
        "status": "ok",
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "hostname": platform.node(),
        "process_id": os.getpid(),
        "uptime_seconds": (
            time.time() - psutil.boot_time() if "psutil" in globals() else None
        ),
        "app_version": "0.1.0",
    }
