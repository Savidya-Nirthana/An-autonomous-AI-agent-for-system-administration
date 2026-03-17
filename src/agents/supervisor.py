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
- servers → SSH connections, reverse proxies, start simple HTTP webserver
- system → package managers, reboots, time sync, server uptime
- users → create, modify, disable, and manage local OS users and groups
- admin → answer questions using ONLY chat memory
- knowledge → answer general knowledge questions, generate text/code, or provide explanations that do NOT require system tools
- cmd → execute STRICTLY FORMATTED terminal commands (e.g., `ls`, `cd /tmp`, `mkdir new_folder`). DO NOT route natural language requests (e.g., "update a file by adding...") to 'cmd'. If the request is conversational or needs reasoning, use 'filesystem' or another agent. 'cmd' does NOT understand natural language.
- FINISH → ALL tasks in the user's request are complete

RULES:
1. Route to the BEST agent for the user's request.
2. Review the "TASK CONTEXT" to see what previous agents have accomplished.
3. For multi-part requests (e.g., "Find my IP and save it to a file"), you MUST route to the agents sequentially. If one part is done (e.g., IP found in TASK CONTEXT), route to the next agent (e.g., filesystem to save it).
4. DO NOT route to another agent to just double-check, confirm, or verify information. Only route to another agent if there is an unfulfilled sub-task.
5. DO NOT route to the "admin" agent unless the user EXPLICITLY asks a conversational question about chat memory.
6. If an agent failed or returned an error, you may try a DIFFERENT agent, but DO NOT route to the same agent again. If 'cmd' failed, it is likely because the user's request was not a valid shell command; use an LLM-based agent instead or FINISH.
7. CRITICAL: If the user's request was PURELY a terminal command (like `cd ...`, `ls`, etc.), and the 'cmd' agent has executed it, you MUST choose FINISH. DO NOT hallucinate extra tasks.
8. If the ENTIRE user request is complete based on the TASK CONTEXT, choose FINISH.

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
