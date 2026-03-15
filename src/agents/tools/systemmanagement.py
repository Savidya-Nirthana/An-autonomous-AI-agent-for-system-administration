import subprocess, sys
from langchain.tools import tool
from typing import Any, List, Dict, Optional
from cli.checkOS import checkOS
from utils.execution_log import log_execution
from cli.request_admin_access import run_as_admin


# testing process...

@tool
def updatePackages(package : List = ['all']) -> str :
    '''
    take package list if user given as a parameters and update those packages,
    if user dose not give any package list or a name,
    then take it as all and update all packages.
    '''
    
    try:
        os = checkOS()

        if os == 'windows':
            cmd = ['winget', 'upgrade'] + package
        elif os == 'linux' or os == 'darwin':
            cmd = ['apt', 'update', '&&', 'apt', 'upgrade', '-y']
        
        response = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            'sucess':False,
            'result': str(response),
            'ui_type':'normal_window',
    
        }
    except Exception as e:
        return {
            'sucess':False,
            'error': str(e),
            'ui_type':'normal_window',
        
        }


def shutdown(time:int = 0) -> str :
    '''shutdown the device at given time in seconds'''
    os = checkOS()
    try:
        if os == 'windows':
            cmd = ['shutdown', '/r', '/t', time]
        elif os == 'linux' or os == 'darwin':
            cmd = ['shutdown', '-h', 'now'] #command need to be added for time 
    
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

def restart(time:int = 0) -> str :
    '''shutdown the device at given time in seconds'''
    os = checkOS()
    try:
        if os == 'windows':
            cmd = ['shutdown', '/s', '/t', time]
        elif os == 'linux' or os == 'darwin':
            cmd = ['reboot'] #command need to be added
    
        response = subprocess.run(cmd, capture_output=True, text=true)
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