from langchain.tools import tool
import platform
import subprocess
from typing import Dict, Any

@tool
def ipconfig_release() -> Dict[str, Any]:
    """
    Release the current IP address for all adapters (Windows only).
    Useful when network connectivity is stuck or needs a reset.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "network_fix"
        }

    try:
        # Running ipconfig /release
        process = subprocess.run(["ipconfig", "/release"], capture_output=True, text=True, errors="replace", timeout=30)
        return {
            "success": process.returncode == 0,
            "data": process.stdout,
            "output": "IP address release command executed. Use 'renew' to get a new IP.",
            "ui_type": "network_fix",
            "operation": "Release IP"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "network_fix",
            "operation": "Release IP"
        }

@tool
def ipconfig_renew() -> Dict[str, Any]:
    """
    Renew the IP address for all adapters (Windows only).
    Useful after releasing an IP or when DHCP fails to provide an address.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "network_fix"
        }

    try:
        # Running ipconfig /renew
        process = subprocess.run(["ipconfig", "/renew"], capture_output=True, text=True, errors="replace", timeout=60)
        return {
            "success": process.returncode == 0,
            "data": process.stdout,
            "output": "IP address renew command executed. Network configuration has been refreshed.",
            "ui_type": "network_fix",
            "operation": "Renew IP"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "network_fix",
            "operation": "Renew IP"
        }

@tool
def ipconfig_flush_dns() -> Dict[str, Any]:
    """
    Flush and reset the contents of the DNS client resolver cache (Windows only).
    Useful for resolving DNS-related connectivity issues.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "network_fix"
        }

    try:
        # Running ipconfig /flushdns
        process = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, errors="replace", timeout=30)
        return {
            "success": process.returncode == 0,
            "data": process.stdout,
            "output": "DNS resolver cache successfully flushed.",
            "ui_type": "network_fix",
            "operation": "Flush DNS"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "network_fix",
            "operation": "Flush DNS"
        }

@tool
def winsock_reset() -> Dict[str, Any]:
    """
    Reset the Winsock catalog to a clean state (Windows only, Admin usually required).
    Useful for repairing network corrupted by software or malware.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "network_fix"
        }

    try:
        # Running netsh winsock reset
        process = subprocess.run(["netsh", "winsock", "reset"], capture_output=True, text=True, errors="replace", timeout=30)
        return {
            "success": process.returncode == 0,
            "data": process.stdout,
            "output": "Winsock catalog successfully reset. A restart may be required for full effect.",
            "ui_type": "network_fix",
            "operation": "Winsock Reset"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "network_fix",
            "operation": "Winsock Reset"
        }

@tool
def tcp_ip_reset() -> Dict[str, Any]:
    """
    Reset the TCP/IP stack to its default configuration (Windows only, Admin required).
    Useful for fixing deep-seated IP protocol corruption.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "network_fix"
        }

    try:
        # Running netsh int ip reset
        process = subprocess.run(["netsh", "int", "ip", "reset"], capture_output=True, text=True, errors="replace", timeout=30)
        return {
            "success": process.returncode == 0,
            "data": process.stdout,
            "output": "TCP/IP stack successfully reset. A restart is highly recommended.",
            "ui_type": "network_fix",
            "operation": "TCP/IP Reset"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "network_fix",
            "operation": "TCP/IP Reset"
        }
