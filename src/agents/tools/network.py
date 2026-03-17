from langchain.tools import tool
import platform
import subprocess
import re
from typing import Dict, Any, List
import socket
import shutil
import json
from src.utils.execution_log import log_execution


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

    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    elif system in ("linux", "darwin"):
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
    else:
        raise ValueError(f"Unsupported OS: {system}")

    latencies: List[float] = []
    replies = 0

    try:
        process = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=timeout*count + 5)
        output = process.stdout
        
        for line in output.splitlines():
            latency_match = re.search(r"time[=<]\s*(\d+\.?\d*)\s*ms", line)
            if latency_match:
                latency = float(latency_match.group(1))
                latencies.append(latency)
                replies += 1
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "ping"
        }

    packet_loss = int(((count - replies) / count) * 100) if count > 0 else 100
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

    return {
        "success": True,
        "host": host,
        "packets_sent": count,
        "packets_received": replies,
        "packet_loss_percent": packet_loss,
        "average_latency_ms": avg_latency,
        "ui_type": "ping"
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

    if system == "windows":
        cmd = ["tracert", "-d", "-h", str(maxHops), "-w", str(timeout * 1000), host]
    elif system in ("linux", "darwin"):
        cmd = ["traceroute", "-n", "-m", str(maxHops), "-w", str(timeout), host]
    else:
        raise ValueError(f"Unsupported OS: {system}")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    
    hops: List[Dict[str, Any]] = []
    hop_regex = re.compile(r"^\s*(\d+)\s+(.+)$")
    ip_regex = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
    latency_regex = re.compile(r"(\d+\.?\d*)\s*ms")

    if process.stdout:
        for line in process.stdout:
            line = line.strip()
            match = hop_regex.match(line)
            if match:
                hop_num = int(match.group(1))
                rest = match.group(2)
                ip_match = ip_regex.search(rest)
                latencies = latency_regex.findall(rest)
                
                hops.append({
                    "hop": hop_num,
                    "ip": ip_match.group(1) if ip_match else "*",
                    "latencies": [float(x) for x in latencies],
                    "success": len(latencies) > 0
                })

    process.wait()

    return {
        "success": True,
        "host": host,
        "hops": hops,
        "ui_type": "traceroute"
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

    try:
        process = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        return {
            "success": True,
            "data": process.stdout,
            "output": "IP configuration successfully retrieved and displayed via UI.",
            "ui_type": "ipconfig"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "ipconfig"
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

@tool
def show_ip_mac_details() -> Dict[str, Any]:
    """
    Show IP, Mask, and MAC addresses.
    """
    system = platform.system().lower()
    if system == "windows":
        cmd = ["getmac", "/v"]
    else:
        cmd = ["ip", "addr", "show"]
        
    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": True,
            "data": process.stdout.strip(),
            "output": "IP & MAC details successfully retrieved and displayed via UI.",
            "ui_type": "ip_mac_details"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "ui_type": "ip_mac_details"}

@tool
def show_arp_cache() -> Dict[str, Any]:
    """
    Show ARP cache (IP to MAC mapping).
    """
    system = platform.system().lower()
    if system == "windows":
        cmd = ["arp", "-a"]
    else:
        cmd = ["ip", "neigh", "show"]
        
    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": True,
            "data": process.stdout.strip(),
            "output": "ARP cache successfully retrieved and displayed via UI.",
            "ui_type": "arp_cache"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "ui_type": "arp_cache"}

@tool
def show_active_ports() -> Dict[str, Any]:
    """
    Show active network ports and PIDs.
    """
    system = platform.system().lower()
    if system == "windows":
        cmd = ["netstat", "-an", "-o"]
    else:
        cmd = ["ss", "-tuln"]
        
    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": True,
            "data": process.stdout.strip(),
            "output": "Active network ports successfully retrieved and displayed via UI.",
            "ui_type": "active_ports"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "ui_type": "active_ports"}

@tool
def dns_lookup(domain: str, record_type: str = "A") -> Dict[str, Any]:
    """
    Query DNS records for a domain.
    Args:
        domain (str): Domain name to query
        record_type (str): Type of record (e.g. A, MX, TXT, CNAME). Defaults to A.
    """
    system = platform.system().lower()
    if system == "windows":
        cmd = ["nslookup", f"-type={record_type}", domain]
    else:
        cmd = ["dig", domain, record_type, "+short"]
        
    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": True,
            "domain": domain,
            "record_type": record_type,
            "data": process.stdout.strip(),
            "output": f"DNS records for {domain} ({record_type}) successfully retrieved and displayed via UI.",
            "ui_type": "dns_lookup"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "ui_type": "dns_lookup"}

@tool
def show_routing_table() -> Dict[str, Any]:
    """
    Show the system routing table.
    """
    system = platform.system().lower()
    if system == "windows":
        # using cmd /c and -4 to ensure it finds the command and minimizes output
        cmd = ["cmd", "/c", "route", "print", "-4"]
    else:
        cmd = ["ip", "route", "show"]
        
    try:
        # errors="replace" prevents decoding crashes from weird characters
        process = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        output = process.stdout
        
        # Windows output is huge; return only Active Routes for efficiency
        if system == "windows" and "Active Routes:" in output:
            parts = output.split("Active Routes:")
            if len(parts) > 1:
                active = parts[1].split("Persistent Routes:")[0].strip()
                output = "Active Routes:\n" + active
                
        return {
            "success": True,
            "data": output.strip(),
            "output": "Routing table successfully retrieved and displayed via UI.",
            "ui_type": "routing_table"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "ui_type": "routing_table"}

@tool
def show_wifi_interfaces() -> Dict[str, Any]:
    """
    Show Wi-Fi signal strength and interface details efficiently.
    """
    system = platform.system().lower()
    if system == "windows":
        cmd = ["netsh", "wlan", "show", "interfaces"]
    else:
        if shutil.which("iwconfig"):
            cmd = ["iwconfig"]
        else:
            return {"success": False, "error": "iwconfig not installed", "ui_type": "wifi_interfaces"}
            
    try:
        process = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        output = process.stdout
        
        # Parse Windows output to reduce token bloat (just return key data)
        if system == "windows" and process.returncode == 0:
            parsed_data = {}
            for line in output.split('\n'):
                if ":" in line:
                    key, val = [p.strip() for p in line.split(":", 1)]
                    if key in ["Name", "Description", "State", "SSID", "BSSID", "Network type", "Authentication", "Cipher", "Channel", "Signal"]:
                        parsed_data[key] = val
            if parsed_data:
                output = "\n".join([f"{k}: {v}" for k, v in parsed_data.items()])
                
        return {
            "success": True,
            "data": output.strip(),
            "output": "Wi-Fi interface details successfully retrieved and displayed via UI.",
            "ui_type": "wifi_interfaces"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "ui_type": "wifi_interfaces"}

@tool
def set_static_ip(interface: str, ip: str, mask: str, gateway: str = "") -> Dict[str, Any]:
    """
    Set a static IP address for a network interface (Windows only).
    Equivalent to 'netsh interface ip set address name="<interface>" static <ip> <mask> <gateway>'.
    
    args:
        interface (str): The name of the interface (e.g., "Wi-Fi", "Ethernet").
        ip (str): The static IP address.
        mask (str): The subnet mask.
        gateway (str): The default gateway (optional).
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "static_ip_config"
        }

    try:
        cmd = ["netsh", "interface", "ip", "set", "address", f'name="{interface}"', "static", ip, mask]
        if gateway:
            cmd.append(gateway)
            
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        
        success = result.returncode == 0
        output = result.stdout or result.stderr
        
        # If output is empty and returncode is 0, netsh was successful
        if success and not output.strip():
            output = f"Successfully set static IP {ip} for interface '{interface}'."

        return {
            "success": success,
            "data": output.strip(),
            "output": f"Static IP configuration attempted for: {interface}",
            "ui_type": "static_ip_config",
            "interface": interface,
            "ip": ip,
            "mask": mask,
            "gateway": gateway or "None"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "static_ip_config",
            "interface": interface
        }

@tool
def set_static_dns(interface: str, dns_ip: str) -> Dict[str, Any]:
    """
    Set a static DNS address for a network interface (Windows only).
    Equivalent to 'netsh interface ip set dns name="<interface>" static <dns_ip>'.
    
    args:
        interface (str): The name of the interface (e.g., "Wi-Fi", "Ethernet").
        dns_ip (str): The static DNS IP address (e.g., "8.8.8.8").
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "static_dns_config"
        }

    try:
        # Use simple positional arguments for netsh to avoid quoting issues
        import subprocess
        cmd = ["netsh", "interface", "ip", "set", "dns", interface, "static", dns_ip]
        
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        
        success = result.returncode == 0
        output = result.stdout or result.stderr
        
        if success and not output.strip():
            output = f"Successfully set static DNS {dns_ip} for interface '{interface}'."

        return {
            "success": success,
            "data": output.strip(),
            "output": f"Static DNS configuration attempted for: {interface}",
            "ui_type": "static_dns_config",
            "interface": interface,
            "dns_ip": dns_ip
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "static_dns_config",
            "interface": interface,
            "dns_ip": dns_ip
        }

@tool
def check_netbios_table(remote_ip: str) -> Dict[str, Any]:
    """
    Check the NetBIOS name table of a remote IP address (Windows only).
    Equivalent to 'nbtstat -A <remote_ip>'.
    
    args:
        remote_ip (str): The IP address of the remote system.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "netbios_table"
        }

    try:
        import subprocess
        cmd = ["nbtstat", "-A", remote_ip]
        
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        
        success = result.returncode == 0
        output = result.stdout or result.stderr
        
        return {
            "success": success,
            "data": output.strip(),
            "output": f"NetBIOS table check attempted for: {remote_ip}",
            "ui_type": "netbios_table",
            "remote_ip": remote_ip
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "netbios_table",
            "remote_ip": remote_ip
        }

@tool
def get_network_adapters() -> Dict[str, Any]:
    """
    List all network adapters and their physical status (Windows only).
    Uses PowerShell 'Get-NetAdapter'.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "network_adapters"
        }

    try:
        import subprocess
        import json
        
        # PowerShell command to get adapters and convert to JSON
        ps_cmd = (
            "Get-NetAdapter | "
            "Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress | "
            "ConvertTo-Json"
        )
        
        cmd = ["powershell", "-Command", ps_cmd]
        
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or result.stdout,
                "ui_type": "network_adapters"
            }
            
        output = result.stdout.strip()
        if not output:
             return {
                "success": True,
                "data": [],
                "output": "No network adapters found.",
                "ui_type": "network_adapters"
            }
            
        try:
            data = json.loads(output)
            # Ensure data is always a list
            if isinstance(data, dict):
                data = [data]
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Failed to parse PowerShell output: {output}",
                "ui_type": "network_adapters"
            }

        return {
            "success": True,
            "data": data,
            "output": f"Found {len(data)} network adapter(s).",
            "ui_type": "network_adapters"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "network_adapters"
        }

@tool
def test_net_connection(host: str, port: int = 80) -> Dict[str, Any]:
    """
    Ping and check TCP port connectivity for a remote host (Windows only).
    Uses PowerShell 'Test-NetConnection'.
    
    args:
        host (str): The hostname or IP address to test.
        port (int): The TCP port to test (default is 80).
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "test_net_connection"
        }

    try:
        import subprocess
        import json
        
        # PowerShell command to test connection and convert to JSON
        ps_cmd = (
            f"Test-NetConnection -ComputerName {host} -Port {port} | "
            "Select-Object ComputerName, RemoteAddress, PingSucceeded, TcpTestSucceeded, InterfaceAlias | "
            "ConvertTo-Json"
        )
        
        cmd = ["powershell", "-Command", ps_cmd]
        
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=60)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or result.stdout,
                "ui_type": "test_net_connection"
            }
            
        output = result.stdout.strip()
        if not output:
             return {
                "success": False,
                "error": "No output from Test-NetConnection.",
                "ui_type": "test_net_connection"
            }
            
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Failed to parse PowerShell output: {output}",
                "ui_type": "test_net_connection"
            }

        return {
            "success": True,
            "data": data,
            "output": f"Connection test completed for {host} on port {port}.",
            "ui_type": "test_net_connection",
            "host": host,
            "port": port
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "test_net_connection",
            "host": host,
            "port": port
        }