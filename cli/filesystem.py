from rich.panel import Panel
from rich.align import Align
from cli.ui_theme import console
from typing import List
from rich.table import Table


def show_detailed_list_ui(content):
    table = Table(title="📁 Directory Listing")

    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Perms")
    table.add_column("Owner")
    table.add_column("Group")
    table.add_column("Size", justify="right")

    for e in content:
        table.add_row(
            e["name"],
            e["type"],
            e["permissions"],
            e["owner"],
            e["group"],
            str(e["size"])
        )

    console.print(table)

def show_simple_list_ui(entries):
    for e in entries:
        icon = "📁" if e["type"] == "dir" else "📄"
        print(f"{icon} {e['name']}")