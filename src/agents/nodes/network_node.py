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
)
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a helpful network operations assistant. "
    "Use the provided tools to perform network diagnostics. "
    "Always run the tool — never guess results from previous executions."
)

_TOOLS = [
    ping, traceroute, get_ip_address,
    show_ipconfig, get_default_gateway, tcp_port_check,
]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def network_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the network ReAct agent with clean message context."""
    from cli.reasoning_ui import show_agent_start, show_agent_result

    show_agent_start("network")
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
