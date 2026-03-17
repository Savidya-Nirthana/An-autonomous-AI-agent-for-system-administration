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

AVAILABLE AGENTS & PRIORITIES:
1. network → ALWAYS route here for IP settings, DNS settings, ping, tracert, ipconfig, winsock/tcp resets, ACTIVE PORTS, ARP CACHE, ROUTING TABLE, WIFI INTERFACES, or NETWORK ADAPTERS. Static IP/DNS configuration is ONLY for this agent.
2. firewall → inspect firewall status, firewall rules, and security settings. This agent CANNOT configure IP or DNS addresses.
3. filesystem → file/folder operations (create, delete, list, navigate), DISK REPAIR (chkdsk), and PERMISSION FIXES (icacls).
4. monitoring → system health status (CPU, memory, disk usage %, processes), system details (OS/BIOS/uptime/user information/system logs), installed applications, and LISTING ALL INSTALLED DRIVERS. This agent also handles terminating/killing processes.
5. admin → answer questions using ONLY chat memory. Use this for general talk.
6. FINISH → ALL tasks in the user's request are complete.

RULES:
1. Route to the BEST agent for the user's request.
2. Review the "TASK CONTEXT" to see what previous agents have accomplished.
3. EXTREMELY IMPORTANT: If the "TASK CONTEXT" contains a "monitoring_result" key, the monitoring agent has already run and returned data. You MUST choose FINISH immediately — do NOT route to monitoring again.
4. EXTREMELY IMPORTANT: If the user's request was to perform an action (like creating a file, writing content, checking a ping, listing processes) AND the "TASK CONTEXT" shows that the action was performed and a result was returned, you MUST choose FINISH immediately. This applies even if the agent reports an "Ambiguous" result or minor error.
5. DO NOT route to another agent to double-check, confirm, or verify information.
6. DO NOT route to the "admin" agent unless the user EXPLICITLY asks a conversational question about chat memory.
7. For multi-part requests, route to the next needed agent ONLY if there is a completely unaddressed part of the original request.
8. [CRITICAL] Do NOT route networking requests (IP, DNS, configuration) to the firewall agent.
9. [CRITICAL] Do NOT route networking requests to the filesystem agent.

OUTPUT FORMAT:
You must return ONLY a valid JSON object matching this schema. Do not return the schema itself, return the actual JSON object with your true values filled in. Do NOT wrap it in markdown block quotes (```json).
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

    # ── Hard exit: monitoring already ran and returned a result ──
    task_context = state.get("task_context", {})
    if "monitoring" in visited and task_context.get("monitoring_result"):
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
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    import json
    import re
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=_SUPERVISOR_PROMPT.format(
                format_instructions=_parser.get_format_instructions()
            )),
            ("human", "{input}"),
        ])

        # We separate the llm call and parser to allow manual JSON cleanup if it fails
        llm = _get_llm()
        raw_response = (prompt | llm).invoke({"input": routing_input}).content
        
        try:
            decision = _parser.invoke(raw_response)
        except Exception as parse_err:
            # Fallback: manually strip bad LLM JSON markdown wrapper and try parsing again
            cleaned_json = re.sub(r'```json\n|```\n|```', '', raw_response).strip()
            
            # Robustify: Escape single backslashes in the reason string (common in Windows names)
            # This looks for a backslash NOT followed by valid JSON escape chars
            cleaned_json = re.sub(r'\\(?![\\/bfnrtu"])', r'\\\\', cleaned_json)

            try:
                # If the LLM literally returned schema properties instead of values, default to admin
                if '"properties":' in cleaned_json or '"type": "string"' in cleaned_json:
                    decision = RoutingDecision(agent="admin", reason="Fallback after LLM returned schema instead of JSON.")
                else:
                    data = json.loads(cleaned_json)
                    decision = RoutingDecision(**data)
            except Exception:
                # If still failing, check if it's a finish-like response
                if "FINISH" in raw_response.upper():
                    decision = RoutingDecision(agent="FINISH", reason="Fallback FINISH due to parsing error.")
                else:
                    raise parse_err
        
        console = Console()
        reasoning_text = Text()
        reasoning_text.append("Agent Selected: ", style="bold cyan")
        reasoning_text.append(f"{decision.agent}\n", style="bold green")
        reasoning_text.append("Reasoning: ", style="bold cyan")
        reasoning_text.append(f"{decision.reason}", style="italic yellow")
        
        panel = Panel(
            reasoning_text, 
            title="[bold magenta]Supervisor Routing Decision[/bold magenta]", 
            border_style="cyan", 
            expand=False
        )
        console.print(panel)
        
        return {"next_agent": decision.agent}

    except Exception as e:
        console = Console()
        console.print(f"[bold red][Supervisor] routing error: {e}, finishing.[/bold red]")
        return {"next_agent": "FINISH"}