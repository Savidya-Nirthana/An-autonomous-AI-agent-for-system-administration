from pathlib import Path
from typing import List, Dict
import json


BASE_DIR = Path(__file__).resolve().parent.parent


MEMORY_DIR = BASE_DIR / "memory"
if not MEMORY_DIR.exists():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def load_chat_memory(session_id: str)-> List[Dict]:
    file = MEMORY_DIR / f"{session_id}.json"
    if not file.exists():
        return []
    with open(file, "r") as f:
        return json.load(f)


def save_chat_memory(session_id: str, messages: List[Dict]):
    file = MEMORY_DIR / f"{session_id}.json"
    with open(file, "w") as f:
        json.dump(messages, f)


