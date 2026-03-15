from langchain.tools import tool
import platform
import subprocess
import re
from typing import Dict, Any, List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
import socket
import shutil
import json
from src.utils.execution_log import log_execution

console = Console()


@tool
def get_ip_address() -> Dict[str, Any]:
    """
    Get IP address of the system.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        
        s.close()
        
        return {
            "success": True,
            "ip_address": ip,
            "ui_type": "ip_address"
        }
    except Exception:
        return {
            "success": False,
            "ip_address": "could not get ip address",
            "ui_type": "ip_address"
        }


@tool
def ping(host: str, count: int = 4, timeout: int = 3) -> Dict[str, Any]:
    """
    Get ping details from the ping command. 

    Args:
        host (str): Hostname or IP address
        count (int): Number of ping packets
        timeout (int): Timeout per packet (seconds)

    """

    system = platform.system().lower()

    console.print(f"  [dim]ping {host} ...[/dim]", end="")

    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    elif system in ("linux", "darwin"):
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
    else:
        raise ValueError(f"Unsupported OS: {system}")

    latencies: List[float] = []
    replies = 0

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    try:
        for line in process.stdout:
            line = line.strip()
            latency_match = re.search(r"time[=<]\s*(\d+\.?\d*)\s*ms", line)
            if latency_match:
                latency = float(latency_match.group(1))
                latencies.append(latency)
                replies += 1
    except KeyboardInterrupt:
        process.terminate()

    process.wait()

    packet_loss = int(((count - replies) / count) * 100)
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

    # Print clean one-liner result
    if avg_latency is not None:
        console.print(f" [green]{avg_latency}ms[/green] [dim]loss:{packet_loss}%[/dim]")
    else:
        console.print(f" [red]timeout[/red] [dim]loss:{packet_loss}%[/dim]")

    return {
        "host": host,
        "success": replies > 0,
        "packet_loss_percent": packet_loss,
        "average_latency_ms": avg_latency,
    }





@tool
def traceroute(
    host: str,
    dnsResolve: bool = False,
    maxHops: int = 30,
    timeout: int = 2,
    srcAddr: str = ""
) -> Dict[str, Any]:
    """
    Get the details from traceroute command.
    Args:
        host (str): Hostname or IP address
        dnsResolve (bool): Resolve hostname to IP address
        maxHops (int): Maximum number of hops
        timeout (int): Timeout per packet (seconds)
        srcAddr (str): Source IP address

    if srcAddr is none take my ip address as source address

    please don't show the result from previous traceroute command. always show the result of current traceroute command.
    """

    system = platform.system().lower()

    console.print(f"  [dim]traceroute {host} ...[/dim]")

    if system == "windows":
        cmd = ["tracert", "-d", "-h", str(maxHops), "-w", str(timeout * 1000), host]
    elif system in ("linux", "darwin"):
        cmd = ["traceroute", "-n", "-m", str(maxHops), "-w", str(timeout), host]
    else:
        raise ValueError(f"Unsupported OS: {system}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    hops: List[Dict[str, Any]] = []

    hop_regex = re.compile(r"^\s*(\d+)\s+(.+)$")
    ip_regex = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
    latency_regex = re.compile(r"(\d+\.?\d*)\s*ms")

    for line in process.stdout:
        line = line.strip()
        match = hop_regex.match(line)

        if not match:
            continue

        hop_num = int(match.group(1))
        rest = match.group(2)

        ip_match = ip_regex.search(rest)
        latencies = latency_regex.findall(rest)

        if "*" in rest or not latencies:
            hop_data = {
                "hop": hop_num,
                "ip": "*",
                "latency_ms": [],
                "status": "timeout"
            }
            console.print(f"  [dim]{hop_num}. * timeout[/dim]")
        else:
            hop_data = {
                "hop": hop_num,
                "ip": ip_match.group(1) if ip_match else "unknown",
                "latency_ms": [float(x) for x in latencies],
                "status": "ok"
            }
            avg = sum(float(x) for x in latencies) / len(latencies)
            console.print(f"  [dim]{hop_num}. {hop_data['ip']} {avg:.1f}ms[/dim]")

        hops.append(hop_data)

    process.wait()

    return {
        "host": host,
        "max_hops": maxHops,
        "timeout": timeout,
        "hops": hops
    }

@tool
def show_ipconfig() -> Dict[str, Any]:
    """
    Run ipconfig (Windows) or ifconfig (Linux/macOS)
    Show IP, MAC address, default gateway etc.
    """

    system = platform.system().lower()

    if system == "windows":
        cmd = ["ipconfig", "/all"]
    elif system in ("linux", "darwin"):
        cmd = ["ifconfig"]
    else:
        raise ValueError(f"Unsupported OS: {system}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    output_lines = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Showing IP configuration...", total=1)

        for line in process.stdout:
            line = line.strip()
            console.print(line)
            output_lines.append(line)
            progress.advance(task)

    process.wait()

    full_output = "\n".join(output_lines)

    return {
        "host": "localhost",
        "success": True,
        "ipconfig": full_output
    }


@tool
def get_default_gateway() -> Dict[str, Any]:
    """
    Get the system default gateway.
    """
    system = platform.system().lower()

    try:
        if system == "windows":
            output = subprocess.check_output(
                ["ipconfig"],
                text=True,
                stderr=subprocess.STDOUT
            )
            match = re.search(r"Default Gateway[^\d]*(\d+\.\d+\.\d+\.\d+)", output)
            gateway = match.group(1) if match else None

        elif system in ("linux", "darwin"):
            output = subprocess.check_output(
                ["ip", "route"],
                text=True,
                stderr=subprocess.STDOUT
            )
            match = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", output)
            gateway = match.group(1) if match else None

        else:
            raise ValueError("Unsupported OS")

        return {
            "success": True,
            "default_gateway": gateway,
            "ui_type": "default_gateway"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "default_gateway": None
        }


@tool
def tcp_port_check(host: str, port: int, timeout: int = 5, as_text: bool = False) -> dict | str:
    """
    Cross-platform network check (TCP port).

    Args:
        host (str): Hostname or IP
        port (int): TCP port to test
        timeout (int): Timeout in seconds
        as_text (bool): Return human-readable summary

    please don't return the result from previous exections always call the tool again to get the latest result

    Returns:
        dict or str: Result

    """

    system = platform.system().lower()

    result = {
        "host" : host,
        "port" : port,
        "timeout" : timeout,
        "success" : False,
        "error" : None,
        "ui_type" : "tcp_port_check"
    }


    if system == "windows" and shutil.which("powershell"):
        ps_cmd = f"""
        try {{
            $r = Test-NetConnection -ComputerName "{host}" -Port {port} -InformationLevel Detailed
            $r.TcpTestSucceeded
        }} catch {{
            $false
        }}
        """
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=timeout
            )
            output = completed.stdout.strip().lower()
            result["tcp_success"] = output == "true"
        except Exception:
            result["tcp_success"] = False
    
    else:
        if shutil.which("nc"):
            try:
                completed = subprocess.run(
                    ["nc", "-zv", "-w", str(timeout), host, str(port)],
                    capture_output=True, text=True
                )
                result["tcp_success"] = completed.returncode == 0
            except Exception:
                result["tcp_success"] = False
        else:
            result["tcp_success"] = None 

    result["success"] = result["tcp_success"]

    if as_text:
        return f"✅ Port {port} is open on {host}" if result["tcp_success"] else f"❌ Port {port} is closed on {host}"

    return result

        

    