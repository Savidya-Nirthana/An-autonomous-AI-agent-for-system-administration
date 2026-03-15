"""
Direct command execution node.
Runs simple shell commands without calling an LLM.
"""

import subprocess
from langchain_core.messages import AIMessage
from src.agents.state import AgentState
from src.agents.tools.filesystem import change_dir, WORKING_STATE


def cmd_node(state: AgentState) -> dict:
    """
    Directly execute command line operations without LLM overhead.
    """
    from cli.reasoning_ui import show_agent_start, show_agent_result

    show_agent_start("cmd")
    messages = state.get("messages", [])
    
    if not messages:
        return {"next_agent": "FINISH"}

    user_input = messages[-1].content.strip()
    result_text = ""

    # Special handling for 'cd' which must change the process's working directory
    if user_input.startswith("cd ") or user_input == "cd":
        path = user_input[3:].strip()
        if not path:
            path = "."
            
        res = change_dir.invoke({"path": path})
        if res.get("success"):
            result_text = res.get("path", "")
        else:
            result_text = res.get("path", "Failed to change directory")
    else:
        # Standard subprocess execution
        try:
            # We run in shell=True to support commands like 'dir', 'ls', and pipes if given.
            # We use WORKING_STATE["cwd"] from filesystem tools to persist state.
            process = subprocess.run(
                user_input, 
                shell=True, 
                cwd=WORKING_STATE["cwd"], 
                capture_output=True, 
                text=True
            )
            
            # Combine stdout and stderr if it fails, or just stdout
            if process.returncode == 0:
                result_text = process.stdout.strip() if process.stdout else "Command executed successfully (no output)."
            else:
                out = process.stdout.strip()
                err = process.stderr.strip()
                result_text = f"Command failed with code {process.returncode}.\nSTDOUT: {out}\nSTDERR: {err}"
                
        except Exception as e:
            result_text = f"Error executing command: {e}"

    show_agent_result("cmd", result_text)

    # We append the result as an AIMessage so it appears in the conversation history
    new_messages = messages + [AIMessage(content=result_text)]
    
    return {
        "messages": new_messages,
        "visited": state.get("visited", []) + ["cmd"],
        "task_context": {"cmd_result": result_text},
        "next_agent": "FINISH"
    }
