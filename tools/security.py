from langchain.tools import tool   
import os , sys, subprocess

@tool
def full_route(ip_address: str) -> str:
    """
    Get the details from pathping command. ( routing details )
    Args:
        ip_address (str): IP address or hostname
    """
    try:
        result =  subprocess.check_output(['pathping', ip_address]).decode('utf-8')
        return {
            "success": True,
            "result": result,
            "ui_type": "normal_window"
        }
    except Exception as e:
        return {
            "success": False,
            "result": str(e),
            "ui_type": "normal_window"
        }