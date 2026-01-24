from rich.panel import Panel
from rich.align import Align
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

def show_traceroute_ui(traceroute: dict):
    panel = Panel(
        Align.left(
            f"[key]Traceroute[/key]: [success]{traceroute['table']}[/success]",
            vertical="middle"
        ),
        title="🌐 Network Info",
    )
    console.print(panel)


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