from langchain.tools import tool
from typing import List
import paramiko
from scp import SCPClient
from concurrent.futures import ThreadPoolExecutor
import time

@tool
def send_files(ip_address: List[str], source_local: str, remote_dest: str, user: str, pwd: str):
    """Send a file to a remote computer or multiple computers """
    """can send ranges of ip addresses then take the range and send files to all of them"""
    """Send file to different location of same computer  """
    """Do not use previous results to run this tool again"""
    """Send a files to a multiple remote computers"""
    """This will send files faster by using multithreading"""
    """Manages the multithreading across all IPs."""
    result_list = []
    def single_file_transfer(ip_address, source_local, remote_dest, user, pwd):
        try:
            attempt = 0
            max_retries = 3
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect using ONLY the IP
            ssh.connect(ip_address, username=user, password=pwd)
            
            with SCPClient(ssh.get_transport()) as scp:
                # Send to the SPECIFIC Linux path
                scp.put(source_local, recursive=True, remote_path=remote_dest)
                
            ssh.close()

            return f"[bold green]Success: Sent to {ip_address}[/bold green]"
            
        except Exception as e:
            if attempt < max_retries:
                return f"[bold red]Timeout for {ip_address}[/bold red]" 
            

    with ThreadPoolExecutor(max_workers=5) as executor:
        # We use a lambda to pass all the extra arguments to the function
        result_list.extend(list(executor.map(
            lambda ip: single_file_transfer(ip, source_local, remote_dest, user, pwd), 
            ip_address
        )))
    
    return {
        "ui_type": "send_files",
        "result": result_list
    }

# Usage
# ips = ["192.168.159.171", "192.168.159.172", "192.168.159.173"] # List of your VMs
# local_folder = "C:/zTest_Source"
# linux_destination = "/home/kali/Downloads"
# username = "kali"
# password = "kali"
