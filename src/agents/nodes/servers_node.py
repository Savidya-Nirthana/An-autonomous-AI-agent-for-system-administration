"""
Servers agent node — handles SSH file sharing and remote server operations.
"""

from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from src.agents.state import AgentState
from src.infrastructure.llm import get_chat_llm
from src.agents.tools.servers import (
    webserver,
    ssh_connect_password,
    ssh_disconnect,
    ssh_execute_command,
    # ssh_upload_file_password,
    # ssh_upload_file_rsa,
    # ssh_download_file_password,
    # ssh_download_file_rsa,
    # ssh_execute_command_password,
    # ssh_execute_command_rsa,
)
from .helpers import build_agent_messages, extract_final_response


_SYSTEM_PROMPT = (
    "You are a helpful server operations assistant. "
    "Use the provided tools to perform SSH remote operations such as "
    "connecting to remote servers, uploading files, downloading files, "
    "and executing commands on remote servers. "
    "You support two authentication methods: username/password and RSA private key. "
    "Always ask the user which authentication method they prefer if not specified. "
    "Always run the tool — never guess results from previous executions."
)

_TOOLS = [
    webserver,
    ssh_connect_password,
    ssh_disconnect,
    ssh_execute_command,
    # ssh_upload_file_password,
    # ssh_upload_file_rsa,
    # ssh_download_file_password,
    # ssh_download_file_rsa,
    # ssh_execute_command_password,
    # ssh_execute_command_rsa,
]

_agent = create_react_agent(
    model=get_chat_llm(),
    tools=_TOOLS,
    prompt=_SYSTEM_PROMPT,
)


def servers_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the servers ReAct agent with clean message context."""
    from cli.reasoning_ui import show_agent_start, show_agent_result

    show_agent_start("servers")
    clean_msgs = build_agent_messages(state["messages"], state.get("task_context", {}))
    result = _agent.invoke({"messages": clean_msgs}, config=config)
    response = extract_final_response(result["messages"])

    if response:
        show_agent_result("servers", response)

    return {
        "messages": result["messages"],
        "visited": state.get("visited", []) + ["servers"],
        "task_context": {"servers_result": response} if response else {},
    }
