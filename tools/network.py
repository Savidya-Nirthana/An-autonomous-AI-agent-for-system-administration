from langchain.tools import tool
import platform
import subprocess
import re
from typing import Dict, Any, List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table

console = Console()


@tool
def ping(host: str, count: int = 4, timeout: int = 3) -> Dict[str, Any]:
    """
    Ping tool with Rich live CLI output.

    Args:
        host (str): Hostname or IP address
        count (int): Number of ping packets
        timeout (int): Timeout per packet (seconds)

    please don't show the result from previous ping command. always show the result of current ping command.
    """

    system = platform.system().lower()

    console.print(Panel.fit(
        f"[bold cyan]Pinging[/bold cyan] [bold yellow]{host}[/bold yellow]\n"
        f"[dim]Packets:[/dim] {count}   "
        f"[dim]Timeout:[/dim] {timeout}s   "
        f"[dim]OS:[/dim] {system}",
        title="📡 Ping Tool",
        border_style="cyan"
    ))

    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    elif system in ("linux", "darwin"):
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
    else:
        raise ValueError(f"Unsupported OS: {system}")

    latencies: List[float] = []
    replies = 0

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:

        task = progress.add_task("Sending ICMP packets...", total=count)

        try:
            for line in process.stdout:
                line = line.strip()

                latency_match = re.search(r"time[=<]\s*(\d+\.?\d*)\s*ms", line)

                if latency_match:
                    latency = float(latency_match.group(1))
                    latencies.append(latency)
                    replies += 1
                    console.print(f"[green]✔ Reply[/green] {latency} ms")
                    progress.advance(task)

                elif "timed out" in line.lower():
                    console.print("[red]✖ Request timed out[/red]")
                    progress.advance(task)

        except KeyboardInterrupt:
            process.terminate()
            console.print("\n[bold red]⛔ Ping cancelled by user[/bold red]")

    process.wait()

    packet_loss = int(((count - replies) / count) * 100)
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

    table = Table(title="📊 Ping Summary", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Host", host)
    table.add_row("Packets Sent", str(count))
    table.add_row("Replies", f"{replies}/{count}")
    table.add_row("Packet Loss", f"{packet_loss}%")
    table.add_row(
        "Average Latency",
        f"{avg_latency} ms" if avg_latency else "N/A"
    )

    console.print(table)

    return {
        "host": host,
        "success": replies > 0,
        "packet_loss_percent": packet_loss,
        "average_latency_ms": avg_latency,
    }
