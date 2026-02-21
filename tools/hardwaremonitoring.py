from langchain.tools import tool
import subprocess
from cli.checkOS import checkOS


#only for linux
@tool
def viewCPUfantemp() -> str:
    '''show the current CPU fan temperature'''
    os = checkOS()
    try:
        if 'linux' | 'darvin':
            cmd = ['sensors'] 
    
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

@tool
def viewDriveHealth() -> str:
    ''' Show S.M.A.R.T health data for a drive '''
    os = checkOS()
    try:
        if 'linux' | 'darvin':
            cmd = ['smartctl', '-a', '/dev/sda'] 
    
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

@tool
def viewHardwareSummary() -> str:
    ''' view hardware details as a summary'''
    os = checkOS()
    try:
        if 'linux' | 'darvin':
            cmd = 'apt-get install lshw -y' #hope this works
            subprocess.run(cmd)

            cmd = ['lshw', '-short'] #lshw is need to install prior use 
    
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

@tool
def viewUSBDevices() -> str:
    '''List USB devices in a tree hierarchy '''

    os = checkOS()
    try:
        if 'linux' | 'darvin':
            cmd = ['lsusb','-t'] 
    
        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window'
        } #better view this as a table
    except exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

@tool
def viewPCIInfomation() -> str:
    ''' List PCI devices with verbose machine-readable info'''
    os = checkOS()
    try:
        if 'linux' | 'darvin':
            cmd = ['lspci', '-vmm'] 
    
        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window'
        } #better view this as a table
    except exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }