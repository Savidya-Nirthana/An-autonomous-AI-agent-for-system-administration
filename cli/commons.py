from rich.panel import Panel
from rich.align import Align
from cli.ui_theme import console
from typing import Dict, Any
from rich.table import Table

def normal_window(normal_window:str ) -> None:
    console.print(Panel.fit(Align.center(normal_window), title="Status"))