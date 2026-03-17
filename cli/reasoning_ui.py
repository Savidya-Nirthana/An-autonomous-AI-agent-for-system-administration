"""
Reasoning UI - Minimal, subtle step display for agent operations.

Shows the thinking process in a dim, unobtrusive way.
The thinking is NOT the output — it's just context, and it disappears when done.
"""

from rich.console import Console, Group
from rich.live import Live
from rich.text import Text
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

# ── Transient Display State ──────────────────────────────────────────
_step_counter = 0
_live = None
_renderables = []
_agent_start_times = {}

def _ensure_live():
    """Ensure the Live display is running."""
    global _live, _renderables
    if _live is None:
        _renderables = []
        _live = Live(Group(*_renderables), console=console, transient=True, refresh_per_second=10)
        _live.start()

def _add_renderable(markup_str: str):
    """Add a new line to the transient display."""
    global _renderables, _live
    _ensure_live()
    _renderables.append(Text.from_markup(markup_str))
    _live.update(Group(*_renderables))

def stop_reasoning():
    """Stop the transient display, clearing all thinking lines from the screen."""
    global _live, _renderables, _step_counter, _agent_start_times
    if _live is not None:
        _live.stop()
        _live = None
        _renderables = []
        _step_counter = 0
        _agent_start_times = {}

def reset_steps():
    stop_reasoning()

def _next_step():
    global _step_counter
    _step_counter += 1
    return _step_counter

# ── Reasoning Output Functions ───────────────────────────────────────

def show_routing_decision(agent: str, reason: str):
    """Show which agent was selected and why — dim and subtle."""
    step = _next_step()
    label = AGENT_LABELS.get(agent, agent)
    _add_renderable(f"  [dim]{step}.[/dim] [dim italic]thinking...[/dim italic] [dim]-> {label}:[/dim] [dim italic]{reason}[/dim italic]")

def show_agent_start(agent_name: str):
    """Show that an agent started working — minimal."""
    _agent_start_times[agent_name] = time.time()
    label = AGENT_LABELS.get(agent_name, agent_name)
    _add_renderable(f"     [dim]> {label} is working...[/dim]")

def show_agent_result(agent_name: str, result_summary: str):
    """Show agent result — keep it short and dim."""
    duration_str = ""
    if agent_name in _agent_start_times:
        elapsed = time.time() - _agent_start_times.pop(agent_name)
        duration_str = f" [{elapsed:.2f}s]"

    label = AGENT_LABELS.get(agent_name, agent_name)
    result_summary = str(result_summary)
    short = result_summary if len(result_summary) <= 120 else result_summary[:120] + "..."
    _add_renderable(f"     [dim]> {label} done{duration_str}:[/dim] [dim italic]{short}[/dim italic]")

def show_finish():
    """Show completion — simple checkmark."""
    step = _next_step()
    _add_renderable(f"  [dim]{step}.[/dim] [dim]done[/dim]")

def show_error(message: str):
    """Show an error."""
    _add_renderable(f"  [red]error: {message}[/red]")

# ── Final Output Functions ───────────────────────────────────────────

def show_final_response(response: str):
    """Show the final AI response — this IS the output, so it's normal text."""
    stop_reasoning()
    console.print(f"\n{response}\n")

def show_stream_token(token: str):
    """Print an individual token to the console as it arrives."""
    console.print(token, end="", markup=False)

def show_execution_time(seconds: float):
    """Show the overall execution time for the user's prompt."""
    console.print(f"\n  [dim italic]⏱️ Total execution time: {seconds:.2f}s[/dim italic]\n")
