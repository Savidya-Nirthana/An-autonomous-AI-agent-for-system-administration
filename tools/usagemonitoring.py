import psutil
from langchain.tools import tool
from typing import Dict, Any
import platform

@tool
def cpu_usage(detail: str = "basic") -> Dict[str, Any]:
    """
    Get CPU usage statistics.

    detail:
    - basic   → overall CPU usage
    - full/advanced    → per-core, frequency, load average (if available)

    please don't show the previous usages always run the full command to get the latest usages
    """

    system = platform.system().lower()

    try:
        result = {
            "success": True,
            "os": system,
            "ui_type": "cpu_usage",
            "detail": detail,
        }

        result["cpu_percent"] = psutil.cpu_percent(interval=1)

        if detail == "full":
            result["per_core"] = psutil.cpu_percent(interval=1, percpu=True)

            freq = psutil.cpu_freq()
            if freq:
                result["frequency_mhz"] = {
                    "current": freq.current,
                    "min": freq.min,
                    "max": freq.max,
                }

            if hasattr(psutil, "getloadavg"):
                try:
                    load1, load5, load15 = psutil.getloadavg()
                    result["load_average"] = {
                        "1m": load1,
                        "5m": load5,
                        "15m": load15,
                    }
                except OSError:
                    result["load_average"] = "Not supported"

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "cpu_usage"
        }

@tool
def memory_usage():
    """
    Returns the memory usage percentage.
    """

    system = platform.system().lower()

    try:
        memory_present = psutil.virtual_memory().percent
        return {
            "success": True,
            "memory_present": memory_present,
            "ui_type" : "memory_usage"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "memory_usage"
        }


@tool
def disk_usage():
    """
    Returns the disk usage percentage.
    """
    disk_present = psutil.disk_usage('/').percent
    return {
        "success": True,
        "disk_present": disk_present,
        "ui_type" : "disk_usage"
    }