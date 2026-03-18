"""
src.agents — ChatOps multi-agent system powered by LangGraph.

Primary export: chatops_graph (compiled StateGraph)
"""

from .graph import chatops_graph

# Tool exports (for backward compat / direct use)
from .tools.filesystem import *
from .tools.network import *
from .tools.firewallandsecurity import *
from .tools.usagemonitoring import *
from .tools.servers import *
from .tools.usermanagement import *

__all__ = [
    "chatops_graph",
    # filesystem tools
    "make_dir",
    "create_file",
    "change_dir",
    "list_dir",
    "delete_file_request",
    "delete_file_confirm",
    "pending_manage",
    # network tools
    "ping",
    "traceroute",
    "get_ip_address",
    "show_ipconfig",
    "get_default_gateway",
    "tcp_port_check",
    # firewall tools
    "firewall_status",
    # monitoring tools
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    # user tools
    "list_users",
    "add_user",
    "delete_user",
    "change_password",
    "list_groups",
    "add_to_group",
    "remove_from_group",
    "ssh_connect_password",
    "ssh_disconnect",
    "ssh_execute_command",
    "webserver",
]
