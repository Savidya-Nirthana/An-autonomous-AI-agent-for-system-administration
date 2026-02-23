from langchain.tools import tool
from utils.execution_log import log_execution
import sys
import os

@tool
def firewall_status() -> str:
    """Show firewall status"""
    try:
        if sys.platform == "win32":
            command = "netsh advfirewall show allprofiles" 
        elif sys.platform in ("linux" , "darwin") : 
            command = "ufw status verbose"
            
        return f"{os.system(command)}"
    except Exception as e:
        print(f"Error finding firewall status: {e}")
        