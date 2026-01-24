from pathlib import Path
from typing import List, Dict
import json
from database.vector_db import QdrantStorage



def load_chat_memory(session_id: str, query: str)-> List[Dict]:
    
    vector_db = QdrantStorage()
    context = vector_db.search(session_id, query)

    return context

def save_chat_memory(session_id: str, user_message: str, assistant_message: str):
    vector_db = QdrantStorage()
    vector_db.upsert(session_id, user_message, assistant_message)
