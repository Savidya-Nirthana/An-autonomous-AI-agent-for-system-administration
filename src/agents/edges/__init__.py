"""
Edge logic — conditional routing from the supervisor to agent nodes.
"""

from typing import Literal
from src.agents.state import AgentState


# The set of agent node names + END sentinel
AgentName = Literal["filesystem", "network", "firewall", "monitoring", "admin", "cmd", "FINISH"]


def route_to_agent(state: AgentState) -> str:
    """
    Read state['next_agent'] set by the supervisor and return
    the matching node name, or '__end__' to finish the graph.
    """
    next_agent = state.get("next_agent", "FINISH")

    if next_agent == "FINISH":
        return "__end__"

    return next_agent
