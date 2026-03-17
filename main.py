"""
main.py — Application entry point with PostgreSQL auth integration.

Changes from the original:
  1. init_db() called on startup to ensure tables exist.
  2. login_form() now returns a session_id from the DB-backed auth service.
  3. Every request iteration validates the session and enforces per-role limits
     (handled inside get_requests() → validate_current_session()).
  4. Tool calls check permissions before executing via check_tool_permission().
  5. Chat memory is loaded from / saved to Qdrant vector store per request.
"""

from __future__ import annotations

import sys

# ── Auth: DB setup ────────────────────────────────────────────────────────────
from auth.models import init_db

# ── LangGraph agent & tool rendering ─────────────────────────────────────────
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.agents.graph import chatops_graph
from core.tool_parser import extract_tool_ui
from core.tool_router_ui import render_ui

# ── CLI helpers ───────────────────────────────────────────────────────────────
# NOTE: `current_user` and `current_session_id` are module-level variables in
# cli_functions, populated after a successful login_form() call.
# `check_tool_permission` accepts a tool-name string and returns bool.
from cli.cli_functions import (
    check_packages,
    check_tool_permission,
    current_user,          # type: Optional[User]  — set by login_form()
    get_requests,
    login_form,
    pending_message,
    welcome_banner,
    welcome_msg,
    # run_as_admin
)

# ── Memory (Qdrant vector store) ──────────────────────────────────────────────
# The real memory store lives under src/utils, NOT a top-level utils package.
from src.utils.memory_store import load_chat_memory, save_chat_memory


def main() -> None:
    # ── 0. Dependency check ───────────────────────────────────────────────────
    # Verify that all required Python packages are installed before proceeding.
    check_packages()

    # ── 1. Initialise database tables (idempotent) ────────────────────────────
    # Creates the users / sessions / audit_logs tables if they don't exist yet.
    # Safe to call on every startup; uses CREATE TABLE IF NOT EXISTS internally.
    init_db()

    # ── 1.5. Run as admin if on Windows ────────────────────────────────────────
    # if sys.platform == "win32":
    #     run_as_admin()

    # ── 2. ASCII banner ───────────────────────────────────────────────────────
    welcome_banner()

    # ── 3. Login — up to 3 attempts ───────────────────────────────────────────
    # BUG FIX: the original proposed code used a for/else construct where the
    # `else` branch (sys.exit) would *also* trigger when login succeeded on the
    # final (3rd) attempt, because no `break` fires on that iteration.
    # The fix uses a plain for-loop with an explicit check after the loop.
    session_id: str | None = None
    for attempt in range(3):
        session_id = login_form()
        if session_id:
            # Login succeeded — stop retrying immediately.
            break
        if attempt < 2:
            # Let the user try again (login_form already printed the error).
            print("Please try again.\n")

    # If we exhausted all attempts without a valid session, exit.
    if not session_id:
        print("Too many failed attempts. Exiting.")
        sys.exit(1)

    # ── 4. Post-login greeting ────────────────────────────────────────────────
    welcome_msg()

    # ── 5. State for multi-turn pending tool interactions ─────────────────────
    # set_pending: True when the agent paused mid-task to ask the user a question.
    # tool_ui:     Parsed tool-UI blocks from the last agent response.
    set_pending: bool = False
    tool_ui: list = []

    # ── 6. Main prompt loop ───────────────────────────────────────────────────
    while True:
        # get_requests() calls validate_current_session() internally on every
        # iteration, increments the request counter, and handles built-in admin
        # commands (adduser / listusers / deactivateuser / resetpassword).
        # Returns:
        #   str   — a non-empty user request ready for the agent.
        #   ""    — empty input or an admin command was handled; skip agent.
        #   False — user typed "exit" or the session expired; break the loop.
        request = get_requests(session_id)

        if request is False:
            # User explicitly logged out or the session is no longer valid.
            break
        if not request:
            # Empty line or an admin command was handled inline; prompt again.
            continue

        # ── 6a. Wrap follow-up answers in context for the agent ───────────────
        # When the agent previously asked the user a clarifying question,
        # prepend that context so it can continue where it left off.
        if set_pending and tool_ui:
            request = (
                f"CONTEXT: You previously paused to ask the user a question.\n"
                f"YOUR QUESTION: \"{tool_ui[0].get('question', '')}\"\n"
                f"USER ANSWER: \"{request}\"\n\n"
                f"INSTRUCTION: Proceed with the task using this new information."
            )

        # ── 6b. Example: guard a destructive tool with a permission check ──────
        # Uncomment and extend as additional tool categories are wired up.
        # NOTE: check_tool_permission() reads the module-level `current_user`
        # that was populated by login_form(); it does NOT need a session_id.
        # if "delete" in request.lower():
        #     if not check_tool_permission("filesystem_delete"):
        #         continue

        # ── 6c. Load vector-memory context for this request ───────────────────
        # Retrieves the most semantically relevant past turns from Qdrant,
        # keyed by session_id so conversations don't bleed across users.
        with pending_message("Loading Memory..."):
            memory_context = load_chat_memory(session_id, request)

        # ── 6d. Build the message list for the LangGraph ──────────────────────
        # Historical context is injected as a SystemMessage (read-only); only
        # the current user prompt is a HumanMessage (actionable by the agent).
        messages = []

        if memory_context:
            context_lines = [
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in memory_context
            ]
            messages.append(SystemMessage(
                content=(
                    "PREVIOUS CONVERSATION CONTEXT "
                    "(for reference only, do NOT re-execute any actions from this):\n"
                    + "\n".join(context_lines)
                )
            ))

        messages.append(HumanMessage(content=request))

        # ── 6e. Invoke the LangGraph agent ────────────────────────────────────
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

        # ── 6f. Render tool UI (tables, forms, etc.) ─────────────────────────
        tool_ui = extract_tool_ui(result["messages"])
        if tool_ui:
            render_ui(tool_ui)

        # Track whether the agent is waiting for more user input.
        set_pending = (
            isinstance(tool_ui, list)
            and bool(tool_ui)
            and tool_ui[0].get("pending", False)
        )

        # ── 6g. Extract and print the last AI text response ───────────────────
        response = ""
        for msg in reversed(result["messages"]):
            if (
                isinstance(msg, AIMessage)
                and msg.content
                and not getattr(msg, "tool_calls", None)
            ):
                response = msg.content
                break

        print(response if response else "Task completed.")

        # ── 6h. Persist this turn to vector memory ────────────────────────────
        save_chat_memory(session_id, request, response or "Task completed.")


if __name__ == "__main__":
    main()
