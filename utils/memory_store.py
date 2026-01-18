import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True
)

def save_chat_memory(session_id, messages):
    """
    Save chat memory to Redis for the current session
    Messages will be automatically deleted when session expires
    """
    try:
        chat_key = f"chat:{session_id}"
        
        # Store messages as JSON
        redis_client.set(chat_key, json.dumps(messages))
        
        # Set same TTL as session (get from session key)
        session_ttl = redis_client.ttl(f"session:{session_id}")
        if session_ttl > 0:
            redis_client.expire(chat_key, session_ttl)
        
        return True
    except Exception as e:
        print(f"Error saving chat memory: {e}")
        return False

def load_chat_memory(session_id):
    """
    Load chat memory from Redis for the current session
    Returns empty list if no history exists (fresh session)
    """
    try:
        chat_key = f"chat:{session_id}"
        messages_json = redis_client.get(chat_key)
        
        if messages_json:
            return json.loads(messages_json)
        else:
            # Fresh session - return empty list
            return []
    except Exception as e:
        print(f"Error loading chat memory: {e}")
        return []

def clear_chat_memory(session_id):
    """
    Manually clear chat memory for a session
    (Normally handled automatically on logout)
    """
    try:
        chat_key = f"chat:{session_id}"
        redis_client.delete(chat_key)
        return True
    except Exception as e:
        print(f"Error clearing chat memory: {e}")
        return False

def get_chat_history_count(session_id):
    """Get the number of messages in chat history"""
    try:
        messages = load_chat_memory(session_id)
        return len(messages)
    except:
        return 0