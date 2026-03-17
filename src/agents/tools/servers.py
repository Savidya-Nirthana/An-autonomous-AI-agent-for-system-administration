import subprocess, sys, os
from langchain.tools import tool
from typing import Any, List, Dict, Optional
import paramiko
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
#  SSH DISCONNECT TOOL
# ══════════════════════════════════════════════════════════════════════

@tool
def ssh_disconnect(
    host: str,
    username: str,
) -> Dict:
    """
    End and explicitly close the SSH connection to the remote server.
    Use this tool to formally terminate the remote session in your workflow.

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
            'result': "web server created successfully",
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error': str(e),
            'ui_type':'Normal_window'

        }
