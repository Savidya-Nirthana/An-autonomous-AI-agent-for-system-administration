import json
from langchain_core.messages import ToolMessage
from typing import Optional, Dict, Any


def extract_tool_ui(messages) -> Optional[Dict[str, Any]]:
    tool_message = []
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            try:
                tool_message.append(json.loads(msg.content))
            except json.JSONDecodeError:
                pass
    return tool_message
    