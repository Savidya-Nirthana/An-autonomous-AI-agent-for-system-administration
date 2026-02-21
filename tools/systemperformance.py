from langchain import tool
import subpricess
from cli.checkOS import checkOS


#if it has fro windows add it
@tool
def viewCPUUtilization(times:int = 3, everySeconds:int = 1) -> str:
    ''' Report CPU utilization 3 times every 1 second'''
    os = checkOS()
    try:
        if 'linux' | 'darvin':
            cmd = ['sar', '-u', everySeconds, times] 
    
        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window' 
        }#table is prefer
    except exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }