from langchain.tools import tool
from utils.execution_log import log_execution
import os


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
    """ create a file with the given name and content """
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
def list_dir(path: str = None) -> str:
    """ list the contents of the directory """
    try:
        return os.listdir(path)
    except Exception as e:
        print(f"Error listing directory: {e}")
    return os.listdir(path)