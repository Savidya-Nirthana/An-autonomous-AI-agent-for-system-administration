"""
Usage monitoring agent node — CPU, memory, disk.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.usagemonitoring import cpu_usage, memory_usage, disk_usage
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a system monitoring assistant. "
    "Use the provided tools to check CPU, memory, and disk usage. "
    "Always run the tools to get fresh data — never reuse previous results."
)

_TOOLS = [cpu_usage, memory_usage, disk_usage]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def monitoring_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the monitoring ReAct agent with clean message context."""
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["monitoring"],
        "task_context": {"monitoring_result": response} if response else {},
    }
