from langchain.tools import tool
from utils.execution_log import log_execution
import shutil
import threading
from rich.console import Console
import os, sys
from typing import Optional, Dict, Any, List

@tool
def firewall_status() -> Dict[str, Any]:
    """Show firewall status"""
    """Do not use previous results to run this tool again"""
    try:
        if sys.platform == "win32":
            command = "netsh advfirewall show allprofiles" 
        elif sys.platform in ("linux" , "darwin") : 
            command = "ufw status verbose"
        else: 
            return "Unsupported platform"
        
        result = os.system(command)
        return f"{result}"
    except Exception as e:
        print(f"Error finding firewall status: {e}")
        return {
            "success": False,
            "error": str(e),
            "ui_type": "firewall_status"
        }
        
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
def turn_on_firewall() -> str:

    """Turn on firewall for all profiles"""
    """Do not use previous results to run this tool again"""

    try:
        if sys.platform == "win32":
            # Turn firewall status ON 
            os.system("netsh advfirewall set allprofiles state on")

        elif sys.platform in ("linux", "darwin"):
            os.system("ufw enable")
        else:
            return "Unsupported platform"

        return (
            f"Firewall turned ON "
            
        )
    except Exception as e:
        return f"Error turning on firewall: {e}"


def block_internet_connection() -> str:
    """
    Turns on the firewall and blocks all inbound and outbound traffic.
    """
    try:
        if sys.platform == "win32":
            os.system("netsh advfirewall set allprofiles state on")
            os.system("netsh advfirewall set allprofiles firewallpolicy blockinboundalways,blockoutbound")
        elif sys.platform in ("linux", "darwin"):
            os.system("ufw enable")
            os.system("ufw default deny incoming")
            os.system("ufw default deny outgoing")
        else:
            return "Unsupported platform"
        return "Internet connection blocked successfully."
    except Exception as e:
        return f"Error blocking internet: {e}"


def restore_internet_connection() -> str:
    """
    Restores internet access by allowing outbound traffic and blocking inbound.
    """
    try:
        if sys.platform == "win32":
            os.system("netsh advfirewall set allprofiles state on")
            os.system("netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound")
        elif sys.platform in ("linux", "darwin"):
            os.system("ufw default allow outgoing")
            os.system("ufw default deny incoming")
        else:
            return "Unsupported platform"
        return "Internet connection restored to default settings."
    except Exception as e:
        return f"Error restoring internet: {e}"





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