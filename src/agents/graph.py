"""
LangGraph StateGraph — the compiled multi-agent graph.
"""

from langgraph.graph import StateGraph, END

from src.agents.state import AgentState
from src.agents.supervisor import supervisor_node
from src.agents.edges import route_to_agent
from src.agents.nodes import (
    filesystem_node,
    network_node,
    firewall_node,
    monitoring_node,
    admin_node,
    cmd_node,
    knowledge_node,
)


def build_graph() -> StateGraph:
    """Construct and compile the ChatOps multi-agent graph."""

    graph = StateGraph(AgentState)

    # ── Add nodes ────────────────────────────────────────────────
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("filesystem", filesystem_node)
    graph.add_node("network", network_node)
    graph.add_node("firewall", firewall_node)
    graph.add_node("monitoring", monitoring_node)
    graph.add_node("admin", admin_node)
    graph.add_node("cmd", cmd_node)
    graph.add_node("knowledge", knowledge_node)

    # ── Entry point ──────────────────────────────────────────────
    graph.set_entry_point("supervisor")

    # ── Conditional edge: supervisor → agent or END ──────────────
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "filesystem": "filesystem",
            "network": "network",
            "firewall": "firewall",
            "monitoring": "monitoring",
            "admin": "admin",
            "cmd": "cmd",
            "knowledge": "knowledge",
            "__end__": END,
        },
    )

    # ── Each agent loops back to the supervisor ──────────────────
    for node_name in ["filesystem", "network", "firewall", "monitoring", "admin", "cmd", "knowledge"]:
        graph.add_edge(node_name, "supervisor")

    return graph.compile()


# Pre-built graph instance, ready to use
chatops_graph = build_graph()
