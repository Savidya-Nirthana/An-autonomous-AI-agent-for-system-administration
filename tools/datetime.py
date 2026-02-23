from langchain.tools import tool
from utils.execution_log import log_execution
# import stat
from typing import Optional, Dict, Any, List
import sys, subprocess
from cli.request_admin_access import run_as_admin
from cli.checkOS import checkOS


@tool
def get_last_time_sync_details() -> str: 
    """ get the last time sync details """
    """ if time is not sync recently or correctly this can cause unable to access some web sites like google, facebook and etc.."""
    try:
        os = checkOS()

        if os == "windows":
            cmd = ["w32tm", "/query", "/status"]
        elif os in ("linux", "darwin"):
            cmd = ["timedatectl", "status"]
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }

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
        os = checkOS()

        if os == "windows":
            cmd = ["w32tm", "/resync"]
        elif os in ("linux", "darwin"):
            cmd = ["timedatectl", "set-ntp", "true"]
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }

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

@tool
def viewUPTime() -> str:
    ''' Show how long the system has been running pretty printed'''
    os = checkOS()
    try:
        if os == 'linux' or os == 'darwin':
            cmd = ['uptime'] 
    
        elif os == 'windows':
            return {
                'sucess':True,
                'result':'This tool is only for linux and darwin',
                'ui_type':'normal_window'
            }
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }

        response = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window'
        }
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }