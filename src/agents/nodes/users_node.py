"""
Users agent node — handles user management.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.usermanagement import (
    createNewUser, 
    changeUserPassword, 
    addUsersToGroup, 
    disableAccount, 
    enableAccount, 
    deleteUser, 
    createGroup,
    deleteGroup,
    listUsers,
    listGroups,
    listUsersByGroup
)
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a user management assistant for a system administration tool. "
    "You have tools to create/delete users, change passwords, manage groups, enable/disable accounts. "
    "IMPORTANT RULES:\n"
    "1. Always call the appropriate tool immediately — never refuse or say a parameter is incorrect.\n"
    "2. Group names and usernames are provided by the user — accept them as-is and pass them directly to the tool.\n"
    "3. Never guess or fabricate results. Always execute the tool and return the actual output.\n"
    "4. If a tool returns an error, report the exact error message to the user."
)

_TOOLS = [
    createNewUser, 
    changeUserPassword, 
    addUsersToGroup, 
    disableAccount, 
    enableAccount, 
    deleteUser, 
    createGroup,
    deleteGroup,
    listUsers,
    listGroups,
    listUsersByGroup
]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def users_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the users ReAct agent with clean message context."""
    from cli.reasoning_ui import show_agent_start, show_agent_result

    show_agent_start("users")
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    if response:
        show_agent_result("users", response)

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["users"],
        "task_context": {"users_result": response} if response else {},
    }
