"""
src.agents — ChatOps multi-agent system powered by LangGraph.

Primary export: chatops_graph (compiled StateGraph)
"""

from .graph import chatops_graph

# Tool exports (for backward compat / direct use)
from .tools.filesystem import *
from .tools.network import *
from .tools.firewallmanagement import *
from .tools.usagemonitoring import *
from .tools.usermanagement import *

from .tools.servers import *

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
    # server / SSH tools
    "webserver",
    "ssh_connect_password",
    "ssh_disconnect",
    # "ssh_upload_file_password",
    # "ssh_upload_file_rsa",
    # "ssh_download_file_password",
    # "ssh_download_file_rsa",
    # "ssh_execute_command_password",
    # "ssh_execute_command_rsa",
]
