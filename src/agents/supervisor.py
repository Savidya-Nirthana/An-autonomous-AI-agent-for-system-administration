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
- cmd → execute any command without any agent call check the command is correct code like cd <directory> or ls or dir or mkdir <directory> or rmdir <directory> or touch <file> or rm <file> or cat <file> or echo <text> <file> or cp <file> <directory> or mv <file> <directory> etc. so these codes can be directly executed without using any agent.
- FINISH → ALL tasks in the user's request are complete

RULES:
1. Route to the BEST agent for the user's request.
2. Review the "TASK CONTEXT" to see what previous agents have accomplished.
3. EXTREMELY IMPORTANT: If the user's request was to perform an action (like creating a file, writing content, checking a ping) AND the "TASK CONTEXT" shows that the action was performed and a result was returned, you MUST choose FINISH immediately.
4. DO NOT route to another agent to double-check, confirm, or verify information.
5. DO NOT route to the "admin" agent unless the user EXPLICITLY asks a conversational question about chat memory.
6. For multi-part requests, route to the next needed agent ONLY if there is a completely unaddressed part of the original request.

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
    task_context = state.get("task_context", {})
    context_str = ""
    if task_context:
        context_str = "\nTASK CONTEXT (Results from previous agents):\n"
        for k, v in task_context.items():
            context_str += f"- {k}: {v}\n"

    if visited:
        routing_input = (
            f"ORIGINAL REQUEST: {last_human}\n"
            f"AGENTS ALREADY COMPLETED: {', '.join(visited)}\n"
            f"{context_str}"
            f"Route to the next needed agent, or FINISH if the overall request is fully satisfied."
        )
    else:
        routing_input = last_human

    # ── Call routing LLM with error recovery ─────────────────
    from cli.reasoning_ui import show_routing_decision, show_finish, show_error

    try:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=_SUPERVISOR_PROMPT.format(
                format_instructions=_parser.get_format_instructions()
            )),
            ("human", "{input}"),
        ])

        chain = prompt | _get_llm() | _parser
        decision: RoutingDecision = chain.invoke({"input": routing_input})

        if decision.agent == "FINISH":
            show_finish()
        else:
            show_routing_decision(decision.agent, decision.reason)

        return {"next_agent": decision.agent}

    except Exception as e:
        show_error(f"Routing error: {e}, finishing.")
        return {"next_agent": "FINISH"}
