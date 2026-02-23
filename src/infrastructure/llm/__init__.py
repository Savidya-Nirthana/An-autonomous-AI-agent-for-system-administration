"""
LLM Providers wrappers - 2 Model architectures

Two specialised LLMs for different tasks:
    - Router: routes user messages to the correct tool
    - Agent: executes the tool and returns the result
"""

from .llm_provider import get_router_llm, get_chat_llm
from .embeddings import get_default_embedding

__all__ = [
    "get_router_llm",
    "get_chat_llm",
    "get_default_embedding",
]