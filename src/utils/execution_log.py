from pathlib import Path
from typing import Dict
import json



LOG_DIR = Path("executions")
if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_execution(session_id: str, tool:str, payload: Dict):
    file = LOG_DIR / f"{session_id}.json"
    data = []
    if file.exists():
        data = json.load(file)
    data.append({"tool": tool, "payload": payload})

    with open(file, "w") as f:
        json.dump(data, f)




def load_execution_log(session_id: str):
    file = LOG_DIR / f"{session_id}.json"
    if not file.exists():
        return []
    with open(file, "r") as f:
        return json.load(f)


