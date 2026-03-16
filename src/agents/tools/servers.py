import subprocess, sys
from langchain.tools import tool
from typing import Any, List, Dict, Optional
from cli.checkOS import checkOS
from utils.execution_log import log_execution
from cli.request_admin_access import run_as_admin



@tool
def webserver(path: str = "./", port: int = 8080) -> Dict :
    '''
        create a web server 
        if the requested path is empty or dosen't exist, 
        create that path and add a simple index.html 
        that has "hello" text inside it and 
        (
            <!doctype html>
            <html><body><h1>Hello from server </h1></body></html>
        ) 
        create the server 
    '''

    try:
        # if checkOS() == 'windows':
        #     #go to that path and is there any .html file exists if not create index.html and add text hello to it
        #     cmd = ['python3', '-m', 'http.server', port]
        # elif checkOS() == 'linux':
        #     #go to that path and is there any .html file exists if not create index.html and add text hello to it
        #     cmd = []
        # else:
        #     return {
        #         'sucess':False,
        #         'error': 'OS not support',
        #         'ui_type':'Normal_window'
        #     }      
        cmd = ['python3', '-m', 'http.server', port]
        response = subprocess.run(cmd , capture_output=True, text=True)

        return {
            'sucess':True,
            'error': response.stdout,
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'sucess':False,
            'error': str(e),
            'ui_type':'Normal_window'

        }