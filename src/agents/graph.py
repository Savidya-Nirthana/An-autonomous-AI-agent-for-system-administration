"""
LangGraph StateGraph — the compiled multi-agent graph.

Topology:
    START → supervisor ─┬─→ filesystem ─→ supervisor
                        ├─→ network    ─→ supervisor
                        ├─→ firewall   ─→ supervisor
                        ├─→ monitoring ─→ supervisor
                        ├─→ admin      ─→ supervisor
                        ├─→ users      ─→ supervisor
                        ├─→ system     ─→ supervisor
                        ├─→ servers    ─→ supervisor
                        └─→ END (FINISH)
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
    users_node,
    system_node,
    servers_node,
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
    graph.add_node("users", users_node) #added and ontesting
    graph.add_node("system", system_node) #added and ontesting
    graph.add_node("servers", servers_node)

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
            "users": "users",
            "system": "system",
            "servers": "servers",
            "__end__": END,
        },
    )

    # ── Each agent loops back to the supervisor ──────────────────
    for node_name in ["filesystem", "network", "firewall", "monitoring", "admin", "users", "system", "servers"]:
        graph.add_edge(node_name, "supervisor")

    return graph.compile()


# Pre-built graph instance, ready to use
chatops_graph = build_graph()
