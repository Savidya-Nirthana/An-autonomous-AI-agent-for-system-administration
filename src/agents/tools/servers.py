import subprocess, sys, os
from langchain.tools import tool
from typing import Any, List, Dict, Optional
import paramiko
from scp import SCPClient
from cli.checkOS import checkOS


# ── Helper: create SSH client with password auth ─────────────────────
def _ssh_connect_password(host: str, port: int, username: str, password: str) -> paramiko.SSHClient:
    """Create and return an SSH client connected via username/password."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port, username=username, password=password, timeout=15)
    return client


# ── Helper: create SSH client with RSA key auth ─────────────────────
def _ssh_connect_rsa(host: str, port: int, username: str, key_path: str) -> paramiko.SSHClient:
    """Create and return an SSH client connected via RSA private key."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file(key_path)
    client.connect(hostname=host, port=port, username=username, pkey=private_key, timeout=15)
    return client


# ══════════════════════════════════════════════════════════════════════
#  SSH CONNECTION TOOL
# ══════════════════════════════════════════════════════════════════════

@tool
def ssh_connect_password(
    host: str,
    username: str,
    password: str,
    port: int = 22,
) -> Dict:
    """
    Create and test an SSH connection to a remote server using username and password authentication.
    Use this tool to establish, verify, and test SSH connectivity to a remote machine.
    Returns basic server information (hostname, OS, uptime) on success.

    Args:
        host: IP address or hostname of the remote server.
        username: SSH username on the remote server.
        password: SSH password for the user.
        port: SSH port (default 22).
    """
    try:
        client = _ssh_connect_password(host, port, username, password)

        # Gather basic info from the connected server
        info = {}
        for label, cmd in [("hostname", "hostname"), ("os", "uname -a"), ("uptime", "uptime")]:
            try:
                _stdin, stdout, _stderr = client.exec_command(cmd, timeout=10)
                info[label] = stdout.read().decode("utf-8", errors="replace").strip()
            except Exception:
                info[label] = "(unavailable)"

        client.close()

        return {
            "success": True,
            "result": (
                f"SSH connection to {username}@{host}:{port} established successfully.\n"
                f"Hostname : {info.get('hostname', 'N/A')}\n"
                f"OS       : {info.get('os', 'N/A')}\n"
                f"Uptime   : {info.get('uptime', 'N/A')}"
            ),
            "server_info": info,
            "ui_type": "normal_window",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "normal_window",
        }


# ══════════════════════════════════════════════════════════════════════
#  EXISTING TOOL
# ══════════════════════════════════════════════════════════════════════

@tool
def ssh_disconnect(
    host: str,
    username: str,
) -> Dict:
    """
    End and explicitly close the SSH connection to the remote server.
    Use this tool to formally terminate the remote session in your workflow.
    (Note: The underlying system automatically closes connections behind the scenes after each operation to prevent resource leaks, but calling this tool finalizes the logical session).

    Args:
        host: IP address or hostname of the remote server.
        username: SSH username on the remote server.
    """
    return {
        "success": True,
        "result": f"SSH connection to {username}@{host} has been securely closed and terminated.",
        "ui_type": "normal_window",
    }


#tested on windows
@tool
def webserver(path: str = "./", port: int = 8080) -> Dict :
    '''
        create a web server 
        if the requested path is empty or dosen't exist, 
        create that path and add a simple index.html 
        that has "hello" text inside it and 
        (
            <!doctype html>
            <html><body><h1>Hello from server </h1></body></html>
        ) 
        create the server 
    '''

    try:
        os_name = checkOS()
        
        if os_name == 'windows':
            cmd = f"python -m http.server {port}"
            os.system(f'start cmd /k "{cmd}"')
        else:
            cmd = f"python3 -m http.server {port}"
            os.system(f'nohup {cmd} &')

        return {
            'success':True,
            # 'result': response.stdout,
            'result': "web server created successfully",
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error': str(e),
            'ui_type':'Normal_window'

        }


# ══════════════════════════════════════════════════════════════════════
#  SSH FILE UPLOAD TOOLS
# ══════════════════════════════════════════════════════════════════════

# @tool
# def ssh_upload_file_password(
#     host: str,
#     username: str,
#     password: str,
#     local_path: str,
#     remote_path: str,
#     port: int = 22,
# ) -> Dict:
#     """
#     Upload a local file to a remote server via SCP using SSH username and password authentication.
    
#     Args:
#         host: IP address or hostname of the remote server.
#         username: SSH username on the remote server.
#         password: SSH password for the user.
#         local_path: Full path to the local file to upload.
#         remote_path: Destination path on the remote server.
#         port: SSH port (default 22).
#     """
#     try:
#         client = _ssh_connect_password(host, port, username, password)
#         with SCPClient(client.get_transport()) as scp:
#             scp.put(local_path, remote_path)
#         client.close()
#         return {
#             'success': True,
#             'result': f'File "{local_path}" uploaded to {host}:{remote_path} successfully.',
#             'ui_type': 'normal_window'
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e),
#             'ui_type': 'normal_window'
#         }


# @tool
# def ssh_upload_file_rsa(
#     host: str,
#     username: str,
#     key_path: str,
#     local_path: str,
#     remote_path: str,
#     port: int = 22,
# ) -> Dict:
#     """
#     Upload a local file to a remote server via SCP using RSA private key authentication.
    
#     Args:
#         host: IP address or hostname of the remote server.
#         username: SSH username on the remote server.
#         key_path: Full path to the RSA private key file (e.g. ~/.ssh/id_rsa).
#         local_path: Full path to the local file to upload.
#         remote_path: Destination path on the remote server.
#         port: SSH port (default 22).
#     """
#     try:
#         client = _ssh_connect_rsa(host, port, username, key_path)
#         with SCPClient(client.get_transport()) as scp:
#             scp.put(local_path, remote_path)
#         client.close()
#         return {
#             'success': True,
#             'result': f'File "{local_path}" uploaded to {host}:{remote_path} successfully (RSA auth).',
#             'ui_type': 'normal_window'
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e),
#             'ui_type': 'normal_window'
#         }


# # ══════════════════════════════════════════════════════════════════════
# #  SSH FILE DOWNLOAD TOOLS
# # ══════════════════════════════════════════════════════════════════════

# @tool
# def ssh_download_file_password(
#     host: str,
#     username: str,
#     password: str,
#     remote_path: str,
#     local_path: str,
#     port: int = 22,
# ) -> Dict:
#     """
#     Download a file from a remote server to the local machine via SCP using SSH username and password authentication.
    
#     Args:
#         host: IP address or hostname of the remote server.
#         username: SSH username on the remote server.
#         password: SSH password for the user.
#         remote_path: Path of the file on the remote server to download.
#         local_path: Destination path on the local machine.
#         port: SSH port (default 22).
#     """
#     try:
#         client = _ssh_connect_password(host, port, username, password)
#         with SCPClient(client.get_transport()) as scp:
#             scp.get(remote_path, local_path)
#         client.close()
#         return {
#             'success': True,
#             'result': f'File "{remote_path}" downloaded from {host} to "{local_path}" successfully.',
#             'ui_type': 'normal_window'
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e),
#             'ui_type': 'normal_window'
#         }


# @tool
# def ssh_download_file_rsa(
#     host: str,
#     username: str,
#     key_path: str,
#     remote_path: str,
#     local_path: str,
#     port: int = 22,
# ) -> Dict:
#     """
#     Download a file from a remote server to the local machine via SCP using RSA private key authentication.
    
#     Args:
#         host: IP address or hostname of the remote server.
#         username: SSH username on the remote server.
#         key_path: Full path to the RSA private key file (e.g. ~/.ssh/id_rsa).
#         remote_path: Path of the file on the remote server to download.
#         local_path: Destination path on the local machine.
#         port: SSH port (default 22).
#     """
#     try:
#         client = _ssh_connect_rsa(host, port, username, key_path)
#         with SCPClient(client.get_transport()) as scp:
#             scp.get(remote_path, local_path)
#         client.close()
#         return {
#             'success': True,
#             'result': f'File "{remote_path}" downloaded from {host} to "{local_path}" successfully (RSA auth).',
#             'ui_type': 'normal_window'
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e),
#             'ui_type': 'normal_window'
#         }


# # ══════════════════════════════════════════════════════════════════════
# #  SSH REMOTE COMMAND EXECUTION TOOLS
# # ══════════════════════════════════════════════════════════════════════

# @tool
# def ssh_execute_command_password(
#     host: str,
#     username: str,
#     password: str,
#     command: str,
#     port: int = 22,
#     work_dir: Optional[str] = None,
# ) -> Dict:
#     """
#     Execute a command on a remote server via SSH using username and password authentication.
#     Use this to run shell commands, check status, install packages, manage services, etc. on another PC or server.
    
#     Args:
#         host: IP address or hostname of the remote server.
#         username: SSH username on the remote server.
#         password: SSH password for the user.
#         command: The shell command to execute on the remote server.
#         port: SSH port (default 22).
#         work_dir: Optional path to change to before executing the command.
#     """
#     try:
#         client = _ssh_connect_password(host, port, username, password)
#         if work_dir:
#             command = f"cd {work_dir} && {command}"
#         stdin, stdout, stderr = client.exec_command(command, timeout=30)
#         output = stdout.read().decode('utf-8', errors='replace')
#         errors = stderr.read().decode('utf-8', errors='replace')
#         exit_code = stdout.channel.recv_exit_status()
#         client.close()

#         return {
#             'success': exit_code == 0,
#             'result': output if output else '(no output)',
#             'error': errors if errors else None,
#             'exit_code': exit_code,
#             'ui_type': 'normal_window'
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e),
#             'ui_type': 'normal_window'
#         }


# @tool
# def ssh_execute_command_rsa(
#     host: str,
#     username: str,
#     key_path: str,
#     command: str,
#     port: int = 22,
#     work_dir: Optional[str] = None,
# ) -> Dict:
#     """
#     Execute a command on a remote server via SSH using RSA private key authentication.
#     Use this to run shell commands, check status, install packages, manage services, etc. on another PC or server.
    
#     Args:
#         host: IP address or hostname of the remote server.
#         username: SSH username on the remote server.
#         key_path: Full path to the RSA private key file (e.g. ~/.ssh/id_rsa).
#         command: The shell command to execute on the remote server.
#         port: SSH port (default 22).
#         work_dir: Optional path to change to before executing the command.
#     """
#     try:
#         client = _ssh_connect_rsa(host, port, username, key_path)
#         if work_dir:
#             command = f"cd {work_dir} && {command}"
#         stdin, stdout, stderr = client.exec_command(command, timeout=30)
#         output = stdout.read().decode('utf-8', errors='replace')
#         errors = stderr.read().decode('utf-8', errors='replace')
#         exit_code = stdout.channel.recv_exit_status()
#         client.close()

#         return {
#             'success': exit_code == 0,
#             'result': output if output else '(no output)',
#             'error': errors if errors else None,
#             'exit_code': exit_code,
#             'ui_type': 'normal_window'
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e),
#             'ui_type': 'normal_window'
#         }


# # ══════════════════════════════════════════════════════════════════════
# #  SSH RSA KEY MANAGEMENT TOOLS
# # ══════════════════════════════════════════════════════════════════════

# @tool
# def generate_ssh_rsa_key(key_path: str) -> Dict:
#     """
#     Generate an RSA SSH key pair (private and public keys).
    
#     Args:
#         key_path: The full path to save the private key (e.g., ~/.ssh/id_rsa).
#                   The public key will be saved as <key_path>.pub.
#     """
#     try:
#         key_path = os.path.expanduser(key_path)
#         pub_key_path = f"{key_path}.pub"
        
#         # Ensure directory exists
#         os.makedirs(os.path.dirname(key_path) or '.', exist_ok=True)
        
#         # Generate the RSA key
#         key = paramiko.RSAKey.generate(2048)
#         key.write_private_key_file(key_path)
        
#         # Write the public key
#         with open(pub_key_path, "w") as f:
#             f.write(f"{key.get_name()} {key.get_base64()} autogenerated-by-agent")
            
#         # On Unix, ensure the private key has correct permissions (0600)
#         if hasattr(os, 'chmod'):
#             try:
#                 os.chmod(key_path, 0o600)
#             except Exception:
#                 pass
            
#         return {
#             'success': True,
#             'result': f"Successfully generated RSA key pair! Private key at '{key_path}', public key at '{pub_key_path}'.",
#             'ui_type': 'normal_window'
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': str(e),
#             'ui_type': 'normal_window'
#         }


# @tool
# def deploy_ssh_rsa_public_key(
#     host: str, 
#     username: str, 
#     password: str, 
#     public_key_path: str, 
#     port: int = 22
# ) -> Dict:


    # """
    # Deploy a local SSH public key to a remote server's ~/.ssh/authorized_keys file using a password.
    # This enables passwordless (RSA key-based) login for future connections.
    
    # Args:
    #     host: IP address or hostname of the remote server.
    #     username: SSH username on the remote server.
    #     password: SSH password for the user.
    #     public_key_path: Full path to the local public key file (e.g., ~/.ssh/id_rsa.pub).
    #     port: SSH port (default 22).
    # """
    # try:
    #     public_key_path = os.path.expanduser(public_key_path)
    #     with open(public_key_path, "r") as f:
    #         pub_key_content = f.read().strip()
            
    #     client = _ssh_connect_password(host, port, username, password)
        
    #     # Create .ssh directory if it doesn't exist, and append the key
    #     commands = [
    #         "mkdir -p ~/.ssh",
    #         "chmod 700 ~/.ssh",
    #         f"echo '{pub_key_content}' >> ~/.ssh/authorized_keys",
    #         "chmod 600 ~/.ssh/authorized_keys"
    #     ]
        
    #     for cmd in commands:
    #         stdin, stdout, stderr = client.exec_command(cmd)
    #         exit_status = stdout.channel.recv_exit_status()
    #         if exit_status != 0:
    #             error_msg = stderr.read().decode().strip()
    #             client.close()
    #             return {
    #                 'success': False,
    #                 'error': f"Failed to execute '{cmd}': {error_msg}",
    #                 'ui_type': 'normal_window'
    #             }
                
    #     client.close()
    #     return {
    #         'success': True,
    #         'result': f"Successfully deployed public key to {username}@{host}. You can now use RSA key authenication.",
    #         'ui_type': 'normal_window'
    #     }
    # except Exception as e:
    #     return {
    #         'success': False,
    #         'error': str(e),
    #         'ui_type': 'normal_window'
    #     }


# ssh_upload_file_password,
# ssh_upload_file_rsa,
# ssh_download_file_password,
# ssh_download_file_rsa,
# ssh_execute_command_password,
# ssh_execute_command_rsa,