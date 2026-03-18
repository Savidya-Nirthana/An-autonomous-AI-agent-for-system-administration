import subprocess, sys, os
from langchain.tools import tool
from typing import Any, List, Dict, Optional
import paramiko
from cli.checkOS import checkOS


# Global state to maintain SSH connection
SSH_STATE = {
    "client": None,
    "host": None,
    "username": None
}


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
    Create an SSH connection using username and password authentication, keeping the session open for future commands.
    Use this tool to establish your initial connection to a remote machine before running commands.
    Returns basic server information (hostname, OS, uptime) on success.

    Args:
        host: IP address or hostname of the remote server.
        username: SSH username on the remote server.
        password: SSH password for the user.
        port: SSH port (default 22).
    """
    global SSH_STATE
    try:
        # Close existing connection if there is one
        if SSH_STATE["client"] is not None:
            try:
                SSH_STATE["client"].close()
            except Exception:
                pass
                
        client = _ssh_connect_password(host, port, username, password)

        # Store in state for future commands
        SSH_STATE["client"] = client
        SSH_STATE["host"] = host
        SSH_STATE["username"] = username

        # Gather basic info from the connected server
        info = {}
        for label, cmd in [("hostname", "hostname"), ("os", "uname -a"), ("uptime", "uptime")]:
            try:
                _stdin, stdout, _stderr = client.exec_command(cmd, timeout=10)
                info[label] = stdout.read().decode("utf-8", errors="replace").strip()
            except Exception:
                info[label] = "(unavailable)"

        # Important: DO NOT close the client here so the session persists.
        
        return {
            "success": True,
            "result": (
                f"SSH connection to {username}@{host}:{port} established successfully and kept OPEN.\n"
                f"Hostname : {info.get('hostname', 'N/A')}\n"
                f"OS       : {info.get('os', 'N/A')}\n"
                f"Uptime   : {info.get('uptime', 'N/A')}"
            ),
            "server_info": info,
            "ui_type": "normal_window",
        }
    except Exception as e:
        SSH_STATE["client"] = None
        SSH_STATE["host"] = None
        SSH_STATE["username"] = None
        return {
            "success": False,
            "error": str(e),
            "ui_type": "normal_window",
        }


# ══════════════════════════════════════════════════════════════════════
#  SSH DISCONNECT TOOL
# ══════════════════════════════════════════════════════════════════════

@tool
def ssh_disconnect() -> Dict:
    """
    Explicitly close the active SSH connection to the remote server.
    Use this tool to formally terminate the remote session when finished.
    """
    global SSH_STATE
    client = SSH_STATE.get("client")
    host = SSH_STATE.get("host", "unknown host")
    username = SSH_STATE.get("username", "unknown user")
    
    if client is not None:
        try:
            client.close()
            success = True
            msg = f"SSH connection to {username}@{host} has been securely closed and terminated."
        except Exception as e:
            success = False
            msg = f"Error disconnecting: {e}"
            
        SSH_STATE["client"] = None
        SSH_STATE["host"] = None
        SSH_STATE["username"] = None
        
        return {
            "success": success,
            "result": msg if success else None,
            "error": msg if not success else None,
            "ui_type": "normal_window",
        }
    else:
        return {
            "success": False,
            "error": "No active SSH connection to disconnect.",
            "ui_type": "normal_window",
        }


# ══════════════════════════════════════════════════════════════════════
#  SSH EXECUTE COMMAND TOOL
# ══════════════════════════════════════════════════════════════════════

@tool
def ssh_execute_command(command: str, timeout: int = 30) -> Dict:
    """
    Execute a shell command on the currently connected remote SSH server.
    You MUST call `ssh_connect_password` BEFORE using this tool.
    
    Args:
        command: The shell command string to execute remotely.
        timeout: Maximum seconds to wait for command completion (default: 30).
    """
    global SSH_STATE
    client = SSH_STATE.get("client")
    host = SSH_STATE.get("host")
    username = SSH_STATE.get("username")
    
    if client is None:
        return {
            "success": False,
            "error": "Not connected to any SSH server. You must connect first.",
            "ui_type": "normal_window",
        }
        
    try:
        # Check transport is basically still alive
        if not client.get_transport() or not client.get_transport().is_active():
             return {
                 "success": False,
                 "error": "The SSH connection was dropped or timed out. Please reconnect.",
                 "ui_type": "normal_window",
             }

        _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        
        stdout_text = stdout.read().decode("utf-8", errors="replace").strip()
        stderr_text = stderr.read().decode("utf-8", errors="replace").strip()
        
        # Determine success from exit code (defaults to 0 if command ran correctly)
        exit_status = stdout.channel.recv_exit_status()
        success = (exit_status == 0)

        output = []
        if stdout_text:
            output.append("STDOUT:\n" + stdout_text)
        if stderr_text:
            output.append("STDERR:\n" + stderr_text)
            
        result_str = "\n".join(output) if output else "(no output)"

        return {
            "success": success,
            "result": f"Exit Status: {exit_status}\n{result_str}",
            "ui_type": "normal_window",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute command '{command}': {str(e)}",
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
