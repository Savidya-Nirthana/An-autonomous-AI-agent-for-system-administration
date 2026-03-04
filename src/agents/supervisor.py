"""
Supervisor Node — the brain of the LangGraph multi-agent system.

Routes to specialist agents and supports multi-step chaining.
Hard-capped at MAX_AGENT_STEPS to prevent infinite loops.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.agents.state import AgentState
from schema.routing_schema import RoutingDecision
from src.infrastructure.llm import get_router_llm


MAX_AGENT_STEPS = 3  # hard cap: at most 3 agent hops per user message

# ── Lazy singleton ───────────────────────────────────────────────────
_router_llm = None

def _get_llm():
    global _router_llm
    if _router_llm is None:
        _router_llm = get_router_llm()
    return _router_llm


# ── Parser ───────────────────────────────────────────────────────────
_parser = PydanticOutputParser(pydantic_object=RoutingDecision)


# ── Supervisor prompt ────────────────────────────────────────────────
_SUPERVISOR_PROMPT = """You are a ROUTING SUPERVISOR for a system-administration chatbot.

AVAILABLE AGENTS:
- filesystem → file/folder operations (create, delete, list, navigate)
- network → ping, traceroute, IP lookup, port check
- firewall → firewall status and security settings
- monitoring → CPU, memory, disk usage
- admin → answer questions using ONLY chat memory
- FINISH → ALL tasks in the user's request are complete

RULES:
1. Route to the BEST agent for the user's request.
2. If agents have already completed tasks and the request is fully handled, choose FINISH.
3. For multi-part requests, route to the next needed agent.

{format_instructions}"""


def supervisor_node(state: AgentState) -> dict:
    """
    Examines state to decide the next agent or FINISH.
    """
    messages = state.get("messages", [])
    visited = state.get("visited", [])

    # ── Safety: hard cap on agent steps ──────────────────────
    if len(visited) >= MAX_AGENT_STEPS:
        return {"next_agent": "FINISH"}

    # ── Find latest user message ─────────────────────────────
    last_human = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human = msg.content
            break

    if not last_human:
        return {"next_agent": "FINISH"}

    # ── Build routing input ──────────────────────────────────
    if visited:
        routing_input = (
            f"ORIGINAL REQUEST: {last_human}\n"
            f"AGENTS ALREADY COMPLETED: {', '.join(visited)}\n"
            f"Route to the next needed agent, or FINISH if done."
        )
    else:
        routing_input = last_human

    # ── Call routing LLM with error recovery ─────────────────
    try:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=_SUPERVISOR_PROMPT.format(
                format_instructions=_parser.get_format_instructions()
            )),
            ("human", "{input}"),
        ])

        chain = prompt | _get_llm() | _parser
        decision: RoutingDecision = chain.invoke({"input": routing_input})
        print(f"[Supervisor] → {decision.agent} ({decision.reason})")
        return {"next_agent": decision.agent}

    except Exception as e:
        print(f"[Supervisor] routing error: {e}, finishing.")
        return {"next_agent": "FINISH"}
