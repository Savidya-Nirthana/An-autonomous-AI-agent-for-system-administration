from typing import Literal
from langchain.agents import create_agent
from tools.filesystem import make_dir, create_file, change_dir, list_dir
from tools.network import ping, traceroute, get_ip_address, show_ipconfig, get_default_gateway
from tools.firewallandsecurity import firewall_status, restore_internet_connection, block_internet_connection, turn_on_firewall, turn_off_firewall, view_saved_credintials_by_os, delay
from tools.usagemonitoring import cpu_usage, memory_usage, disk_usage

class AgentClient:
    def __init__(self, llm, agent_name: Literal["filesystem", "admin", "network", "networkandfile", "security", "usagemonitoring"]):
        self.llm_client = llm.client
        self.agent_name = agent_name


    def create_agent(self):
        if self.agent_name == "admin":
            return create_agent(
                model=self.llm_client,
                system_prompt="You are a helpful assistant who can answer any question",
            )
        elif self.agent_name == "filesystem":
            return create_agent(
                model=self.llm_client,
                tools=[make_dir, create_file, change_dir, list_dir],
                system_prompt="You are a helpful assistant who can create directories and files",
            )
        elif self.agent_name == "network":
            print("network agent created")
            return create_agent(
                model=self.llm_client,
                tools=[ping, traceroute, get_ip_address, show_ipconfig, get_default_gateway],
                system_prompt="You are a helpful assistant who can perform network operations",
            )

        elif self.agent_name == "networkandfile":
            print("networkandfile agent created")
            return create_agent(
                model=self.llm_client,
                tools=[ping, traceroute, get_ip_address, show_ipconfig, get_default_gateway, make_dir, create_file, change_dir, list_dir],
                system_prompt="You are a helpful assistant who can perform network operations and file operations",
            )

        elif self.agent_name == "security":
            return create_agent(
                model=self.llm_client,
                tools=[
                    view_saved_credintials_by_os, 
                    firewall_status, 
                    turn_on_firewall, 
                    turn_off_firewall, 
                    delay,
                    restore_internet_connection,
                    block_internet_connection,
                ],
                system_prompt="You are a helpful assistant who can perform security and credentials related operations",
            )
        
        elif self.agent_name == "usagemonitoring":
            return create_agent(
                model=self.llm_client,
                tools=[cpu_usage, memory_usage, disk_usage],
                system_prompt="You are a helpful assistant who can perform usage monitoring (cpu, memory, disk space)",
            )


