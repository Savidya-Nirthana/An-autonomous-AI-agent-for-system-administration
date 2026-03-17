from cli.networking import (
    show_default_gateway_ui,
    show_ip_address_ui,
    show_traceroute_ui,
    show_tcp_port_check_ui,
    show_static_ip_ui,
    show_static_dns_ui,
    show_netbios_table_ui,
    show_network_adapters_ui,
    show_test_net_connection_ui,
    show_ping_ui,
    show_ipconfig_ui,
    show_ip_mac_details_ui,
    show_arp_cache_ui,
    show_active_ports_ui,
    show_dns_lookup_ui,
    show_routing_table_ui,
    show_wifi_interfaces_ui,
    show_network_fix_ui
)
from cli.filesystem import (
    show_detailed_list_ui,
    show_simple_list_ui,
    show_file_info_ui,
    show_read_file_ui,
    show_tree_ui,
    show_chkdsk_ui,
    show_permissions_ui,
    show_take_ownership_ui
)
from cli.resource_monitoring import (
    show_cpu_basic_ui,
    show_cpu_full_ui,
    show_memory_usage_ui,
    show_disk_usage_ui,
    show_processes_ui,
    show_system_info_ui,
    show_drivers_ui,
    show_user_info_ui,
    show_disk_free_ui,
    show_event_logs_ui,
    show_apps_ui,
    show_wmic_software_ui,
    show_process_kill_ui
)
from rich.console import Console
from rich.panel import Panel


def render_ui(tool_data: dict) -> bool:
    for tool in tool_data:
        ui_type = tool.get("ui_type")

        if ui_type == "default_gateway":
            show_default_gateway_ui(tool.get("default_gateway"))

        elif ui_type == "ip_address":
            show_ip_address_ui(tool.get("ip_address"))

        elif ui_type == "traceroute":
            show_traceroute_ui(tool)

        elif ui_type == "ping":
            show_ping_ui(tool)

        elif ui_type == "ipconfig":
            show_ipconfig_ui(tool)

        elif ui_type == "ip_mac_details":
            show_ip_mac_details_ui(tool)

        elif ui_type == "arp_cache":
            show_arp_cache_ui(tool)

        elif ui_type == "active_ports":
            show_active_ports_ui(tool)

        elif ui_type == "dns_lookup":
            show_dns_lookup_ui(tool)

        elif ui_type == "routing_table":
            show_routing_table_ui(tool)

        elif ui_type == "wifi_interfaces":
            show_wifi_interfaces_ui(tool)

        elif ui_type == "static_ip_config":
            show_static_ip_ui(tool)

        elif ui_type == "static_dns_config":
            show_static_dns_ui(tool)

        elif ui_type == "netbios_table":
            show_netbios_table_ui(tool)

        elif ui_type == "network_adapters":
            show_network_adapters_ui(tool)

        elif ui_type == "test_net_connection":
            show_test_net_connection_ui(tool)

        elif ui_type == "network_fix":
            show_network_fix_ui(tool)

        elif ui_type == "list_dir":
            if tool["view"] == "simple":
                show_simple_list_ui(tool["entries"])
            else:
                show_detailed_list_ui(tool["entries"])

        elif ui_type == "file_info":
            show_file_info_ui(tool)
        
        elif ui_type == "read_file":
            show_read_file_ui(tool)
            
        elif ui_type == "directory_tree":
            show_tree_ui(tool)

        elif ui_type == "chkdsk":
            show_chkdsk_ui(tool)

        elif ui_type == "permissions_fix":
            show_permissions_ui(tool)

        elif ui_type == "take_ownership":
            show_take_ownership_ui(tool)

        elif ui_type == "tcp_port_check":
            show_tcp_port_check_ui(tool)

        elif ui_type == "cpu_usage":
            if tool["detail"] == "basic":
                show_cpu_basic_ui(tool)
            else:
                show_cpu_full_ui(tool)
        
        elif ui_type == "memory_usage":
            show_memory_usage_ui(tool)

        elif ui_type == "disk_usage":
            show_disk_usage_ui(tool)

        elif ui_type == "running_processes":
            show_processes_ui(tool)
        
        elif ui_type == "system_info":
            show_system_info_ui(tool)

        elif ui_type == "system_drivers":
            show_drivers_ui(tool)

        elif ui_type == "user_info":
            show_user_info_ui(tool)

        elif ui_type == "disk_free":
            show_disk_free_ui(tool)

        elif ui_type == "system_logs":
            show_event_logs_ui(tool)

        elif ui_type == "installed_apps":
            show_apps_ui(tool)

        elif ui_type == "wmic_software":
            show_wmic_software_ui(tool)
        
        elif ui_type == "process_kill":
            show_process_kill_ui(tool)
        
        # New Network & System Monitoring Tools (Pre-formatted in node scripts)
        elif ui_type in [
            "ip_mac_details", 
            "arp_cache", 
            "active_ports", 
            "dns_lookup", 
            "routing_table", 
            "wifi_interfaces",
            "path_ping",
            "mac_address",
            "cpu_load",
            "system_drivers",
            "user_info",
            "login_history"
        ]:
            if "output" in tool:
                titles = {
                    "ip_mac_details": "🌐 [bold blue]IP & MAC Details[/bold blue]",
                    "arp_cache": "🔗 [bold green]ARP Cache[/bold green]",
                    "active_ports": "🔌 [bold magenta]Active Network Ports[/bold magenta]",
                    "dns_lookup": "🔍 [bold cyan]DNS Lookup[/bold cyan]",
                    "routing_table": "🛣️ [bold red]Routing Table[/bold red]",
                    "wifi_interfaces": "📡 [bold yellow]Wi-Fi Interfaces[/bold yellow]",
                    
                    "running_processes": "⚙️ [bold red]Running Processes[/bold red]",
                    "system_info": "🖥️ [bold cyan]System Information[/bold cyan]",
                    "memory_stats": "🧠 [bold magenta]Memory Statistics[/bold magenta]",
                    "memory_usage": "💾 [bold cyan]Memory Usage[/bold cyan]",
                    "disk_usage": "💽 [bold magenta]Disk Usage[/bold magenta]",
                    "cpu_load": "⏱️ [bold yellow]CPU Load[/bold yellow]",
                    "system_drivers": "🚗 [bold green]System Drivers[/bold green]",
                    "user_info": "👤 [bold blue]User Information[/bold blue]",
                    "login_history": "📜 [bold white]Login History[/bold white]"
                }
                
                colors = {
                    "ip_mac_details": "blue",
                    "arp_cache": "green",
                    "active_ports": "magenta",
                    "dns_lookup": "cyan",
                    "routing_table": "red",
                    "wifi_interfaces": "yellow",
                    
                    "running_processes": "red",
                    "system_info": "cyan",
                    "memory_stats": "magenta",
                    "memory_usage": "cyan",
                    "disk_usage": "magenta",
                    "cpu_load": "yellow",
                    "system_drivers": "green",
                    "user_info": "blue",
                    "login_history": "white"
                }

                Console().print(Panel(
                    str(tool["output"]).strip(),
                    title=titles.get(ui_type, "[bold]Tool Output[/bold]"),
                    border_style=colors.get(ui_type, "white")
                ))

    return True

