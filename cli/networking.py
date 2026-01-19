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