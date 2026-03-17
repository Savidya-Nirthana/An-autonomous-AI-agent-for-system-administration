import subprocess, sys
from langchain.tools import tool
from typing import Any, List, Dict, Optional
from cli.checkOS import checkOS

# testing process...

@tool
def updatePackages(package : List = ['all']) -> Dict :
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
            'success':True,
            'result': str(response),
            'ui_type':'normal_window',

        }
    except Exception as e:
        return {
            'success':False,
            'error': str(e),
            'ui_type':'normal_window',

        }

#windows checked
@tool
def shutdown(time:int = 0) -> Dict :
    '''shutdown the device at given time in seconds'''
    os = checkOS()
    try:
        if os == 'windows':
            cmd = ['shutdown', '/s', '/t', str(time)]
        elif os == 'linux' or os == 'darwin':
            cmd = ['shutdown', '-h', str(time)]

        response = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'success':True,
            'result': str(response),
            'ui_type':'normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error':str(e),
            'ui_type':'normal_window'
        }

#windows checked
@tool
def restart(time:int = 0) -> Dict :
    '''restart the device at given time in seconds'''
    os = checkOS()
    try:
        if os == 'windows':
            cmd = ['shutdown', '/r', '/t', str(time)]
        elif os == 'linux' or os == 'darwin':
            cmd = ['shutdown', '-r', '+', str(time)]

        response = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'success':True,
            'result': str(response),
            'ui_type':'normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error':str(e),
            'ui_type':'normal_window'
        }



@tool
def get_last_time_sync_details() -> Dict:
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
                'success':False,
                'error':'OS not supported',
                'ui_type':'normal_window'
            }

        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "result" : str(result),
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
def sync_time() -> Dict:
    """ sync the time with correct time"""
    try:
        os = checkOS()

        if os == "windows":
            cmd = ["w32tm", "/resync"]
        elif os in ("linux", "darwin"):
            cmd = ["timedatectl", "set-ntp", "true"]
        else:
            return {
                'success':False,
                'error':'OS not supported',
                'ui_type':'normal_window'
            }

        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "result": str(result),
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
def viewUPTime() -> Dict:
    ''' Show how long the system has been running pretty printed'''
    os = checkOS()
    try:
        if os == 'linux' or os == 'darwin':
            cmd = ['uptime']

        elif os == 'windows':
            return {
                'success':True,
                'result':'This tool is only for linux and darwin',
                'ui_type':'normal_window'
            }
        else:
            return {
                'success':False,
                'error':'OS not supported',
                'ui_type':'normal_window'
            }

        response = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'success':True,
            'result': str(response),
            'ui_type':'normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error':str(e),
            'ui_type':'normal_window'
        }
