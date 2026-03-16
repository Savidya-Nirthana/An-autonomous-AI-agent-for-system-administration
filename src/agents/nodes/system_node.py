"""
System agent node — handles system operations.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.systemmanagement import (
    updatePackages, shutdown, restart, get_last_time_sync_details, sync_time, viewUPTime
)
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a helpful system operations assistant. "
    "Use the provided tools to perform system diagnostics. "
    "Always run the tool — never guess results from previous executions."
)

_TOOLS = [
     updatePackages, shutdown, restart, get_last_time_sync_details, sync_time, viewUPTime
]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def system_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the system ReAct agent with clean message context."""
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["system"],
        "task_context": {"system_result": response} if response else {},
    }
