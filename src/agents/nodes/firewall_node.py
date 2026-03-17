"""
Firewall & Security agent node.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.firewallandsecurity import firewall_status
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a security operations assistant. "
    "Use the provided tools to inspect firewall and security settings."
)

_TOOLS = [firewall_status]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def firewall_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the firewall ReAct agent with clean message context."""
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["firewall"],
        "task_context": {"firewall_result": response} if response else {},
    }
