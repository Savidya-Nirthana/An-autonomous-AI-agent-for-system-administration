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


def show_file_info_ui(info: dict):
    if not info.get("success"):
        console.print(f"[red]❌ {info.get('error', 'Unknown error')}[/red]")
        return

    table = Table(title=f"📄 File Info: {info['name']}")

    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Name", info.get("name", "N/A"))
    table.add_row("Full Path", info.get("full_path", "N/A"))
    table.add_row("Type", info.get("type", "N/A"))
    table.add_row("Size", f"{info.get('size_bytes', 'N/A')} bytes")
    table.add_row("Permissions", info.get("permissions", "N/A"))
    table.add_row("Owner", info.get("owner", "N/A"))
    table.add_row("Group", info.get("group", "N/A"))
    table.add_row("Last Modified", info.get("last_modified", "N/A"))

    ext = info.get("extension")
    if ext:
        table.add_row("Extension", ext)

    console.print(table)


def show_read_file_ui(info: dict):
    if not info.get("success"):
        console.print(f"[red]❌ {info.get('error', 'Unknown error')}[/red]")
        return

    console.print(f"📄 Reading file: {info['name']}")
    console.print(f"Full path: {info['full_path']}")
    console.print(f"Size: {info['size_bytes']} bytes")
    console.print("-" * 60)

    content = info.get("content", "")
    if not content.strip():
        console.print("[dim]File is empty or contains only whitespace[/dim]")
    else:
        console.print(content)

    console.print("-" * 60)
