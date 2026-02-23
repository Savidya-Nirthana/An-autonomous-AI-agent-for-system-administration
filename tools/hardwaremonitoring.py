from langchain.tools import tool
import subprocess
from cli.checkOS import checkOS

def checkWMIC() -> bool:
    iswmic = subprocess.run(['where wmic >nul 2>nul'], capture_output=True, shell=True)
            
    if iswmic.returncode != 0:
        print('wmic installing')
        subprocess.run('DISM /Online /Add-Capability /CapabilityName:WMIC~~~~', shell=True) #admin access is needed
        print('wmic installed')
        return True
    return False

#text this on linux
@tool
def viewCPUfantemp() -> str:
    '''show the current CPU fan temperature of my device'''
    os = checkOS()
    try:
        if os == 'linux' or os == 'darwin':
            cmd = ['sensors'] 
    
        elif os == 'windows':
            checkWMIC()
            cmd = ['wmic', 'cpu', 'get', 'name,numberofcores,maxclockspeed'] 
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }
            
        response = subprocess.ren(cmd, capture_output=True, text=true)
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
def viewDriveHealth() -> str:
    ''' Show S.M.A.R.T health data for a drive '''
    os = checkOS()
    try:
        if 'linux' or 'darwin':
            cmd = ['sudo', 'smartctl', '-a', '/dev/sda'] 
        elif os == 'windows':
            checkWMIC()
            cmd = ['wmic', 'diskdrive', 'get', 'model,status'] #testing
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }
        
        response = subprocess.ren(cmd, capture_output=True, text=true)
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
def viewHardwareSummary() -> str:
    ''' view hardware details as a summary'''
    os = checkOS()
    try:
        if os == 'linux' or os == 'darwin':
            cmd = 'apt-get install lshw -y' #hope this works
            subprocess.run(cmd)
            cmd = ['lshw', '-short'] #lshw is need to install prior use 
        elif os == 'windows':
            checkWMIC()
            cmd = ['wmic', 'path', 'win32_pnpentity', 'get', 'caption']
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }

        response = subprocess.ren(cmd, capture_output=True, text=true)
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
def viewUSBDevices() -> str:
    '''List USB devices in a tree hierarchy '''

    os = checkOS()
    try:
        if os == 'linux' or os == 'darwin':
            cmd = ['lsusb','-t'] 
        elif os == 'windows':
            checkWMIC()
            cmd = ['wmic', 'path', 'win32_usbcontrollerdevice', 'get', 'caption']
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }
        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window'
        } #better view this as a table
    except Exception as e:
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
        if os == 'linux' or os == 'darwin':
            cmd = ['lspci', '-vmm'] 
    
        elif os == 'windows':
            checkWMIC()
            cmd = [] #need to find the command for this
        else:
            return {
                'sucess':False,
                'error':'OS not supported',
                'ui_type':'Normal_window'
            }

        response = subprocess.ren(cmd, capture_output=True, text=true)
        return {
            'sucess':True,
            'result':response,
            'ui_type':'normal_window'
        } #better view this as a table
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }