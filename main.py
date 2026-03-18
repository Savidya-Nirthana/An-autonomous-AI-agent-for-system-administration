import paths
from dotenv import load_dotenv

from cli.setup import run_first_time_setup
run_first_time_setup()

paths.USER_DATA_DIR = paths.get_user_data_dir()
paths.ENV_FILE = paths.USER_DATA_DIR / ".env"
paths.QDRANT_DATA_DIR = paths.USER_DATA_DIR / "qdrant_data"
paths.EXECUTIONS_DIR = paths.USER_DATA_DIR / "executions"

load_dotenv(dotenv_path=str(paths.ENV_FILE))

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.agents.graph import chatops_graph
from src.utils.memory_store import save_chat_memory, load_chat_memory
from core.tool_parser import extract_tool_ui
from core.tool_router_ui import render_ui

import os
os.chdir(os.path.expanduser("~"))

from cli.cli_functions import (
    welcome_banner,
    login_form,
    welcome_msg,
    get_requests,
    pending_message,
)
from cli.reasoning_ui import reset_steps, show_final_response, show_stream_token, show_execution_time, stop_reasoning
import time
import asyncio

import argparse
from auth.models import Session as DBSession, User as DBUser, SessionLocal
import cli.cli_functions

parser = argparse.ArgumentParser()
parser.add_argument("--session_id", type=str, default=None, help="Resume an existing session")
args, unknown = parser.parse_known_args()

session_id = args.session_id

if not session_id:
    welcome_banner()
    session_id = login_form()
    
    if not session_id:
        exit()
else:
    # Resuming session from an elevated process restart
    db = SessionLocal()
    sess = db.query(DBSession).filter_by(session_id=session_id).first()
    if not sess:
        print("Invalid session ID for elevation resumption. Exiting.")
        exit()
    user = db.query(DBUser).filter_by(id=sess.user_id).first()
    db.expunge(user)
    db.close()
    
    cli.cli_functions.current_session_id = session_id
    cli.cli_functions.current_user = user

welcome_msg()


set_pending = False
tool_ui = {}

async def main_loop():
    global set_pending
    global tool_ui
    while True:
        prompt = await asyncio.to_thread(get_requests, session_id)

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

        response = ""
        llm_response = ""
        _streaming_started = False
        print("\n", end="")

        async for event in chatops_graph.astream_events(
            {
                "messages": messages,
                "next_agent": "",
                "task_context": {},
                "pending_approvals": [],
                "error": None,
                "visited": [],
                "metadata": {"session_id": session_id},
            },
            version="v1",
            config={
                "configurable": {"session_id": session_id},
                "recursion_limit": 25,
            },
        ):
            kind = event["event"]
            tags = event.get("tags", [])

            if kind == "on_chat_model_stream":
                # Skip streaming tokens from the supervisor/router LLM
                # (it emits JSON routing decisions, not human-readable text)
                is_supervisor = any("supervisor" in t for t in tags)
                if is_supervisor:
                    continue

                content = event["data"]["chunk"].content
                if content:
                    if not _streaming_started:
                        stop_reasoning()
                        _streaming_started = True
                    show_stream_token(str(content))
                    response += str(content)
            
            elif kind == "on_chain_end" and event["name"] == "LangGraph":
                result = event["data"]["output"]
                tool_ui = extract_tool_ui(result.get("messages", []))
                
                # Extract the final text response from the LLM
                for msg in reversed(result.get("messages", [])):
                    if isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
                        llm_response = msg.content
                        break

                if tool_ui:
                    stop_reasoning()
                    render_ui(tool_ui)

                if isinstance(tool_ui, list) and tool_ui:
                    set_pending = tool_ui[0].get("pending", False)
                else:
                    set_pending = False

        stop_reasoning()

        # Show the LLM's final response if it wasn't already streamed
        if llm_response and not _streaming_started:
            show_final_response(llm_response)
        elif not response and not llm_response:
            show_final_response("Task completed.")

        total_time = time.time() - start_time
        show_execution_time(total_time)

        save_chat_memory(session_id, prompt, response or llm_response or "Task completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
    except Exception as exc:
        import traceback
        print(f"\n[FATAL ERROR] {exc}")
        traceback.print_exc()
        input("\nPress Enter to exit...")
