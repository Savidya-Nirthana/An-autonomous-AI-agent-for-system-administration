from rich.prompt import Prompt
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.console import Console 
import pyfiglet
import importlib
import subprocess
import sys
import getpass
import os
from rich.live import Live
import time

# def check_packages():
#     packages = ["rich", "pyfiglet", "langchain", "redis", "psycopg2", "bcrypt", "python-dotenv"]
#     for package in packages:
#         module_name = "dotenv" if package == "python-dotenv" else package
#         try:
#             importlib.import_module(package)
#         except ImportError:
#             print(f"installing missing packages: {package}...")
            
#             # Detect if running in uv environment
#             if os.getenv("VIRTUAL_ENV") and "uv" in os.getenv("VIRTUAL_ENV", ""):
#                 # Use uv pip
#                 subprocess.check_call(["uv", "pip", "install", package])
#             else:
#                 # Use regular pip
#                 subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def welcome_banner():
    try:    
        console = Console() 
        ascii_banner = pyfiglet.figlet_format("Admin Mind", justify="center") 
        console.print(Text(ascii_banner, style="bold magenta", justify="right"))
    except:
        console.print(Text("Error on banner", style="bold red"))

def login_form(auth_manager):
    """
    Login form with authentication
    Returns: session_id if successful, None if failed
    """
    try:
        console = Console()
        max_attempts = 3
        
        for attempt in range(max_attempts):
            console.print('[bold cyan]Enter Your username[/bold cyan]:', end=" ")
            user_name = console.input()
            
            console.print("[bold cyan]Enter Your password[/bold cyan]:", end=" ")
            user_password = getpass.getpass('')
            
            # Authenticate user
            session_id = auth_manager.login(user_name, user_password)
            
            if session_id:
                clear_consol()
                console.print(f'[bold green]✓ Login successful! Session: {session_id}[/bold green]')
                return session_id
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    console.print(f'[bold red]✗ Invalid credentials. {remaining} attempts remaining.[/bold red]')
                else:
                    console.print('[bold red]✗ Maximum login attempts exceeded.[/bold red]')
                    
        return None
                    
    except Exception as e:
        console.print(f'[bold red]Login Error: {e}[/bold red]')
        return None

def welcome_msg():
    try:
        console = Console() 
        panel = Panel(Text("--- Hello! Welcome to Admin Mind by White house---", justify="center", style="bold on green"))
        console.print(panel)
    except:
        console.print(Text("Error on welcome"))

def pending_message(message=""):
    try:
        console = Console()
        with console.status(f"[bold yellow]{message}[/bold yellow]", spinner="aesthetic"): 
            time.sleep(10)
    except:
        console.print("[bold red]Error on pending...[/bold red]")
    
def live_update(responses=""):
    console = Console()
    with Live(console=console, refresh_per_second=4) as live:
        for response in responses:
            live.update(f"[bold yellow]{response}[/bold yellow]")
            time.sleep(2)
        live.update("")

def get_requests():
    try:
        console = Console()
        console.print('[bold green]Request >>>[/bold green]', end=" ")
        request = console.input()
        
        if request.lower() == "exit" or request.lower() == "logout":
            return False  # Signal to exit/logout
            
        if request.lower() == "pending":
            pending_message(message="")
            return True  # Continue but don't process as command
            
        if request.lower() == "liveupdate":
            resp = [
                "Hello, how can I help?", 
                "Here's some context about your query...", 
                "Final answer: use Rich Live to update dynamically!"
            ]
            live_update(resp)
            return True  # Continue but don't process as command
        
        return request
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Session interrupted[/bold yellow]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error on request: {e}[/bold red]")
        return True

def logout_message(auth_manager, session_id):
    """Display logout message and destroy session"""
    try:
        console = Console()
        
        # Destroy session
        if auth_manager.logout(session_id):
            console.print('[bold green]✓ Logged out successfully. All session data cleared.[/bold green]')
            console.print('[bold cyan]Goodbye! 👋[/bold cyan]')
        else:
            console.print('[bold yellow]⚠ Logout completed (session may have expired)[/bold yellow]')
            
    except Exception as e:
        console.print(f'[bold red]Logout error: {e}[/bold red]')

def session_info(auth_manager, session_id):
    """Display current session information"""
    try:
        console = Console()
        session_data = auth_manager.get_session_info(session_id)
        
        if session_data:
            ttl = auth_manager.session_manager.get_session_ttl(session_id)
            console.print(Panel(
                f"[bold cyan]User:[/bold cyan] {session_data['username']}\n"
                f"[bold cyan]Session ID:[/bold cyan] {session_id}\n"
                f"[bold cyan]Created:[/bold cyan] {session_data['created_at']}\n"
                f"[bold cyan]Last Activity:[/bold cyan] {session_data['last_activity']}\n"
                f"[bold cyan]Time Remaining:[/bold cyan] {ttl} seconds",
                title="[bold green]Session Info[/bold green]",
                border_style="green"
            ))
        else:
            console.print('[bold red]Session not found or expired[/bold red]')
            
    except Exception as e:
        console.print(f'[bold red]Error getting session info: {e}[/bold red]')

def exit_program():
    exit()
    
def clear_consol():
    if sys.platform == "win32":
        os.system("cls")
    elif sys.platform == "linux" or sys.platform == "darwin":
        os.system("clear && printf '\\033[3J'")