"""
Admin agent node — memory-locked, no tools, answers from chat history only.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.agents.prompts.admin.admin_prompts import admin_system_prompt
from src.infrastructure.llm import get_chat_llm
from .helpers import build_agent_messages, extract_final_response


_agent = create_react_agent(
    model=get_chat_llm(),
    tools=[],
    prompt=admin_system_prompt,
)


def admin_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the admin agent with clean message context."""
    from cli.reasoning_ui import show_agent_start, show_agent_result

    show_agent_start("admin")
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    if response:
        show_agent_result("admin", response)

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["admin"],
        "task_context": {"admin_result": response} if response else {},
    }
