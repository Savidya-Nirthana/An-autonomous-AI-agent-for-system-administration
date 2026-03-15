"""
This is where the permission check actually blocks routing
"""

from cli import cli_functions               # import MODULE, not the variable
from auth import auth_service
from src.agents.state import AgentState

def route_to_agent(state: AgentState) -> str:
    next_node = state.get("next")          # set by supervisor_node

    if next_node == "__end__" or next_node is None:
        return "__end__"

    # ── Permission check ──────────────────────────────────────────
    user = cli_functions.current_user
    if user and not auth_service.can_use_tool(user, next_node):
        print(f"[Access Denied] Your role '{user.role.value}' "
              f"cannot use the '{next_node}' agent.")
        return "__end__"

    return next_node