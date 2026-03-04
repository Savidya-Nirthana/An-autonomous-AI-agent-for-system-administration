"""
Helpers for agent nodes — build clean message context for each agent.
"""

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from typing import Sequence


def build_agent_messages(messages: Sequence[BaseMessage], task_context: dict) -> list:
    """
    Build a clean message list for an agent node:
    1. Keep all SystemMessages (memory context)
    2. Keep the LAST HumanMessage (current request)
    3. Inject a summary of prior agent results from task_context

    This prevents agents from seeing raw tool calls / responses
    from OTHER agents, which confuses them.
    """
    clean = []

    # Carry over system messages (memory context)
    for msg in messages:
        if isinstance(msg, SystemMessage):
            clean.append(msg)

    # If prior agents produced results, inject as context
    if task_context:
        summary_lines = []
        for key, value in task_context.items():
            summary_lines.append(f"- {key}: {value}")
        summary = "\n".join(summary_lines)
        clean.append(SystemMessage(
            content=f"RESULTS FROM PRIOR STEPS (use these to complete the current task):\n{summary}"
        ))

    # Add only the last human message (the actual request)
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            clean.append(msg)
            break

    return clean


def extract_final_response(messages: Sequence[BaseMessage]) -> str:
    """Extract the final AI text response from agent output messages."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            return msg.content
    return ""
