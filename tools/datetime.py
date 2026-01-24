from langchain.tools import tool
from utils.execution_log import log_execution
import platform
import stat
from typing import Optional, Dict, Any, List
import sys, subprocess


@tool
def get_last_time_sync_details() -> str: 
    """ get the last time sync details """
    try:
        os = platform.system().lower()

        if os == "windows":
            cmd = ["w32tm", "/query", "/status"]
        elif os in ("linux", "darwin"):
            cmd = ["timedatectl", "status"]
        else:
            raise ValueError(f"Unsupported OS: {os}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "result" : result,
            "success": True,
            "ui_type": "last_sync_time"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "last_sync_time"
        }

@tool
def sync_time() -> str: 
    """ sync the time with correct time"""
    try:
        os = platform.system().lower()

        if os == "windows":
            cmd = ["w32tm", "/resync"]
        elif os in ("linux", "darwin"):
            cmd = ["timedatectl", "set-ntp", "true"]
        else:
            raise ValueError(f"Unsupported OS: {os}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "result": result,
            "success": True,
            "ui_type": "normal_window"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "normal_window"
        }