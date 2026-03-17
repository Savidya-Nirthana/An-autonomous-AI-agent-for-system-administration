from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich import box
from cli.ui_theme import console

def show_default_gateway_ui(gateway: str):
    panel = Panel(
        Align.left(
            f"[key]Default Gateway[/key]: [success]{gateway}[/success]",
            vertical="middle"
        ),
        title="🌐 Network Info",
    )
    console.print(panel)


def show_ip_address_ui(ip_address: str):
    panel = Panel(
        Align.left(
            f"[key]IP Address[/key]: [success]{ip_address}[/success]",
            vertical="middle"
        ),
        title="🌐 Network Info",
    )
    console.print(panel)

def show_traceroute_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="📡 Traceroute Error", border_style="red"))
        return

    hops = data.get("hops", [])
    table = Table(title=f"Traceroute: {data.get('host')}", show_lines=True, header_style="bold magenta")
    table.add_column("Hop", justify="right")
    table.add_column("IP Address", justify="left", style="cyan")
    table.add_column("Latency (ms)", justify="left", style="green")
    table.add_column("Status", justify="center")

    for h in hops:
        latencies = ", ".join([str(l) for l in h.get("latencies", [])]) or "-"
        status = "[green]OK[/green]" if h.get("success") else "[red]Timeout[/red]"
        table.add_row(str(h["hop"]), h["ip"], latencies, status)

    console.print(Panel(table, border_style="magenta", expand=False))


def show_ping_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="📡 Ping Error", border_style="red"))
        return

    table = Table(title=f"Ping Summary: {data.get('host')}", show_header=False, border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")

    table.add_row("Host", data.get("host"))
    table.add_row("Packets Sent", str(data.get("packets_sent")))
    table.add_row("Packets Received", f"{data.get('packets_received')}/{data.get('packets_sent')}")
    table.add_row("Packet Loss", f"{data.get('packet_loss_percent')}%")
    table.add_row("Average Latency", f"{data.get('average_latency_ms')} ms" if data.get("average_latency_ms") else "N/A")

    console.print(Panel(table, border_style="cyan", expand=False))


def show_ipconfig_ui(data: dict):
    output = data.get("data", "No output available.")
    console.print(Panel(output.strip(), title="🌐 IP Configuration", border_style="blue"))


def show_ip_mac_details_ui(data: dict):
    output = data.get("data", "No details found.")
    
    table = Table(title="🌐 IP & MAC Details", border_style="blue", show_header=True, header_style="bold blue")
    table.add_column("Connection Name", style="cyan")
    table.add_column("Network Adapter", style="white")
    table.add_column("Physical Address", style="magenta")
    table.add_column("Transport Name", style="dim")

    lines = output.split('\n')
    found_header = False
    for line in lines:
        if "Physical Address" in line and "Transport Name" in line:
            found_header = True
            continue
        if found_header and line.strip() and not line.startswith("="):
            # Parsing getmac /v output which is usually fixed width or space separated
            # Connection Name | Network Adapter | Physical Address | Transport Name
            parts = [p.strip() for p in line.split('  ') if p.strip()]
            if len(parts) >= 3:
                # Handle cases where some fields might be empty or combined
                name = parts[0]
                adapter = parts[1]
                mac = parts[2]
                transport = parts[3] if len(parts) > 3 else "N/A"
                table.add_row(name, adapter, mac, transport)

    if table.row_count == 0:
        console.print(Panel(output.strip(), title="🌐 IP & MAC Details", border_style="blue"))
    else:
        console.print(table)


def show_arp_cache_ui(data: dict):
    output = data.get("data", "ARP cache unavailable.")
    
    table = Table(title="🔗 ARP Cache", border_style="green", show_header=True, header_style="bold green")
    table.add_column("Internet Address", style="cyan")
    table.add_column("Physical Address", style="magenta")
    table.add_column("Type", style="white")

    lines = output.split('\n')
    for line in lines:
        # Match IP addresses (Windows arp -a format)
        parts = [p.strip() for p in line.split() if p.strip()]
        if len(parts) >= 3 and "." in parts[0] and "-" in parts[1]:
            table.add_row(parts[0], parts[1], parts[2])

    if table.row_count == 0:
        console.print(Panel(output.strip(), title="🔗 ARP Cache", border_style="green"))
    else:
        console.print(table)


def show_active_ports_ui(data: dict):
    output = data.get("data", "No active ports detectable.")
    
    table = Table(title="🔌 Active Network Ports", border_style="magenta", show_header=True, header_style="bold magenta")
    table.add_column("Proto", style="cyan")
    table.add_column("Local Address", style="white")
    table.add_column("Foreign Address", style="yellow")
    table.add_column("State", style="green")
    table.add_column("PID", style="dim")

    lines = output.split('\n')
    for line in lines:
        parts = [p.strip() for p in line.split() if p.strip()]
        # Windows netstat -an -o format: Proto | Local Addr | Foreign Addr | State | PID
        if len(parts) >= 4 and parts[0] in ["TCP", "UDP"]:
            proto = parts[0]
            local = parts[1]
            foreign = parts[2]
            if proto == "TCP":
                state = parts[3]
                pid = parts[4] if len(parts) > 4 else "N/A"
            else:
                state = "N/A"
                pid = parts[3] if len(parts) > 3 else "N/A"
            table.add_row(proto, local, foreign, state, pid)

    if table.row_count == 0:
        console.print(Panel(output.strip(), title="🔌 Active Network Ports", border_style="magenta"))
    else:
        console.print(table)


def show_dns_lookup_ui(data: dict):
    output = data.get("data", "No DNS records found.")
    domain = data.get("domain", "N/A")
    rtype = data.get("record_type", "A")
    console.print(Panel(output.strip(), title=f"🔍 DNS Lookup: {domain} ({rtype})", border_style="cyan"))


def show_routing_table_ui(data: dict):
    output = data.get("data", "Routing table unavailable.")
    
    table = Table(title="🛣️ Routing Table", border_style="red", show_header=True, header_style="bold red")
    table.add_column("Destination", style="cyan")
    table.add_column("Netmask", style="dim")
    table.add_column("Gateway", style="yellow")
    table.add_column("Interface", style="white")
    table.add_column("Metric", style="magenta")

    lines = output.split('\n')
    found_routes = False
    for line in lines:
        if "Network Destination" in line:
            found_routes = True
            continue
        if found_routes:
            parts = [p.strip() for p in line.split() if p.strip()]
            if len(parts) >= 5 and "." in parts[0]:
                table.add_row(parts[0], parts[1], parts[2], parts[3], parts[4])
            elif len(parts) == 0 and table.row_count > 0:
                # End of active routes section
                break

    if table.row_count == 0:
        console.print(Panel(output.strip(), title="🛣️ Routing Table", border_style="red"))
    else:
        console.print(table)


def show_wifi_interfaces_ui(data: dict):
    output = data.get("data", "No Wi-Fi interfaces found.")
    console.print(Panel(output.strip(), title="📡 Wi-Fi Interfaces", border_style="yellow"))


def show_network_fix_ui(data: dict):
    operation = data.get("operation", "Network Fix")
    success = data.get("success", False)
    output = data.get("data", "No output available.")
    
    color = "green" if success else "red"
    title = f"🛠️ {operation}: {'Success' if success else 'Failed'}"
    
    console.print(Panel(output.strip(), title=title, border_style=color))


def show_tcp_port_check_ui(tcp_port_check: dict):
    host = tcp_port_check.get("host", "N/A")
    port = tcp_port_check.get("port", "N/A")
    timeout = tcp_port_check.get("timeout", "N/A")
    tcp_success = tcp_port_check.get("tcp_success", False)
    success = tcp_port_check.get("success", False)
    error = tcp_port_check.get("error")

    status_text = "[green]OPEN[/green]" if tcp_success else "[red]CLOSED[/red]"
    overall = "[green]SUCCESS[/green]" if success else "[red]FAILED[/red]"

    content = f"""
[key]Host[/key]        : {host}
[key]Port[/key]        : {port}
[key]Timeout[/key]     : {timeout}s
[key]TCP Status[/key]  : {status_text}
[key]Result[/key]      : {overall}
"""

    if error:
        content += f"\n[key]Error[/key]       : [red]{error}[/red]"

    panel = Panel(
        Align.left(content.strip()),
        title="🌐 TCP Port Check",
        border_style="cyan"
    )

    console.print(panel)


def show_static_ip_ui(data: dict):
    interface = data.get("interface", "N/A")
    ip = data.get("ip", "N/A")
    mask = data.get("mask", "N/A")
    gateway = data.get("gateway", "None")
    success = data.get("success", False)
    output = data.get("data", "No output available.")
    
    color = "green" if success else "red"
    status_text = "SUCCESS" if success else "FAILED"
    
    title = f"🌐 Set Static IP: {status_text}"
    
    info = f"[bold cyan]Interface:[/] {interface}\n"
    info += f"[bold cyan]IP Address:[/] {ip}\n"
    info += f"[bold cyan]Subnet Mask:[/] {mask}\n"
    info += f"[bold cyan]Gateway:[/] {gateway}\n"
    info += f"─" * 40 + "\n"
    info += output.strip()
    
    console.print(Panel(info, title=title, border_style=color))


def show_test_net_connection_ui(data: dict):
    success = data.get("success", False)
    test_data = data.get("data", {})
    host = data.get("host", "N/A")
    port = data.get("port", "N/A")
    error = data.get("error")
    
    if not success:
        console.print(Panel(f"[red]Error:[/] {error or 'Unknown error'}", title="❌ Connection Test Failed", border_style="red"))
        return

    # Extract fields from PowerShell JSON
    computer = test_data.get("ComputerName", "N/A")
    remote_ip = test_data.get("RemoteAddress", "N/A")
    ping_ok = test_data.get("PingSucceeded", False)
    tcp_ok = test_data.get("TcpTestSucceeded", False)
    interface = test_data.get("InterfaceAlias", "N/A")
    
    tcp_status = "[green]SUCCESS[/]" if tcp_ok else "[red]FAILED[/]"
    ping_status = "[green]SUCCESS[/]" if ping_ok else "[red]FAILED[/]"
    
    title = f"🔌 Connection Test: {host}"
    color = "green" if (tcp_ok or ping_ok) else "red"
    
    info = f"[bold cyan]Computer:[/] {computer}\n"
    info += f"[bold cyan]Remote IP:[/] {remote_ip}\n"
    info += f"[bold cyan]Interface:[/] {interface}\n"
    info += f"─" * 40 + "\n"
    info += f"[bold cyan]Ping Status:[/] {ping_status}\n"
    info += f"[bold cyan]TCP Port {port} Status:[/] {tcp_status}\n"
    
    console.print(Panel(info, title=title, border_style=color))


def show_netbios_table_ui(data: dict):
    remote_ip = data.get("remote_ip", "N/A")
    success = data.get("success", False)
    output = data.get("data", "No output available.")
    
    color = "green" if success else "red"
    status_text = "SUCCESS" if success else "FAILED"
    
    title = f"🔍 NetBIOS Table: {remote_ip} ({status_text})"
    
    # Simple display of the raw output in a panel for now, 
    # as nbtstat output format is tricky to table-parse reliably
    console.print(Panel(output.strip(), title=title, border_style=color))


def show_network_adapters_ui(data: dict):
    success = data.get("success", False)
    adapters = data.get("data", [])
    output_msg = data.get("output", "")
    error = data.get("error")
    
    if not success:
        console.print(Panel(f"[red]Error:[/] {error or 'Unknown error'}", title="❌ Network Adapters", border_style="red"))
        return

    if not adapters:
        console.print(Panel(output_msg, title="🌐 Network Adapters", border_style="yellow"))
        return

    table = Table(title="🌐 Network Adapters", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Link Speed")
    table.add_column("MAC Address", style="dim")

    for adapter in adapters:
        status = str(adapter.get("Status", "Unknown"))
        status_color = "green" if status.lower() == "up" else "red"
        
        table.add_row(
            str(adapter.get("Name", "N/A")),
            str(adapter.get("InterfaceDescription", "N/A")),
            f"[{status_color}]{status}[/]",
            str(adapter.get("LinkSpeed", "N/A")),
            str(adapter.get("MacAddress", "N/A"))
        )

    console.print(table)


def show_static_dns_ui(data: dict):
    interface = data.get("interface", "N/A")
    dns_ip = data.get("dns_ip", "N/A")
    success = data.get("success", False)
    output = data.get("data", "No output available.")
    
    color = "green" if success else "red"
    status_text = "SUCCESS" if success else "FAILED"
    
    title = f"🌐 Set Static DNS: {status_text}"
    
    info = f"[bold cyan]Interface:[/] {interface}\n"
    info += f"[bold cyan]DNS IP Address:[/] {dns_ip}\n"
    info += f"─" * 40 + "\n"
    info += output.strip()
    
    console.print(Panel(info, title=title, border_style=color))