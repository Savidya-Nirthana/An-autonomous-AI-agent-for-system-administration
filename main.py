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

#added by chrishmika to get admin access on start
from cli.take_admin_access import req_Admin_Access
req_Admin_Access()


welcome_banner()
session_id = login_form()

if not session_id:
    exit()

welcome_banner()
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

    # ── Handle follow-up from a pending question ─────────────
    if set_pending:
        prompt = (
            f'CONTEXT: You previously paused to ask the user a question.\n'
            f'YOUR QUESTION: "{tool_ui[0].get("question", "")}"\n'
            f'USER ANSWER: "{prompt}"\n\n'
            f'INSTRUCTION: Proceed with the task using this new information.'
        )

    # ── Load conversation memory ─────────────────────────────
    with pending_message("Loading Memory..."):
        memory_context = load_chat_memory(session_id, prompt)

    # ── Build messages list ──────────────────────────────────
    #  Memory goes as a SystemMessage (context only, not re-executable)
    #  Only the current prompt is a HumanMessage (actionable)
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

    # ── Invoke the LangGraph ─────────────────────────────────
    with pending_message("Thinking..."):
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

    # ── Extract tool UI data and render ──────────────────────
    tool_ui = extract_tool_ui(result["messages"])

    if tool_ui:
        render_ui(tool_ui)

    # ── Check for pending interactions ───────────────────────
    if isinstance(tool_ui, list) and tool_ui:
        set_pending = tool_ui[0].get("pending", False)
    else:
        set_pending = False

    # ── Print response and save to memory ────────────────────
    response = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
            response = msg.content
            break

    if response:
        print(response)
    else:
        print("Task completed.")

    save_chat_memory(session_id, prompt, response or "Task completed.")

