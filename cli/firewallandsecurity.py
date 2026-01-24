from rich.panel import Panel
from rich.align import Align
from cli.ui_theme import console
from typing import Dict, Any
from rich.table import Table

def show_firewall_status_ui(firewall_status: str) -> None:
    console.print(Panel.fit(Align.center(firewall_status), title="Firewall Status"))

def show_view_saved_credintials_by_os_ui(view_saved_credintials_by_os: Dict[str, Any]) -> None:

    table = Table(title="Currently stored credentials", show_lines=True)

    table.add_column("Title")
    table.add_column("Value")

    for credential in view_saved_credintials_by_os[2:]:
        credential = credential.split(":",2)        
        
        if len(credential) < 2:
            table.add_row(f"[bold yellow]{credential[0]}[/bold yellow]", end_section=True)
        else:
            table.add_row(f"[bold blue]{credential[0]}[/bold blue]",f"[bold green]{credential[1]}[/bold green]", end_section=True)
                
    console.print(Panel.fit(Align.center(table)))

