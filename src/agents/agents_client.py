from typing import Literal
from langchain.agents import create_agent
from .tools.filesystem import make_dir, create_file, change_dir, list_dir,pending_manage
from .tools.network import ping, traceroute, get_ip_address, show_ipconfig, get_default_gateway, tcp_port_check
from .tools.firewallmanagement import firewall_status
from .tools.usagemonitoring import cpu_usage, memory_usage, disk_usage
from .tools.filesystem_delete import delete_file_request, delete_file_confirm
from .tools.usermanagement import add_user, delete_user, list_users, update_user
from .tools.systemmanagement import update_packages, shutdown, restart, sync_time, view_uptime
from .prompts.admin.admin_prompts import admin_system_prompt
from .prompts.file_system.file_system import filesystem_prompt

class AgentClient:
    def __init__(self, llm, agent_name: Literal["filesystem", "admin", "genaral", "network", "networkandfile", "firewallmanagement", "usagemonitoring"]):
        self.llm_client = llm
        self.agent_name = agent_name


    def create_agent(self):
        if self.agent_name == "admin":
            print("admin agent created")
            return create_agent(
                model=self.llm_client,
                system_prompt=admin_system_prompt,
            )
        elif self.agent_name == "filesystem":
            return create_agent(
                model=self.llm_client,
                tools=[make_dir, create_file, change_dir, list_dir, delete_file_request, delete_file_confirm, pending_manage],
                system_prompt=filesystem_prompt,
            )
        elif self.agent_name == "network":
            print("network agent created")
            return create_agent(
                model=self.llm_client,
                tools=[ping, traceroute, get_ip_address, show_ipconfig, get_default_gateway, tcp_port_check],
                system_prompt="You are a helpful assistant who can perform network operations i provide also my previous chat history",
            )

        elif self.agent_name == "networkandfile":
            print("networkandfile agent created")
            return create_agent(
                model=self.llm_client,
                tools=[ping, traceroute, get_ip_address, show_ipconfig, get_default_gateway, make_dir, create_file, change_dir, list_dir],
                system_prompt="You are a helpful assistant who can perform network operations and file operations",
            )

        elif self.agent_name == "firewallmanagement":
            return create_agent(
                model=self.llm_client,
                tools=[firewall_status],
                system_prompt="You are a helpful assistant who can perform network operations",
            )
        
        elif self.agent_name == "usagemonitoring":
            return create_agent(
                model=self.llm_client,
                tools=[cpu_usage, memory_usage, disk_usage],
                system_prompt="You are a helpful assistant who can perform usage monitoring (cpu, memory, disk space)",
            )
        
        elif self.agent_name == "system":
            return create_agent(
                model=self.llm_client,
                tools=[update_packages, shutdown, restart, sync_time, view_uptime],
                system_prompt="You are a helpful assistant who can perform system operations",
            )


