import paths
from dotenv import load_dotenv

from cli.setup import run_first_time_setup
run_first_time_setup()

paths.USER_DATA_DIR = paths.get_user_data_dir()
paths.ENV_FILE = paths.USER_DATA_DIR / ".env"
paths.QDRANT_DATA_DIR = paths.USER_DATA_DIR / "qdrant_data"
paths.EXECUTIONS_DIR = paths.USER_DATA_DIR / "executions"

load_dotenv(dotenv_path=str(paths.ENV_FILE))

import os
os.chdir(os.path.expanduser("~"))

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.agents.graph import chatops_graph
from src.utils.memory_store import save_chat_memory, load_chat_memory
from core.tool_parser import extract_tool_ui
from core.tool_router_ui import render_ui

from cli.cli_functions import (
    welcome_banner,
    login_form,
    welcome_msg,
    get_requests,
    pending_message,
)
from cli.reasoning_ui import reset_steps, show_final_response, show_execution_time
import time

welcome_banner()
session_id = login_form()

if not session_id:
    exit()

welcome_msg()


set_pending = False
tool_ui = {}

while True:
    prompt = get_requests(session_id)

    if prompt == "":
        print("Please enter a valid request")
        continue
    elif not prompt:
        break

    start_time = time.time()

    if set_pending:
        prompt = (
            f'CONTEXT: You previously paused to ask the user a question.\n'
            f'YOUR QUESTION: "{tool_ui[0].get("question", "")}"\n'
            f'USER ANSWER: "{prompt}"\n\n'
            f'INSTRUCTION: Proceed with the task using this new information.'
        )

    with pending_message("Loading Memory..."):
        memory_context = load_chat_memory(session_id, prompt)

    messages = []

    if memory_context:
        context_lines = []
        for msg in memory_context:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            context_lines.append(f"{role}: {content}")
        context_text = "\n".join(context_lines)
        messages.append(SystemMessage(
            content=f"PREVIOUS CONVERSATION CONTEXT (for reference only, do NOT re-execute any actions from this):\n{context_text}"
        ))

    messages.append(HumanMessage(content=prompt))

    reset_steps()

    result = chatops_graph.invoke(
        {
            "messages": messages,
            "next_agent": "",
            "task_context": {},
            "pending_approvals": [],
            "error": None,
            "visited": [],
            "metadata": {"session_id": session_id},
        },
        config={
            "configurable": {"session_id": session_id},
            "recursion_limit": 25,
        },
    )

    tool_ui = extract_tool_ui(result["messages"])

    if tool_ui:
        render_ui(tool_ui)

    if isinstance(tool_ui, list) and tool_ui:
        set_pending = tool_ui[0].get("pending", False)
    else:
        set_pending = False

    response = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
            response = msg.content
            break

    if response:
        show_final_response(response)
    else:
        show_final_response("Task completed.")

    total_time = time.time() - start_time
    show_execution_time(total_time)

    save_chat_memory(session_id, prompt, response or "Task completed.")

