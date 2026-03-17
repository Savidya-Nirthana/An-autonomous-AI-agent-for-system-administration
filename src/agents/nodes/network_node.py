"""
Network agent node — handles ping, traceroute, IP, port checks.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.network import (
    ping, traceroute, get_ip_address, show_ipconfig,
    get_default_gateway, tcp_port_check,
    show_ip_mac_details, show_arp_cache, show_active_ports, dns_lookup, show_routing_table, show_wifi_interfaces, set_static_ip, set_static_dns, check_netbios_table, get_network_adapters, test_net_connection
)
from src.agents.tools.network_fix import ipconfig_release, ipconfig_renew, ipconfig_flush_dns, winsock_reset, tcp_ip_reset
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a helpful network operations assistant. "
    "Use the provided tools to perform network diagnostics. "
    "Always run the tool — never guess results from previous executions.\n\n"
    "### CONCISENESS PROTOCOL ###\n"
    "1. When a tool displays data in a UI table (e.g., ports, ARP, routing), DO NOT repeat or summarize the data in your response.\n"
    "Simply acknowledge that the data is displayed and ask if the user needs anything else.\n"
    "3. Keep your chat responses to a single, brief sentence.\n\n"
    "4. You can configure static IP and DNS addresses using the set_static_ip and set_static_dns tools.\n\n"
    "If the user asks for system monitoring (CPU, memory, disk, processes, drivers, or system info), "
    "politely state that you specialize in network tasks and suggest using the monitoring tools."
)

_TOOLS = [
    ping, traceroute, get_ip_address,
    show_ipconfig, get_default_gateway, tcp_port_check,
    show_ip_mac_details, show_arp_cache,
    show_active_ports, dns_lookup, show_routing_table,
    show_wifi_interfaces, ipconfig_release, ipconfig_renew, ipconfig_flush_dns,
    winsock_reset, tcp_ip_reset, set_static_ip, set_static_dns, check_netbios_table, get_network_adapters, test_net_connection
]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def network_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the network ReAct agent with clean message context."""
    from cli.reasoning_ui import show_agent_start, show_agent_result, stop_reasoning

    show_agent_start("network")
    stop_reasoning()
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    if response:
        show_agent_result("network", response)

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["network"],
        "task_context": {"network_result": response} if response else {},
    }
