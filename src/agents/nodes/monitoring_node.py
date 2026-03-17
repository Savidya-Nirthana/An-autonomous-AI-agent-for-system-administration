"""
Usage monitoring agent node — CPU, memory, disk.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.usagemonitoring import (
    cpu_usage,
    memory_usage,
    disk_usage,
    list_running_processes,
    system_info,
    list_drivers,
    user_info,
    check_disk_free,
    get_event_logs,
    list_apps,
    list_wmic_software,
    kill_process_by_pid,
    kill_process_by_name,
)
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a system monitoring assistant. "
    "Use the provided tools to check CPU, memory, disk usage, and running processes. "
    "Always run the tools to get fresh data — never reuse previous results.\n\n"
    "Tool guide:\n"
    "- cpu_usage              → CPU percentage (basic or full/per-core)\n"
    "- memory_usage           → RAM usage percentage\n"
    "- disk_usage             → Disk usage percentage\n"
    "- list_running_processes → All running processes sorted by memory usage\n"
    "- system_info            → OS version, uptime, BIOS, hotfixes (Windows)\n"
    "- list_drivers           → List installed drivers (Windows)\n"
    "- user_info              → Detailed current user info (identity, groups, privileges) (Windows)\n"
    "- check_disk_free        → Detailed free space on C: drive (Windows)\n"
    "- get_event_logs         → Read newest 10 system event logs (Windows)\n"
    "- list_apps             → List installed applications via Winget (Windows)\n"
    "- list_wmic_software    → List installed software (legacy/MSI) via WMIC (Windows)\n"
    "- kill_process_by_pid   → Forcefully terminate a process by PID (Windows)\n"
    "- kill_process_by_name  → Forcefully terminate a process by name (Windows)\n\n"
    "IMPORTANT: After calling a tool, provide a VERY brief one-line summary (e.g., 'Retrieved user information.') and STOP. "
    "The full data is already displayed in the visual UI. Do NOT repeat or summarize the actual data (names, IDs, lists) in your response."
)

_TOOLS = [cpu_usage, memory_usage, disk_usage, list_running_processes, system_info, list_drivers, user_info, check_disk_free, get_event_logs, list_apps, list_wmic_software, kill_process_by_pid, kill_process_by_name]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def monitoring_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the monitoring ReAct agent with clean message context."""
    from cli.reasoning_ui import show_agent_start, show_agent_result

    show_agent_start("monitoring")
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    if response:
        show_agent_result("monitoring", response)

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["monitoring"],
        "task_context": {"monitoring_result": response} if response else {},
    }
