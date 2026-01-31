from rich.console import Console
from rich.panel import Panel
from rich.align import Align

console = Console()

def show_send_files_ui(content):
    content = "\n".join(content)
    console.print(Panel.fit(Align.center(f"{content}"), title="Send Files"))
        