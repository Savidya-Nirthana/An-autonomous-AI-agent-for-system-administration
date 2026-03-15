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

    console.print(Panel.fit(
        f"[bold cyan]Pinging[/bold cyan] [bold yellow]{host}[/bold yellow]\n"
        f"[dim]Packets:[/dim] {count}   "
        f"[dim]Timeout:[/dim] {timeout}s   "
        f"[dim]OS:[/dim] {system}",
        title="📡 Ping Tool",
        border_style="cyan"
    ))

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

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:

        task = progress.add_task("Sending ICMP packets...", total=count)

        try:
            for line in process.stdout:
                line = line.strip()

                latency_match = re.search(r"time[=<]\s*(\d+\.?\d*)\s*ms", line)

                if latency_match:
                    latency = float(latency_match.group(1))
                    latencies.append(latency)
                    replies += 1
                    console.print(f"[green]✔ Reply[/green] {latency} ms")
                    progress.advance(task)

                elif "timed out" in line.lower():
                    console.print("[red]✖ Request timed out[/red]")
                    progress.advance(task)

        except KeyboardInterrupt:
            process.terminate()
            console.print("\n[bold red]⛔ Ping cancelled by user[/bold red]")

    process.wait()

    packet_loss = int(((count - replies) / count) * 100)
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

    table = Table(title="📊 Ping Summary", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Host", host)
    table.add_row("Packets Sent", str(count))
    table.add_row("Replies", f"{replies}/{count}")
    table.add_row("Packet Loss", f"{packet_loss}%")
    table.add_row(
        "Average Latency",
        f"{avg_latency} ms" if avg_latency else "N/A"
    )

    console.print(table)

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

    console.print(Panel.fit(
        f"[bold cyan]Tracing route[/bold cyan] [bold yellow]{host}[/bold yellow]\n"
        f"[dim]Max Hops:[/dim] {maxHops}   "
        f"[dim]Timeout:[/dim] {timeout}s   "
        f"[dim]OS:[/dim] {system}",
        title="📡 Traceroute Tool",
        border_style="cyan"
    ))

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

    table = Table(title="Traceroute Hops", show_lines=True)
    table.add_column("Hop", justify="right")
    table.add_column("IP Address", justify="left")
    table.add_column("Latency (ms)", justify="left")
    table.add_column("Status", justify="center")

    hop_regex = re.compile(r"^\s*(\d+)\s+(.+)$")
    ip_regex = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
    latency_regex = re.compile(r"(\d+\.?\d*)\s*ms")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Tracing route...", total=maxHops)

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
                table.add_row(
                    str(hop_num),
                    "*",
                    "-",
                    "[red]Timeout[/red]"
                )
            else:
                hop_data = {
                    "hop": hop_num,
                    "ip": ip_match.group(1) if ip_match else "unknown",
                    "latency_ms": [float(x) for x in latencies],
                    "status": "ok"
                }
                table.add_row(
                    str(hop_num),
                    hop_data["ip"],
                    ", ".join(latencies),
                    "[green]OK[/green]"
                )

            hops.append(hop_data)
            progress.advance(task)

    process.wait()

    console.print(table)

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

        
# testing process...


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