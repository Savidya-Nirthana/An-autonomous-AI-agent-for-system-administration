"""
Filesystem agent node — handles file/directory operations.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.agents.prompts.file_system.file_system import filesystem_prompt
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.filesystem import (
    make_dir, create_file, change_dir, list_dir, file_info, pending_manage, read_file, get_directory_tree, run_chkdsk, reset_permissions, take_ownership
)
from src.agents.tools.filesystem_delete import (
    delete_file_request, delete_file_confirm
)
from .helpers import build_agent_messages, extract_final_response


_TOOLS = [
    make_dir, create_file, change_dir, list_dir, file_info,
    delete_file_request, delete_file_confirm, pending_manage, read_file,
    get_directory_tree, run_chkdsk, reset_permissions, take_ownership
]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=filesystem_prompt,
)


def filesystem_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the filesystem ReAct agent with clean message context."""
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["filesystem"],
        "task_context": {"filesystem_result": response} if response else {},
    }
