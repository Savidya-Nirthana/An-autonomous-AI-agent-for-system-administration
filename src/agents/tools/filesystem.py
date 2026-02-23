from langchain.tools import tool
from utils.execution_log import log_execution
import os
import platform
import stat
from typing import Dict, Any
from pathlib import Path
from langchain_core.runnables import RunnableConfig

if platform.system().lower() != "windows":
    import pwd
    import grp


WORKING_STATE = {
    "cwd": Path.cwd()
}


@tool
def make_dir(dir_name: str) -> str:
    """  create a folder with the given name """
    try:
        os.mkdir(dir_name)
        print(os.listdir())
        print("Directory created successfully")
    except FileExistsError:
        print(f"Directory {dir_name} already exists")
    except Exception as e:
        print(f"Error creating directory: {e}")
    # log_execution(session_id, "make_dir", {"dir_name": dir_name, "path": path})
    return f"created directory {dir_name}"


@tool
def create_file(file_name: str, content: str) -> str:
    """ create a file and write the content to it tool

        args:
            file_name (str): name of the file
            content (str): content of the file
    
    """
    try:
        with open(file_name, "w") as f:
            f.write(content)
        print("File created successfully")
    except Exception as e:
        print(f"Error creating file: {e}")
    return f"created file {file_name}"


@tool
def change_dir(path: str)-> str:
    """ 
    Change the working directory (cross-platform)
    Support absolute, relateve, ~, Windows & unix paths.
    Persists across agent tools
    """

    try:
        resolved_path = Path(path).expanduser()

        if not resolved_path.is_absolute():
            resolved_path = (WORKING_STATE["cwd"] / resolved_path).resolve()

        if not resolved_path.exists():
            return {
                "path" : f"❌ Directory not found: {resolved_path}",
                "success" : False,
                "ui_type" : "change_dir"
                }

        if not resolved_path.is_dir():
            return {
                "path" : f"❌ Path is not a directory: {resolved_path}",
                "success" : False,
                "ui_type" : "change_dir"
                }

        os.chdir(resolved_path)
        WORKING_STATE["cwd"] = resolved_path

        return {
            "path" : f"✅ Current directory: {resolved_path}",
            "success" : True,
            "ui_type" : "change_dir"
            }

    except PermissionError:
        return {
            "path" : f"❌ Permission denied: {resolved_path}",
            "success" : False,
            "ui_type" : "change_dir"
            }
    except Exception as e:
        return {
            "path" : f"❌ Error: {str(e)}",
            "success" : False,
            "ui_type" : "change_dir"
            }


@tool
def list_dir(path: str = ".", view: str = "simple") -> Dict[str, Any]:
    """
    List directory contents.

    view:
    - simple   → only files & directories
    - detailed → permissions, owner, group, size

    please don't show the result from previous list_dir command. always show the result of current list_dir command.
    """
    system = platform.system().lower()
    entries = []

    try:
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            info = os.stat(full_path)

            is_dir = stat.S_ISDIR(info.st_mode)

            if view == "simple":
                entries.append({
                    "name": name,
                    "type": "dir" if is_dir else "file",
                })

            else:
                entry = {
                    "name": name,
                    "type": "dir" if is_dir else "file",
                    "size": info.st_size,
                    "permissions": stat.filemode(info.st_mode),
                }

                if system != "windows":
                    entry["owner"] = pwd.getpwuid(info.st_uid).pw_name
                    entry["group"] = grp.getgrgid(info.st_gid).gr_name
                else:
                    entry["owner"] = "N/A"
                    entry["group"] = "N/A"

                entries.append(entry)

        return {
            "success": True,
            "path": os.path.abspath(path),
            "view": view,
            "entries": entries,
            "ui_type": "list_dir"
        }

    except Exception as e:
        return {
            "success": False,
            "path": path,
            "error": str(e),
            "ui_type": "list_dir"
        }


@tool
def pending_manage(question: str, config: RunnableConfig):
    """
    Call this tool when you need more information from the user.
    
    args:
        question (str): The question to ask the user (e.g., "What should I name the folder?")
        session_id (str): The session id of the user
    """
    session_id = config["configurable"].get("session_id")
    print("pending_manage tool called")
    # print(question)
    return {
        "success": True,
        "ui_type": "pending_manage",
        "pending" : True,
        "session_id" : session_id,
        "question" : question
    }
    