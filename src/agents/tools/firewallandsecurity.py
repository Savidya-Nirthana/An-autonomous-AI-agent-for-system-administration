from langchain.tools import tool
import sys
import os
import subprocess
import shutil
import threading
from rich.console import Console

# testing process...

@tool
def firewall_status() -> dict:
    """Show firewall status"""
    try:
        if sys.platform == "win32":
            command = "netsh advfirewall show allprofiles"
        elif sys.platform in ("linux" , "darwin") :
            command = "ufw status verbose"

        result = subprocess.getoutput(command)

        return {
            'result':result,
            'success':True,
            'error':None,
            'ui_type':'Normal_window'
        }
    except Exception as e:
       return {
            'success':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }


@tool
def view_saved_credintials_by_os() ->dict:
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
            return {
                "result":"Unsupported platform",
                "success": False,
                "error": None,
                "ui_type": "normal_window"
            }

        result = subprocess.getoutput(command)

        result = result.strip().replace(" ","").splitlines()

        return {
            "result":result,
            "success": True,
            "error": None,
            "ui_type": "view_saved_credintials_by_os"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "view_saved_credintials_by_os"
            }

@tool
def turn_off_firewall() -> dict:
    """Turn off firewall for all profiles"""
    try:
        if sys.platform == "win32":
            command = "netsh advfirewall set allprofiles state off"
        elif sys.platform in ("linux", "darwin"):
            command = "ufw disable"
        else:
            return {
                "result":"Unsupported platform",
                "success": False,
                "error": None,
                "ui_type": "normal_window"
            }

        result = subprocess.getoutput(command)

        return {
            "result":result,
            "success": True,
            "error": None,
            "ui_type": "normal_window"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "normal_window"
        }

@tool
def turn_on_firewall() -> dict:

    """Turn on firewall for all profiles"""
    """Do not use previous results to run this tool again"""

    try:
        if sys.platform == "win32":
            # Turn firewall status ON
            command = "netsh advfirewall set allprofiles state on"

        elif sys.platform in ("linux", "darwin"):
            command = "ufw enable"
        else:
            return {
                "result":"Unsupported platform",
                "success": False,
                "error": None,
                "ui_type": "normal_window"
            }

        result = subprocess.getoutput(command)

        return {
            "result":result,
            "success": True,
            "error": None,
            "ui_type": "normal_window"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "normal_window"
        }

@tool
def block_internet_connection() -> dict:
    """
    Turns on the firewall and blocks all inbound and outbound traffic.
    """
    try:
        if sys.platform == "win32":
            subprocess.run("netsh advfirewall set allprofiles state on")
            subprocess.run("netsh advfirewall set allprofiles firewallpolicy blockinboundalways,blockoutbound")
        elif sys.platform in ("linux", "darwin"):
            subprocess.run("ufw enable")
            subprocess.run("ufw default deny incoming")
            subprocess.run("ufw default deny outgoing")
        else:
            return {
                "result":"Unsupported platform",
                "success": False,
                "error": None,
                "ui_type": "normal_window"
            }
        return {
            "result":"Internet connection blocked successfully.",
            "success": True,
            "error": None,
            "ui_type": "normal_window"
        }
    except Exception as e:
        return {
            "result":"Error blocking internet connection.",
            "success": False,
            "error": str(e),
            "ui_type": "normal_window"
        }

@tool
def restore_internet_connection() -> dict:
    """
    Restores internet access by allowing outbound traffic and blocking inbound.
    """
    try:
        if sys.platform == "win32":
            subprocess.run("netsh advfirewall set allprofiles state on")
            subprocess.run("netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound")
        elif sys.platform in ("linux", "darwin"):
            subprocess.run("ufw default allow outgoing")
            subprocess.run("ufw default deny incoming")
        else:
            return {
                "result":"Unsupported platform",
                "success": False,
                "error": None,
                "ui_type": "normal_window"
            }
        return {
            "result":"Internet connection restored to default settings.",
            "success": True,
            "error": None,
            "ui_type": "normal_window"
        }
    except Exception as e:
        return {
            "result":"Error restoring internet connection.",
            "success": False,
            "error": str(e),
            "ui_type": "normal_window"
        }



@tool
def delay(duration:int = 10) -> dict:
    """Delay for a specified duration in seconds if time send as minutes or hours convert it to seconds"""
    """Do not use previous results to run this tool again"""

    try:
        def done():
            print(f"Finished waiting {duration} seconds")

        threading.Timer(duration, done).start()
        return {
            "result":f"Delayed for {duration} seconds",
            "success": True,
            "error": None,
            "ui_type": "normal_window"
        }

    except Exception as e:
        return {
            "result":f"Error in delaying: {e}",
            "success": False,
            "error": str(e),
            "ui_type": "normal_window"
        }