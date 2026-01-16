from langchain_core.runnables import RunnableLambda
import tiktoken
from typing import Literal, Optional, Any


def pick_encoding(
    provider: Literal["openai", "google", "groq"], model: str
) -> tiktoken.Encoding:
    if provider == "openai":
        if any(x in model.lower() for x in ["gpt-4o", "gpt-4", "o3", "o1"]):
            try:
                return tiktoken.get_encoding("o200k_base")
            except Exception:
                pass
        
        return tiktoken.get_encoding("cl100k_base")

    return tiktoken.get_encoding("o200k_base")



def count_text_tokens(
    text: str, provider: Literal["openai", "google", "groq"], model: str
) -> int:
    if not text:
        return 0
    enc = pick_encoding(provider, model)
    return len(enc.encode(text, disallowed_special=()))


def count_messages_tokens(
    messages: list[dict[str, str]],
    provider: Literal["openai", "google", "groq"],
    model: str,
    context_strs: Optional[list[str]] = None,
) -> dict[str, int]:
    enc = pick_encoding(provider, model)

    input_tokens = 0
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        input_tokens += 4
        input_tokens += len(enc.encode(content, disallowed_special=()))

    context_tokens = 0
    if context_strs:
        for ctx in context_strs:
            context_tokens += len(enc.encode(ctx, disallowed_special=()))
    overhead = 3 

    return {
        "input_tokens": input_tokens,
        "context_tokens": context_tokens,
        "estimated_total": input_tokens + context_tokens + overhead,
    }




def token_guard(
    agent,
    provider: Literal["openai", "google", "groq"],
    model_name: str,
    hard_prompt_cap: int
):
    def guard(input):
        messages = input.get("messages", [])
        token_count = count_messages_tokens(messages, provider, model_name)
        if token_count["estimated_total"] > hard_prompt_cap:
            raise ValueError(f"Prompt exceeds token limit of {hard_prompt_cap}")

        print(token_count)

        return agent.invoke(input)

    return RunnableLambda(guard)


        