
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()


def show_cpu_basic_ui(data: dict):
    cpu = data["cpu_percent"]

    color = "green"
    if cpu >= 80:
        color = "red"
    elif cpu >= 50:
        color = "yellow"

    progress = Progress(
        TextColumn("CPU Usage"),
        BarColumn(),
        TextColumn(f"[{color}]{cpu}%[/]"),
        console=console,
    )

    with progress:
        task = progress.add_task("", total=100)
        progress.update(task, completed=cpu)

    console.print(
        Panel.fit(
            f"[bold]{cpu}%[/bold] CPU utilization",
            title="🧠 CPU Usage",
            border_style=color,
        )
    )


def show_cpu_full_ui(data: dict):
    cpu = data["cpu_percent"]
    per_core = data.get("per_core", [])
    freq = data.get("frequency_mhz", {})
    load = data.get("load_average")

    summary = (
        f"[bold]Overall:[/bold] {cpu}%\n"
        f"[bold]Freq:[/bold] {freq.get('current', 'N/A')} MHz\n"
    )

    console.print(
        Panel(
            summary,
            title="🧠 CPU Summary",
            border_style="cyan",
        )
    )

    table = Table(title="CPU Per-Core Usage", show_lines=True)
    table.add_column("Core")
    table.add_column("Usage %", justify="right")

    for i, usage in enumerate(per_core):
        color = "green"
        if usage >= 80:
            color = "red"
        elif usage >= 50:
            color = "yellow"

        table.add_row(
            f"Core {i}",
            f"[{color}]{usage}%[/]"
        )

    console.print(table)

    if isinstance(load, dict):
        console.print(
            Panel(
                f"1m: {load['1m']}\n5m: {load['5m']}\n15m: {load['15m']}",
                title="📊 Load Average",
                border_style="magenta",
            )
        )
