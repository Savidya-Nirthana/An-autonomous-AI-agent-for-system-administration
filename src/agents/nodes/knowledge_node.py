"""
Knowledge agent node — answers general knowledge questions using the LLM's internal knowledge without needing external tools.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.agents.prompts.knowledge.knowledge_prompts import knowledge_system_prompt
from src.infrastructure.llm import get_chat_llm
from .helpers import build_agent_messages, extract_final_response


_agent = create_react_agent(
    model=get_chat_llm(),
    tools=[],
    prompt=knowledge_system_prompt,
)


def knowledge_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the knowledge agent with clean message context."""
    from cli.reasoning_ui import show_agent_start, show_agent_result

    show_agent_start("knowledge")
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    if response:
        show_agent_result("knowledge", response)

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["knowledge"],
        "task_context": {"knowledge_result": response} if response else {},
    }
