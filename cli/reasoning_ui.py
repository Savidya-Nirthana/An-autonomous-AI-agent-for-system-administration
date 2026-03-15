"""
Reasoning UI - Minimal, subtle step display for agent operations.

Shows the thinking process in a dim, unobtrusive way.
The thinking is NOT the output — it's just context.
"""

from rich.console import Console
import time

console = Console()

# ── Agent labels ─────────────────────────────────────────────────────
AGENT_LABELS = {
    "supervisor": "Supervisor",
    "filesystem": "Filesystem",
    "network":    "Network",
    "firewall":   "Firewall",
    "monitoring": "Monitoring",
    "admin":      "Admin",
    "FINISH":     "Done",
}

# ── Step counter ─────────────────────────────────────────────────────
_step_counter = 0

def reset_steps():
    global _step_counter
    _step_counter = 0

def _next_step():
    global _step_counter
    _step_counter += 1
    return _step_counter


def show_routing_decision(agent: str, reason: str):
    """Show which agent was selected and why — dim and subtle."""
    step = _next_step()
    label = AGENT_LABELS.get(agent, agent)
    console.print(f"  [dim]{step}.[/dim] [dim italic]thinking...[/dim italic] [dim]-> {label}:[/dim] [dim italic]{reason}[/dim italic]")


_agent_start_times = {}

def show_agent_start(agent_name: str):
    """Show that an agent started working — minimal."""
    _agent_start_times[agent_name] = time.time()
    label = AGENT_LABELS.get(agent_name, agent_name)
    console.print(f"     [dim]> {label} is working...[/dim]")


def show_agent_result(agent_name: str, result_summary: str):
    """Show agent result — keep it short and dim."""
    duration_str = ""
    if agent_name in _agent_start_times:
        elapsed = time.time() - _agent_start_times.pop(agent_name)
        duration_str = f" [{elapsed:.2f}s]"

    label = AGENT_LABELS.get(agent_name, agent_name)
    # Truncate long results
    short = result_summary if len(result_summary) <= 120 else result_summary[:120] + "..."
    console.print(f"     [dim]> {label} done{duration_str}:[/dim] [dim italic]{short}[/dim italic]")


def show_finish():
    """Show completion — simple checkmark."""
    step = _next_step()
    console.print(f"  [dim]{step}.[/dim] [dim]done[/dim]")


def show_error(message: str):
    """Show an error."""
    console.print(f"  [red]error: {message}[/red]")


def show_final_response(response: str):
    """Show the final AI response — this IS the output, so it's normal text."""
    console.print(f"\n{response}\n")

def show_execution_time(seconds: float):
    """Show the overall execution time for the user's prompt."""
    console.print(f"  [dim italic]⏱️ Total execution time: {seconds:.2f}s[/dim italic]\n")
