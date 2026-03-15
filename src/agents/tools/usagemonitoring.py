import psutil
from langchain.tools import tool
from typing import Dict, Any
import platform
import subprocess
from cli.checkOS import checkOS


@tool
def cpu_usage(detail: str = "basic") -> Dict[str, Any]:
    """
    Get CPU usage statistics.

    detail:
    - basic   → overall CPU usage
    - full/advanced    → per-core, frequency, load average (if available)

    please don't show the previous usages always run the full command to get the latest usages
    """

    system = platform.system().lower()

    try:
        result = {
            "success": True,
            "os": system,
            "ui_type": "cpu_usage",
            "detail": detail,
        }

        result["cpu_percent"] = psutil.cpu_percent(interval=1)

        if detail == "full":
            result["per_core"] = psutil.cpu_percent(interval=1, percpu=True)

            freq = psutil.cpu_freq()
            if freq:
                result["frequency_mhz"] = {
                    "current": freq.current,
                    "min": freq.min,
                    "max": freq.max,
                }

            if hasattr(psutil, "getloadavg"):
                try:
                    load1, load5, load15 = psutil.getloadavg()
                    result["load_average"] = {
                        "1m": load1,
                        "5m": load5,
                        "15m": load15,
                    }
                except OSError:
                    result["load_average"] = "Not supported"

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "cpu_usage"
        }

@tool
def memory_usage():
    """
    Returns the memory usage percentage.
    """

    system = platform.system().lower()

    try:
        memory_present = psutil.virtual_memory().percent
        return {
            "success": True,
            "memory_present": memory_present,
            "ui_type" : "memory_usage"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "memory_usage"
        }


@tool
def disk_usage():
    """
    Returns the disk usage percentage.
    """
    disk_present = psutil.disk_usage('/').percent
    return {
        "success": True,
        "disk_present": disk_present,
        "ui_type" : "disk_usage"
    }


# ------------------------
# testing process...



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


@tool
def viewCPUUtilization(times:int = 3, everySeconds:int = 1) -> str:
    ''' Report CPU utilization 3 times every 1 second'''
    os = checkOS()
    try:
        if os == 'linux' or os == 'darwin':
            cmd = ['sar', '-u', everySeconds, times] 
    
        response = subprocess.run(cmd, capture_output=True, text=True)
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
