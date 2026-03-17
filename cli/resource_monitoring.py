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


def show_memory_usage_ui(data: dict):
    percent = data["percent"]
    total = data["total_gb"]
    used = data["used_gb"]
    available = data["available_gb"]

    color = "green"
    if percent >= 85:
        color = "red"
    elif percent >= 60:
        color = "yellow"

    progress = Progress(
        TextColumn("[bold cyan]RAM Usage[/]"),
        BarColumn(bar_width=40),
        TextColumn(f"[{color}]{percent}%[/]"),
        console=console,
    )

    with progress:
        task = progress.add_task("", total=100)
        progress.update(task, completed=percent)

    table = Table(show_header=True, header_style="bold magenta", padding=(0, 2))
    table.add_column("Stat", style="dim")
    table.add_column("Value", justify="right")
    table.add_row("Total RAM", f"{total} GB")
    table.add_row("Used RAM", f"[bold {color}]{used} GB[/]")
    table.add_row("Available RAM", f"{available} GB")

    console.print(Panel(table, title="💾 Memory Usage Details", border_style="cyan"))


def show_disk_usage_ui(data: dict):
    percent = data["percent"]
    total = data["total_gb"]
    used = data["used_gb"]
    free = data["free_gb"]

    color = "green"
    if percent >= 90:
        color = "red"
    elif percent >= 75:
        color = "yellow"

    progress = Progress(
        TextColumn("[bold magenta]Disk Usage[/]"),
        BarColumn(bar_width=40),
        TextColumn(f"[{color}]{percent}%[/]"),
        console=console,
    )

    with progress:
        task = progress.add_task("", total=100)
        progress.update(task, completed=percent)

    table = Table(show_header=True, header_style="bold cyan", padding=(0, 2))
    table.add_column("Stat", style="dim")
    table.add_column("Value", justify="right")
    table.add_row("Total Space", f"{total} GB")
    table.add_row("Used Space", f"{used} GB")
    table.add_row("Free Space", f"[bold green]{free} GB[/]")

    console.print(Panel(table, title="💽 Disk Usage (Root)", border_style="magenta"))


def show_processes_ui(data: dict):
    procs = data.get("top_processes", [])
    count = data.get("process_count", 0)

    table = Table(title=f"Top Processes (Total: {count})", show_lines=False, header_style="bold blue")
    table.add_column("PID", justify="right", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Status", style="dim")
    table.add_column("Memory %", justify="right")
    table.add_column("User", style="yellow")

    for p in procs:
        mem = p.get("memory_percent") or 0
        mem_str = f"{mem:.2f}%" if mem > 0 else "0.00%"
        
        status = p.get("status", "unknown")
        status_color = "green" if status == "running" else "white"
        
        table.add_row(
            str(p.get("pid", "N/A")),
            p.get("name", "Unknown"),
            f"[{status_color}]{status}[/]",
            mem_str,
            p.get("username") or "N/A"
        )

    console.print(Panel(table, title="[bold white]Processes Information[/bold white]", border_style="blue", expand=False))


def show_system_info_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="🖥️ System Info Error", border_style="red"))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan")
    table.add_column("Value")

    table.add_row("🖥️ OS Name", data.get("os_name", "N/A"))
    table.add_row("🔢 OS Version", data.get("os_version", "N/A"))
    table.add_row("🏢 Manufacturer", data.get("os_manufacturer", "N/A"))
    table.add_row("🧬 BIOS Version", data.get("bios_version", "N/A"))
    table.add_row("⏱️ System Uptime", f"[bold green]{data.get('boot_time', 'N/A')}[/]")
    
    hotfixes = data.get("hotfixes", "N/A")
    # Clean up hotfix display if it's long
    if hotfixes and len(hotfixes) > 100:
        hotfixes = hotfixes[:97] + "..."
    
    table.add_row("📜 Hotfix(s)", hotfixes)

    console.print(Panel(table, title="[bold white]System Information[/bold white]", border_style="blue", expand=False))


def show_drivers_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="🚗 Driver Query Error", border_style="red"))
        return

    drivers = data.get("drivers", [])
    total = data.get("total_drivers", 0)

    table = Table(title=f"Installed Drivers (Showing top {len(drivers)} of {total})", show_lines=False, header_style="bold green")
    table.add_column("Module Name", style="cyan")
    table.add_column("Display Name", style="white")
    table.add_column("Driver Type", style="dim")
    table.add_column("State", style="yellow")

    # CSV headers from driverquery /v:
    # Module Name,Display Name,Description,Driver Type,Start Mode,State,Status,Accept Stop,Accept Pause,Paged Pool(bytes),Code(bytes),BSS(bytes),Link Date,Path,Init(bytes)
    
    for d in drivers:
        state = d.get("State", "Unknown")
        state_color = "green" if state.lower() == "running" else "white"
        
        table.add_row(
            d.get("Module Name", "N/A"),
            d.get("Display Name", "N/A"),
            d.get("Driver Type", "N/A"),
            f"[{state_color}]{state}[/]"
        )
    console.print(Panel(table, title="[bold white]Drivers Information[/bold white]", border_style="blue", expand=False))


def show_user_info_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="👤 User Query Error", border_style="red"))
        return

    # 1. User Info Section
    user = data.get("user", {})
    if user:
        user_table = Table(show_header=False, box=None, padding=(0, 2))
        user_table.add_column("Key", style="cyan bold")
        user_table.add_column("Value", style="white")
        
        user_table.add_row("👤 User Name", user.get("User Name", "N/A"))
        user_table.add_row("🔑 SID", user.get("SID", "N/A"))
        
        console.print(Panel(user_table, title="[bold cyan]User Identity[/]", border_style="cyan", expand=False))

    # 2. Groups Section (Table)
    groups = data.get("groups", [])
    if groups:
        group_table = Table(title="Group Memberships", show_lines=False, header_style="bold magenta", expand=True)
        group_table.add_column("Group Name", style="magenta")
        group_table.add_column("Type", style="dim")
        group_table.add_column("SID", style="dim")
        group_table.add_column("Attributes", style="white")
        
        for g in groups[:15]: # Limit to 15 to keep it clean
            group_table.add_row(
                g.get("Group Name", "N/A"),
                g.get("Type", "N/A"),
                g.get("SID", "N/A"),
                g.get("Attributes", "N/A")
            )
        
        console.print(group_table)
        if len(groups) > 15:
            console.print(f"[dim]... and {len(groups) - 15} more groups.[/]")

    # 3. Privileges Section (Table)
    privs = data.get("privileges", [])
    if privs:
        priv_table = Table(title="User Privileges", show_lines=False, header_style="bold yellow", expand=True)
        priv_table.add_column("Privilege", style="yellow")
        priv_table.add_column("Description", style="white")
        priv_table.add_column("State", style="cyan")
        
        for p in privs:
            state = p.get("State", "Unknown")
            state_color = "green" if state.lower() == "enabled" else "red"
            priv_table.add_row(
                p.get("Privilege Name", "N/A"),
                p.get("Description", "N/A"),
                f"[{state_color}]{state}[/]"
            )
        
        console.print(priv_table)


def show_disk_free_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="💾 Disk Free Error", border_style="red"))
        return

    def to_gb(bytes_val):
        if not isinstance(bytes_val, int):
            return "N/A"
        return f"{bytes_val / (1024**3):.2f} GB"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan bold")
    table.add_column("Value", style="white")

    # Keys from fsutil: Total # of free bytes, Total # of bytes, Total # of avail free bytes
    free = data.get("Total # of free bytes", "N/A")
    total = data.get("Total # of bytes", "N/A")
    avail = data.get("Total # of avail free bytes", "N/A")

    table.add_row("📊 Total Space", to_gb(total))
    table.add_row("🔓 Free Space", to_gb(free))
    table.add_row("✅ Available Space", to_gb(avail))

    if isinstance(free, int) and isinstance(total, int):
        used_perc = ((total - free) / total) * 100
        table.add_row("📉 Usage Percentage", f"{used_perc:.1f}%")

    console.print(Panel(table, title="[bold white]C: Drive Disk Free (fsutil)[/bold white]", border_style="green", expand=False))


def show_event_logs_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="📜 Event Log Error", border_style="red"))
        return

    logs = data.get("logs", [])
    if not logs:
        console.print(Panel("No recent system event logs found.", title="📜 System Event Logs", border_style="blue"))
        return

    table = Table(title="Recent System Event Logs (Newest 10)", show_lines=False, header_style="bold magenta", expand=True)
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Type", style="bold", width=12)
    table.add_column("Source", style="green")
    table.add_column("Message", style="white")

    for log in logs:
        # PowerShell JSON dates look like "/Date(123456789)/" sometimes, 
        # but Select-Object usually gives a more readable string or we can parse it.
        # Let's assume a basic string representation from PowerShell.
        time_str = log.get("TimeGenerated", "N/A")
        # Clean up PowerShell date if it's in /Date(...)/ format
        if "/Date(" in str(time_str):
            time_str = "Recent" # Simple fallback for now
            
        entry_type = str(log.get("EntryType", "Info"))
        type_color = "blue"
        if "Error" in entry_type:
            type_color = "red"
        elif "Warning" in entry_type:
            type_color = "yellow"
        
        # Truncate long messages
        msg = log.get("Message", "N/A")
        if len(msg) > 100:
            msg = msg[:97] + "..."
            
        table.add_row(
            time_str,
            f"[{type_color}]{entry_type}[/]",
            log.get("Source", "N/A"),
            msg
        )

    console.print(Panel(table, title="[bold white]Windows System logs[/bold white]", border_style="blue", expand=False))


def show_apps_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="📦 Application List Error", border_style="red"))
        return

    apps = data.get("apps", [])
    if not apps:
        console.print(Panel("No installed applications found via Winget.", title="📦 Installed Applications", border_style="blue"))
        return

    table = Table(title=f"Installed Applications (Showing {len(apps)})", show_lines=False, header_style="bold green", expand=True)
    table.add_column("Application Name", style="cyan")
    table.add_column("ID", style="dim")
    table.add_column("Version", style="white")
    table.add_column("Available", style="yellow")

    for app in apps:
        table.add_row(
            app.get("name", "N/A"),
            app.get("id", "N/A"),
            app.get("version", "N/A"),
            app.get("available", "N/A")
        )

    console.print(Panel(table, title="[bold white]Installed Software (Winget)[/bold white]", border_style="green", expand=False))


def show_wmic_software_ui(data: dict):
    if not data.get("success"):
        console.print(Panel(f"[bold red]Error:[/] {data.get('error', 'Unknown error')}", title="📦 WMIC Software Error", border_style="red"))
        return

    software = data.get("software", [])
    if not software:
        console.print(Panel("No installed software found via WMIC.", title="📦 Installed Software (WMIC)", border_style="blue"))
        return

    table = Table(title=f"Installed Software (Showing {len(software)})", show_lines=False, header_style="bold green", expand=True)
    table.add_column("Software Name", style="cyan")
    table.add_column("Version", style="white")

    for s in software:
        table.add_row(
            s.get("name", "N/A"),
            s.get("version", "N/A")
        )

    console.print(Panel(table, title="[bold white]Installed Software (WMIC)[/bold white]", border_style="blue", expand=False))


def show_process_kill_ui(data: dict):
    target = data.get("target", "N/A")
    success = data.get("success", False)
    output = data.get("data", "No output available.")
    
    color = "green" if success else "red"
    status_text = "SUCCESS" if success else "FAILED"
    title = f"💀 Process Termination Attempt ({target}): {status_text}"
    
    console.print(Panel(output.strip(), title=title, border_style=color))
