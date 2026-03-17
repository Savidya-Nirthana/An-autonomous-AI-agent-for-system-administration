"""
main.py — Application entry point with PostgreSQL auth integration.
"""

from __future__ import annotations

import sys
import argparse

from auth.models import init_db
from auth.models import SessionLocal

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.agents.graph import chatops_graph
from core.tool_parser import extract_tool_ui
from core.tool_router_ui import render_ui

import cli.cli_functions as cli_state
from cli.cli_functions import (
    check_packages,
    check_tool_permission,
    get_requests,
    login_form,
    pending_message,
    welcome_banner,
    welcome_msg,
    elevate_if_needed,
)

from src.utils.memory_store import load_chat_memory, save_chat_memory


def _restore_session(session_id: str) -> bool:
    """
    Restore module-level auth state from an existing session_id.
    Used when the elevated re-launch passes --session <id>.
    Returns True on success, False if the session is invalid/expired.
    """
    from auth import auth_service
    from auth.models import Session as DBSession, User as DBUser

    db = SessionLocal()
    try:
        user, error = auth_service.validate_session(session_id, db)
        if error or user is None:
            return False

        # Re-attach a detached copy so it's usable outside this session
        db.expunge(user)
        cli_state.current_user       = user
        cli_state.current_session_id = session_id
        return True
    finally:
        db.close()


def main() -> None:
    # ── 0. Dependency check ───────────────────────────────────────────────────
    check_packages()

    # ── 1. Initialise database tables ────────────────────────────────────────
    init_db()

    # ── 2. Parse CLI args (--session injected by elevated re-launch) ──────────
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--session", default=None,
                        help="Resume an existing session (used by UAC re-launch)")
    args, _ = parser.parse_known_args()

    # ── 3. ASCII banner ───────────────────────────────────────────────────────
    welcome_banner()

    # ── 4. Login or session restore ───────────────────────────────────────────
    session_id: str | None = None

    if args.session:
        # Elevated re-launch path: skip interactive login, restore from DB
        if _restore_session(args.session):
            session_id = args.session
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            Console().print(Panel(Text(
                f"✓ Elevated session restored for "
                f"[b]{cli_state.current_user.username}[/b]",
                justify="center", style="bold green"
            )))
        else:
            # Session expired between launch and restore — fall through to login
            Console().print(
                "[bold yellow]Session expired. Please log in again.[/bold yellow]"
            )

    if not session_id:
        # Normal first-launch path: interactive login, up to 3 attempts
        for attempt in range(3):
            session_id = login_form()
            if session_id:
                break
            if attempt < 2:
                print("Please try again.\n")

        if not session_id:
            print("Too many failed attempts. Exiting.")
            sys.exit(1)

        # ── 5. Elevate if role requires it (admin / root_admin) ───────────────
        # On Windows: triggers UAC → re-launches with --session <id> → exits here
        # On Linux:   exec sudo → replaces process → continues elevated
        # On user role: no-op
        elevate_if_needed(cli_state.current_user)

    # ── 6. Post-login greeting ────────────────────────────────────────────────
    welcome_msg()

    # ── 7. State for multi-turn pending tool interactions ─────────────────────
    set_pending: bool = False
    tool_ui: list = []

    # ── 8. Main prompt loop ───────────────────────────────────────────────────
    while True:
        request = get_requests(session_id)

        if request is False:
            break
        if not request:
            continue

        if set_pending and tool_ui:
            request = (
                f"CONTEXT: You previously paused to ask the user a question.\n"
                f"YOUR QUESTION: \"{tool_ui[0].get('question', '')}\"\n"
                f"USER ANSWER: \"{request}\"\n\n"
                f"INSTRUCTION: Proceed with the task using this new information."
            )

        with pending_message("Loading Memory..."):
            memory_context = load_chat_memory(session_id, request)

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

        tool_ui = extract_tool_ui(result["messages"])
        if tool_ui:
            render_ui(tool_ui)

        set_pending = (
            isinstance(tool_ui, list)
            and bool(tool_ui)
            and tool_ui[0].get("pending", False)
        )

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
        save_chat_memory(session_id, request, response or "Task completed.")


if __name__ == "__main__":
    main()