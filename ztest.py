# import os
# import paramiko
# from scp import SCPClient
# from concurrent.futures import ThreadPoolExecutor

# def send_files_scp(ip, source_local, remote_dest, user, pwd):
#     try:
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
#         # Connect using ONLY the IP
#         ssh.connect(ip, username=user, password=pwd)
        
#         with SCPClient(ssh.get_transport()) as scp:
#             # Send to the SPECIFIC Linux path
#             scp.put(source_local, recursive=True, remote_path=remote_dest)
            
#         ssh.close()
#         return f"Success: Sent to {ip}"
#     except Exception as e:
#         return f"Error: {str(e)}"
# # Usage
# # No need for \\ backslashes, just use the IP address
# ip_address = "192.168.159.171"
# linux_path = "/home/kali/Downloads"
# local_files = "./zTest_Source"
# print(send_files_scp(ip_address, local_files, linux_path, "kali", "kali"))