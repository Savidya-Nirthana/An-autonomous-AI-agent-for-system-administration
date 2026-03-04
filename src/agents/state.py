from __future__ import annotations

from typing import Any, Annotated, Sequence, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class PendingApproval(TypedDict):
    action: str
    agent: str
    payload: dict


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_agent: str       # which agent runs next 
    task_context: Annotated[dict[str, Any], lambda a, b: {**a, **b}] # shared memory between agents
    pending_approvals: list[PendingApproval]  # human-in-the-loop queue
    error: str | None   # propergate errors across nodes
    visited: list[str]  # trace which agents that already visited
    metadata: dict[str, Any] # Optional metadata the API layer can attach (requested_id, session_id, etc)



