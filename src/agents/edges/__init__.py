"""
Edge logic — conditional routing from the supervisor to agent nodes.
Includes role-based permission check before routing to any agent.
"""

from typing import Literal
from src.agents.state import AgentState
from cli import cli_functions                    # import the MODULE, not the variable
from auth import auth_service


# The set of agent node names + END sentinel
AgentName = Literal["filesystem", "network", "firewall", "monitoring", "admin", "FINISH"]


def route_to_agent(state: AgentState) -> str:
    """
    Read state['next_agent'] set by the supervisor and return
    the matching node name, or '__end__' to finish the graph.

    Permission check: blocks the route if the current user's role
    does not include the target agent in ROLE_PERMISSIONS.
    """
    next_agent = state.get("next_agent", "FINISH")

    if next_agent == "FINISH":
        return "__end__"

    # ── Permission check ──────────────────────────────────────────
    # Access current_user via the module so we always get the live
    # value (set after login), not a stale None from import time.
    user = cli_functions.current_user
    if user and not auth_service.can_use_tool(user, next_agent):
        print(f"[Access Denied] Your role '{user.role.value}' "
              f"cannot use the '{next_agent}' agent.")
        return "__end__"

    return next_agent
