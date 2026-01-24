from rich.panel import Panel
from rich.align import Align
from cli.ui_theme import console
from typing import List
from rich.table import Table


def show_last_time_sync_details_ui(content):
    # print(type(content))
    content = content.get("result")
    print(result)
    print("-----------")
    print(content)
    console.print(Panel.fit(Align.center(content), title="Last Time Sync Details"))
    # table = Table(title="Last Time Sync Details")

    # table.add_column("Name")
    # table.add_column("Type")
    # table.add_column("Perms")
    # table.add_column("Owner")
    # table.add_column("Group")
    # table.add_column("Size", justify="right")

    # for e in content:
    #     table.add_row(
    #         e["name"],
    #         e["type"],
    #         e["permissions"],
    #         e["owner"],
    #         e["group"],
    #         str(e["size"])
    #     )

    # console.print(table)
