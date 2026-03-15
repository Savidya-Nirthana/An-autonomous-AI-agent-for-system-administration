"""
Chat LLM Providers - 2 Model architectures

Two specialised LLMs for different tasks:
    - Router: routes user messages to the correct tool
    - Agent: executes the tool and returns the result

"""

from typing import Optional, Any, Dict
from langchain_openai import ChatOpenAI

from src.infrastructure.config import (
    ROUTER_MODEL,
    ROUTER_PROVIDER,
    GROQ_BASE_URL,
    CHAT_MODEL,
    CHAT_PROVIDER,
    OPENROUTER_BASE_URL,
    get_api_key
)


def _build_llm(
    model: str,
    provider: str,
    temperature: float = 0.0,
    streaming: bool = False,
    max_tokens: Optional[int] = None,
    **kwargs: Any
) -> ChatOpenAI:
    """
    Internal factory - builds a ChatOpenAI for ant provider. 
    """
    llm_kwargs : Dict[str, Any] = dict(
        model=model,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens,
        **kwargs
    )
    if provider == "openrouter":
        llm_kwargs["openai_api_base"] = OPENROUTER_BASE_URL
        llm_kwargs["openai_api_key"] = get_api_key("openrouter")
    elif provider == "groq":
        llm_kwargs["openai_api_base"] = GROQ_BASE_URL
        llm_kwargs["openai_api_key"] = get_api_key("groq")
    elif provider == "openai":
        llm_kwargs["openai_api_key"] = get_api_key("openai")


    return ChatOpenAI(**llm_kwargs)

def get_router_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """
    Returns the router LLM.
    """
    return _build_llm(
        model=ROUTER_MODEL,
        provider=ROUTER_PROVIDER,
        temperature=0.0,
        **kwargs
    )

def get_chat_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """
    Returns the chat LLM.
    """
    return _build_llm(
        model=CHAT_MODEL,
        provider=CHAT_PROVIDER,
        temperature=0.0,
        max_tokens=2000,
        **kwargs
    )