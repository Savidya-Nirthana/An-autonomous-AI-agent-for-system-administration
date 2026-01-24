from cli.networking import show_default_gateway_ui, show_ip_address_ui, show_traceroute_ui, show_tcp_port_check_ui
from cli.filesystem import show_detailed_list_ui, show_simple_list_ui
from cli.resourse_monitoring import show_cpu_basic_ui, show_cpu_full_ui

def render_ui(tool_data: dict) -> bool:
    for tool in tool_data:
        ui_type = tool.get("ui_type")

        if ui_type == "default_gateway":
            show_default_gateway_ui(tool.get("default_gateway"))
        
        elif ui_type == "ip_address":
            show_ip_address_ui(tool.get("ip_address"))

        elif ui_type == "traceroute":
            show_traceroute_ui(tool.get("traceroute"))
        
        elif ui_type == "list_dir":
            if tool["view"] == "simple":
                show_simple_list_ui(tool["entries"])
            else:
                show_detailed_list_ui(tool["entries"])

        elif ui_type == "tcp_port_check":
            show_tcp_port_check_ui(tool)

        if ui_type == "cpu_usage":
            if tool["detail"] == "basic":
                show_cpu_basic_ui(tool)
            else:
                show_cpu_full_ui(tool)

    return True

