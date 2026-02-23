from langchain.tools import tool
import subprocess
from cli.checkOS import checkOS


#if it has fro windows add it
@tool
def viewCPUUtilization(times:int = 3, everySeconds:int = 1) -> str:
    ''' Report CPU utilization 3 times every 1 second'''
    os = checkOS()
    try:
        if os == 'linux' or os == 'darwin':
            cmd = ['sar', '-u', everySeconds, times] 
    
        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window' 
        }#table is prefer
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }