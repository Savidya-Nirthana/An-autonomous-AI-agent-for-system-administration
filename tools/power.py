from langchain.tools import tool
import subprocess
from cli.checkOS import checkOS

def shutdown(time:int = 0) -> str :
    '''shutdown the device at given time in seconds'''
    os = checkOS()
    try:
        if os == 'windows':
            cmd = ['shutdown', '/r', '/t', time]
        elif os == 'linux' | 'darvin':
            cmd = ['shutdown', '-h', 'now'] #command need to be added for time 
    
        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window'
        }
    except exception as e:
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
        elif os == 'linux' | 'darvin':
            cmd = ['reboot'] #command need to be added
    
        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window'
        }
    except exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

