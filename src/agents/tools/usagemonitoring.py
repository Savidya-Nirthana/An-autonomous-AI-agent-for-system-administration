import psutil
import subprocess
from langchain.tools import tool
from typing import Dict, Any
import platform

@tool
def cpu_usage(detail: str = "basic") -> Dict[str, Any]:
    """
    Get CPU usage statistics.

    detail:
    - basic            → overall CPU usage
    - full / advanced  → per-core, frequency, load average (if available)

    Always run the tool to get fresh data — never reuse previous results.
    """
    system = platform.system().lower()

    try:
        result = {
            "success": True,
            "os": system,
            "ui_type": "cpu_usage",
            "detail": detail,
        }

        result["cpu_percent"] = psutil.cpu_percent(interval=1)

        if detail in ("full", "advanced"):
            result["per_core"] = psutil.cpu_percent(interval=1, percpu=True)

            freq = psutil.cpu_freq()
            if freq:
                result["frequency_mhz"] = {
                    "current": freq.current,
                    "min": freq.min,
                    "max": freq.max,
                }

            if hasattr(psutil, "getloadavg"):
                try:
                    load1, load5, load15 = psutil.getloadavg()
                    result["load_average"] = {
                        "1m": load1,
                        "5m": load5,
                        "15m": load15,
                    }
                except OSError:
                    result["load_average"] = "Not supported"

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "cpu_usage"
        }


@tool
def memory_usage() -> Dict[str, Any]:
    """
    Returns detailed memory usage.
    """
    try:
        mem = psutil.virtual_memory()
        return {
            "success": True,
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent,
            "ui_type": "memory_usage"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "memory_usage"
        }


@tool
def disk_usage() -> Dict[str, Any]:
    """
    Returns detailed disk usage for the root partition.
    """
    try:
        usage = psutil.disk_usage('/')
        return {
            "success": True,
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "percent": usage.percent,
            "ui_type": "disk_usage"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "disk_usage"
        }


@tool
def list_running_processes() -> Dict[str, Any]:
    """
    List running processes with PID, name, status, and memory usage.
    Use this when the user asks to 'list processes', 'show running processes',
    'what processes are running', 'tasklist', 'ps aux', or similar.
    Always call this tool — never reuse previous results.
    """
    system = platform.system().lower()

    try:
        # psutil path: cross-platform, never hangs
        procs = []
        for p in psutil.process_iter(
            ["pid", "name", "status", "memory_percent", "username"],
            ad_value=None,
        ):
            procs.append(p.info)

        # Sort by memory descending so most active appear first
        procs.sort(key=lambda x: x.get("memory_percent") or 0, reverse=True)

        # Native command output for richer detail (best-effort, won't block)
        native_output = None
        try:
            if system == "windows":
                cmd = ["tasklist", "/v", "/fo", "csv"]
                timeout = 15
            else:
                cmd = ["ps", "aux", "--sort=-%mem"]
                timeout = 10

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                errors="replace", timeout=timeout
            )
            raw = result.stdout or ""
            # Truncate to 40 lines to keep LLM context manageable
            lines = raw.splitlines()
            if len(lines) > 40:
                raw = "\n".join(lines[:40]) + "\n... (output truncated)"
            native_output = raw if result.returncode == 0 else None
        except Exception:
            pass  # psutil data is still returned below

        return {
            "success": True,
            "ui_type": "running_processes",
            "os": system,
            "process_count": len(procs),
            "top_processes": procs[:30],
        }

    except Exception as e:
        return {"success": False, "error": str(e), "ui_type": "running_processes"}


@tool
def system_info() -> Dict[str, Any]:
    """
    Returns detailed system information for Windows including OS version,
    uptime, BIOS info, and hotfixes.
    Use this when the user asks for 'system info', 'OS version', 'uptime',
    'BIOS info', or 'hotfixes'.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "system_info"
        }

    try:
        # Get uptime using psutil (portable)
        boot_time = psutil.boot_time()
        import datetime
        uptime = str(datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time))
        
        # Get detailed system info using 'systeminfo' command
        # Parsing CSV format is safest
        cmd = ["systeminfo", "/fo", "csv"]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        
        if result.returncode == 0:
            import csv
            import io
            reader = csv.DictReader(io.StringIO(result.stdout))
            info = next(reader)
            
            return {
                "success": True,
                "ui_type": "system_info",
                "os_name": info.get("OS Name"),
                "os_version": info.get("OS Version"),
                "os_manufacturer": info.get("OS Manufacturer"),
                "bios_version": info.get("BIOS Version"),
                "boot_time": uptime.split('.')[0], # Clean uptime
                "hotfixes": info.get("Hotfix(s)"),
                "raw_data": info
            }
        else:
            return {
                "success": False,
                "error": "Failed to run systeminfo command.",
                "ui_type": "system_info"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "system_info"
        }


@tool
def list_drivers() -> Dict[str, Any]:
    """
    Returns a list of installed drivers on Windows.
    Use this when the user asks to 'list drivers', 'show drivers',
    'what drivers are installed', or similar.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "system_drivers"
        }

    try:
        # Run driverquery /v /fo csv for detailed output
        cmd = ["driverquery", "/v", "/fo", "csv"]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=60)
        
        if result.returncode == 0:
            import csv
            import io
            reader = csv.DictReader(io.StringIO(result.stdout))
            drivers = list(reader)
            
            # Limit to top 50 to avoid context issues, though UI might handle it
            return {
                "success": True,
                "ui_type": "system_drivers",
                "driver_count": len(drivers),
                "drivers": drivers[:50], 
                "total_drivers": len(drivers)
            }
        else:
            return {
                "success": False,
                "error": "Failed to run driverquery command.",
                "ui_type": "system_drivers"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "system_drivers"
        }


@tool
def user_info() -> Dict[str, Any]:
    """
    Returns structured information about the current user, groups, and privileges on Windows.
    Use this when the user asks 'current user', 'provide user informations', 'who am I', 'show my groups', 'what are my privileges', etc.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "user_info"
        }

    try:
        # whoami /all /fo csv produces multiple CSV tables in one output.
        # We need to manually split and parse them.
        cmd = ["whoami", "/all", "/fo", "csv"]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=30)
        
        if result.returncode != 0:
            return {"success": False, "error": "Failed to run whoami command.", "ui_type": "user_info"}

        import csv
        import io
        
        output = result.stdout
        sections = output.split("\n\n")
        
        data = {
            "success": True,
            "ui_type": "user_info",
            "user": {},
            "groups": [],
            "privileges": []
        }

        for idx, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Use csv reader on each block
            f = io.StringIO(section.strip())
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if idx == 0 and rows: # User Info
                data["user"] = rows[0]
            elif "Group Name" in section and rows: # Groups
                data["groups"] = rows
            elif "Privilege Name" in section and rows: # Privileges
                data["privileges"] = rows

        return data

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "user_info"
        }


@tool
def check_disk_free() -> Dict[str, Any]:
    """
    Returns detailed free space information for the C: drive on Windows using fsutil.
    Use this when the user specifically asks for 'disk free space', 'free space on C',
    or mentions 'fsutil'.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "disk_free"
        }

    try:
        # Run fsutil volume diskfree C:
        cmd = ["fsutil", "volume", "diskfree", "C:"]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=15)
        
        if result.returncode != 0:
            # Fallback to PowerShell if fsutil fails (typically due to lack of admin privileges)
            ps_cmd = ["powershell", "-Command", "Get-PSDrive C | Select-Object Used, Free | ConvertTo-Json"]
            ps_result = subprocess.run(ps_cmd, capture_output=True, text=True, errors="replace", timeout=15)
            
            if ps_result.returncode == 0:
                import json
                try:
                    ps_data = json.loads(ps_result.stdout)
                    used = ps_data.get("Used", 0)
                    free = ps_data.get("Free", 0)
                    total = used + free
                    return {
                        "success": True,
                        "ui_type": "disk_free",
                        "Total # of bytes": total,
                        "Total # of free bytes": free,
                        "Total # of avail free bytes": free,
                        "method": "powershell_fallback"
                    }
                except:
                    pass

            return {
                "success": False,
                "error": "Failed to run fsutil command (Access Denied) and PowerShell fallback failed.",
                "ui_type": "disk_free"
            }

        # Original fsutil parsing logic
        lines = result.stdout.strip().split("\n")
        data = {"success": True, "ui_type": "disk_free", "raw_output": result.stdout, "method": "fsutil"}
        
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                try:
                    val = int(val)
                except ValueError:
                    pass
                data[key] = val
                
        return data

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "disk_free"
        }

@tool
def get_event_logs() -> Dict[str, Any]:
    """
    Returns the newest 10 system event logs from Windows using PowerShell.
    Use this when the user asks for 'system logs', 'event logs', or 'check errors/warnings'.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "system_logs"
        }

    try:
        # Get newest 10 system event logs in JSON
        ps_cmd = [
            "powershell", 
            "-Command", 
            "Get-EventLog -LogName System -Newest 10 | Select-Object TimeGenerated, EntryType, Source, Message | ConvertTo-Json"
        ]
        result = subprocess.run(ps_cmd, capture_output=True, text=True, errors="replace", timeout=30)
        
        if result.returncode == 0:
            import json
            try:
                logs = json.loads(result.stdout)
                # If there's only 1 log, PowerShell returns a dict instead of a list of dicts.
                if isinstance(logs, dict):
                    logs = [logs]
                
                return {
                    "success": True,
                    "ui_type": "system_logs",
                    "logs": logs
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse log data.",
                    "ui_type": "system_logs"
                }
        else:
            return {
                "success": False,
                "error": f"Failed to run powershell command: {result.stderr}",
                "ui_type": "system_logs"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "system_logs"
        }


@tool
def list_apps() -> Dict[str, Any]:
    """
    Returns a list of installed applications on Windows via Winget.
    Use this when the user asks for 'installed apps', 'list applications', etc.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "installed_apps"
        }

    try:
        # Run winget list
        cmd = ["winget", "list", "--source", "winget"]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=60)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) < 3:
                return {"success": True, "ui_type": "installed_apps", "apps": []}
            
            # Find the header line and separator line to guess widths
            header_line = ""
            separator_line = ""
            for i, line in enumerate(lines):
                if "Name" in line and "Id" in line:
                    header_line = line
                    separator_line = lines[i+1]
                    start_idx = i + 2
                    break
            else:
                return {"success": False, "error": "Failed to parse winget output format.", "ui_type": "installed_apps"}

            # winget output is fixed width. Let's try to parse it by finding the column starts
            # Name                           Id                                         Version          Available        Source
            # -------------------------------------------------------------------------------------------------------------------
            
            apps = []
            for line in lines[start_idx:]:
                if not line.strip() or "---" in line: continue
                # Basic parsing: Name is the first large chunk, Id is the second
                # Since winget output can be complex, let's use a simpler heuristic or just return the raw lines 
                # but let's try a split and filter
                parts = [p.strip() for p in line.split("  ") if p.strip()]
                if len(parts) >= 3:
                    apps.append({
                        "name": parts[0],
                        "id": parts[1],
                        "version": parts[2],
                        "available": parts[3] if len(parts) > 4 else "N/A"
                    })
            
            return {
                "success": True,
                "ui_type": "installed_apps",
                "apps": apps[:50] # Limit to 50 for stability
            }
        else:
            return {
                "success": False,
                "error": f"Failed to run winget command: {result.stderr or result.stdout}",
                "ui_type": "installed_apps"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "installed_apps"
        }


@tool
def list_wmic_software() -> Dict[str, Any]:
    """
    Returns a list of installed software on Windows using WMIC (slower than winget).
    Use this when the user specifically asks for 'wmic software' or 
    to find legacy/MSI applications.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "wmic_software"
        }

    try:
        # Run wmic product get name,version /format:csv
        cmd = ["wmic", "product", "get", "name,version", "/format:csv"]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=120)
        
        if result.returncode == 0:
            import csv
            import io
            
            # wmic csv format has a leading blank line and the first column is the node name
            output = result.stdout.strip()
            if not output:
                return {"success": True, "ui_type": "wmic_software", "software": []}
                
            f = io.StringIO(output)
            reader = csv.DictReader(f)
            
            software = []
            for row in reader:
                if row.get("Name") and row.get("Version"):
                    software.append({
                        "name": row["Name"],
                        "version": row["Version"]
                    })
            
            return {
                "success": True,
                "ui_type": "wmic_software",
                "software": software
            }
        else:
            return {
                "success": False,
                "error": f"Failed to run wmic command: {result.stderr or result.stdout}",
                "ui_type": "wmic_software"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "wmic_software"
        }


@tool
def kill_process_by_pid(pid: int) -> Dict[str, Any]:
    """
    Forcefully terminate a process by its Process ID (PID) on Windows.
    Use this when the user asks to 'kill process', 'terminate PID', or similar.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "process_kill"
        }

    try:
        cmd = ["taskkill", "/F", "/PID", str(pid)]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=15)
        
        return {
            "success": result.returncode == 0,
            "data": result.stdout or result.stderr,
            "output": f"Process termination attempted for PID {pid}.",
            "ui_type": "process_kill",
            "target": f"PID: {pid}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "process_kill",
            "target": f"PID: {pid}"
        }

@tool
def kill_process_by_name(name: str) -> Dict[str, Any]:
    """
    Forcefully terminate a process by its Image Name (e.g., notepad.exe) on Windows.
    Use this when the user asks to 'kill notepad', 'terminate chrome.exe', or similar.
    """
    system = platform.system().lower()
    if system != "windows":
        return {
            "success": False,
            "error": "This tool is only supported on Windows.",
            "ui_type": "process_kill"
        }

    try:
        # Ensure name has .exe if missing, though taskkill handles it
        cmd = ["taskkill", "/IM", name, "/F"]
        result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=15)
        
        return {
            "success": result.returncode == 0,
            "data": result.stdout or result.stderr,
            "output": f"Process termination attempted for image: {name}.",
            "ui_type": "process_kill",
            "target": f"Name: {name}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ui_type": "process_kill",
            "target": f"Name: {name}"
        }
