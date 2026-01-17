from langchain.tools import tool
from utils.execution_log import log_execution
import shutil
import threading
from rich.console import Console
import os, sys

@tool
def firewall_status() -> str:
    """Show firewall status"""
    """Do not use previous results to run this tool again"""
    try:
        if sys.platform == "win32":
            command = "netsh advfirewall show allprofiles" 
        elif sys.platform in ("linux" , "darwin") : 
            command = "ufw status verbose"
        else: 
            return "Unsupported platform"
           
        return f"{os.system(command)}"
    except Exception as e:
        print(f"Error finding firewall status: {e}")
        return ""
        
@tool
def view_saved_credintials_by_os() ->str:
    """listing saved credentials managed by the OS """
    """Do not use previous results to run this tool again"""
    try:
        console = Console()
        if sys.platform == "win32" :
            command = "cmdkey /list"
        elif sys.platform in ("linux","darwin"):
            if shutil.which("secret-tool"):
                console.print(f"[bold yellow]installing essential tools...[/bold yellow]")
                if sys.platform == "linux" : os.system("sudo apt-get update && sudo apt-get install -y libsecret-tools")
                if sys.platform == "darwin" : os.system("brew install -y libsecret-tools")
                
            command = "secret-tool search --all"  
        else: 
            return "Unsupported platform"   
        
        return f"{os.system(command)}"
    except Exception as e:
        console.print(f"Error on stored username and credentials: {e}")
        return ""


@tool
def turn_off_firewall() -> str:
    """Turn off firewall for all profiles"""
    try:
        if sys.platform == "win32":
            command = "netsh advfirewall set allprofiles state off"
        elif sys.platform in ("linux", "darwin"):
            command = "ufw disable"
        else:
            return "Unsupported platform"
        os.system(command)
        return "Firewall turned OFF"
    except Exception as e:
        return f"Error turning off firewall: {e}"


@tool
def turn_on_firewall(
    inbound: str = "blockinbound",
    outbound: str = "allowoutbound",
    remotemanagement: str = "disable",
    log_dropped: str = "disable",
    log_allowed: str = "disable",
) -> str:
    """
    Turn on firewall for all profiles with optional parameters:
    - inbound: blockinbound | blockinboundalways | allowinbound | notconfigured
    - outbound: allowoutbound | blockoutbound | notconfigured
    - remotemanagement: enable | disable | notconfigured
    - log_dropped: enable | disable | notconfigured
    - log_allowed: enable | disable | notconfigured
    """
    """Do not use previous results to run this tool again"""
    """Blocking the internet connection = blocking inbound and outbound connections"""
    """when blocking the internet , inbound outbound connections, give the code that restore it too"""

    try:
        if sys.platform == "win32":
            # Turn firewall status ON 
            os.system("netsh advfirewall set allprofiles state on")

            # Apply firewall policy
            os.system(f"netsh advfirewall set allprofiles firewallpolicy {inbound},{outbound}")

            # Apply settings
            os.system(f"netsh advfirewall set allprofiles settings remotemanagement {remotemanagement}")

            # Apply logging
            os.system(f"netsh advfirewall set allprofiles logging droppedconnections {log_dropped}")
            os.system(f"netsh advfirewall set allprofiles logging allowedconnections {log_allowed}")

        elif sys.platform in ("linux", "darwin"):
            os.system("ufw enable")
        else:
            return "Unsupported platform"

        return (
            f"Firewall turned ON with policy inbound={inbound}, outbound={outbound}, "
            f"remotemanagement={remotemanagement}, log_dropped={log_dropped}, log_allowed={log_allowed}"
        )
    except Exception as e:
        return f"Error turning on firewall: {e}"

@tool 
def delay(duration:int = 10) -> str:
    """Delay for a specified duration in seconds if time send as minutes or hours convert it to seconds"""
    """Do not use previous results to run this tool again"""

    try:
        def done(): 
            print(f"Finished waiting {duration} seconds") 
        
        threading.Timer(duration, done).start()        
        return f"Delayed for {duration} seconds"

    except Exception as e:
        return f"Error in delaying: {e}"