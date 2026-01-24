from langchain.tools import tool
from utils.delete_state import store_delete_request, get_delete_request, clear_delete_request
from pathlib import Path
import os, shutil, time, platform
from langchain_core.runnables import RunnableConfig


SYSTEM = platform.system().lower()

if SYSTEM == "windows":
    ALLOWED_ROOTS = [
        Path(r"D:\ai\ChatOps\var\app\uploads").resolve(),
    ]
else:
    ALLOWED_ROOTS = [
        Path("/var/app/uploads").resolve(),
        Path("/opt/app/data").resolve(),
    ]

if SYSTEM == "windows":
    APP_ROOT = Path(r"D:\ai\ChatOps\var\app")
else:
    APP_ROOT = Path("/var/app")

TRASH_DIR = (APP_ROOT / ".trash").resolve()


def is_safe_path(path: Path) -> bool:
    real = path.resolve()
    return any(real.is_relative_to(root) for root in ALLOWED_ROOTS)


@tool
def delete_file_request(path: str, config: RunnableConfig):
    """
    Request deletion of a file (dry-run only).
    Does NOT delete anything. 
    """
    session_id = config["configurable"].get("session_id")
    p = Path(path).expanduser()

    if not p.exists():
        return {"success": False, "error": "File not found", "ui_type": "delete"}

    if not p.is_file():
        return {"success": False, "error": "Not a file", "ui_type": "delete"}

    if not is_safe_path(p):
        return {"success": False, "error": "Path not allowed", "ui_type": "delete"}

    store_delete_request(session_id, str(p))

    return {
        "success": True,
        "message": "⚠️ Delete confirmation required",
        "file": str(p),
        "size": p.stat().st_size,
        "confirm_with": f"CONFIRM DELETE {p}",
        "ui_type": "delete_preview"
    }


@tool
def delete_file_confirm(confirmation: str, config: RunnableConfig):
    """
    Confirmation deletion of a file.
    when confirm with is CONFIRM DELETE /var/app/uploads/new.txt
    """
    session_id = config["configurable"].get("session_id")
    path = get_delete_request(session_id)

    if not path:
        return {"success": False, "error": "No pending delete request", "ui_type": "delete"}

    expected = f"CONFIRM DELETE {path}"

    if confirmation.strip() != expected:
        return {"success": False, "error": "Confirmation mismatch", "ui_type": "delete"}

    p = Path(path)

    TRASH_DIR.mkdir(exist_ok=True)
    trash_path = TRASH_DIR / f"{p.name}.{int(time.time())}"

    shutil.move(str(p), trash_path)
    clear_delete_request(session_id)

    return {
        "success": True,
        "message": "✅ File deleted safely (soft delete)",
        "original": path,
        "trash": str(trash_path),
        "ui_type": "delete_done"
    }
