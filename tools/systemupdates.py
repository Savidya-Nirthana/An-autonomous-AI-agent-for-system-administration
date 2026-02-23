import subprocess, sys
from langchain.tools import tool
from typing import Any, List, Dict, Optional
from cli.checkOS import checkOS

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