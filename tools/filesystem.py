from langchain.tools import tool
from utils.execution_log import log_execution
import os
import platform
import stat
from typing import Dict, Any

if platform.system().lower() != "windows":
    import pwd
    import grp



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
def change_dir(dir_name: str) -> str:
    """ change the current working directory """
    try:
        os.chdir(dir_name)
        print("Directory changed successfully")
    except FileNotFoundError:
        print(f"Directory {dir_name} not found")
    return f"changed directory to {dir_name}"

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