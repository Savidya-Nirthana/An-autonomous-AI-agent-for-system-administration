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
import re
from rich.live import Live
import time
import uuid

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style


user_name=""
def check_packages():
    packages = ["rich" ,"pyfiglet","getpass","sys","subprocess","importlib","os", "langchain"]
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"installing missing pacakges...")
            subprocess.check_call([sys.executable,"-m" , "pip", "install", package])

def welcome_banner():
    try:    
        console = Console() 
        ascii_banner = pyfiglet.figlet_format("Admin Mind",justify="center") 
        console.print(Text(ascii_banner, style="bold magenta", justify="right"))
    except:
        console.print(Text("Error on banner",style="bold red"))
        
def login_form():
    try:
        global user_name
        console = Console()
        
        console.print('[bold cyan]Enter Your username (Admin)[/bold cyan]:' , end=" ")
        user_name = console.input()
        
        console.print("[bold cyan]Enter Your password[/bold cyan]:", end=" ")
        user_password = getpass.getpass('')

        if user_name == 'Admin' and user_password == '123':
            session_id = f"{user_name}-{uuid.uuid4().hex[:8]}"
            clear_consol()
            return session_id

        else:
            console.print('[bold red]Not validated ,try again [/bold red]')
            exit_program()                
    except:
        console.print(Text("Login Fail!",style="bold red"))
        exit_program()

def welcome_msg():
    try:
        console = Console() 
        panel = Panel(Text("--- Hello! Welcome to Admin Mind by White house---", justify="center", style="bold  on green "))
        console.print(panel)
    except:
        console.print(Text("Error on welcome"))

def pending_message(message=""):
    console = Console()
    return console.status(f"[bold yellow]{message}[/bold yellow]", spinner="dots")
    
def live_update(responses=""):
    console = Console()
    with Live(console=console, refresh_per_second=4) as live:
        for response in responses:
            live.update(f"[bold yellow]{response}[/bold yellow]", )
            time.sleep(2)
        live.update("")

class FileCompleter(Completer):
    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        
        # Check if the user is typing a word that starts with '@'
        words = text_before_cursor.split()
        if not words:
            return
            
        last_word = words[-1]
        
        if last_word.startswith('@'):
            search_prefix = last_word[1:]  # Everything after '@'
            
            # List files in the current directory
            try:
                files = os.listdir('.')
                for file in files:
                    if file.startswith(search_prefix) and os.path.isfile(file):
                        # Yield completion
                        yield Completion(
                            file, 
                            start_position=-len(search_prefix),
                            display=file
                        )
            except Exception:
                pass


def get_requests(session_id: str):
    try:
        console = Console()
        
        # Define modern prompt style
        style = Style.from_dict({
            'username': 'ansicyan bold',
            'at': 'ansigreen bold',
            'session': 'ansicyan bold',
            'path': 'ansigreen bold',
            'pound': 'ansigreen bold',
        })
        
        cwd = os.getcwd()
        # Prompt toolkit uses formatted text
        prompt_text = HTML(f'<username>[{user_name}</username><at>@</at><session>{session_id}]</session>-<path>[{cwd}]</path>\n<pound>$ </pound>')
        
        session = PromptSession(completer=FileCompleter(), style=style)
        request = session.prompt(prompt_text)
        
        if request.lower() == "exit" : return False             #end the program
        if request.lower() == "pending" : pending_message(message = "")     #show pending screen
        resp =[ "Hello, how can I help?", "Here’s some context about your query...", "Final answer: use Rich Live to update dynamically!" ]
        if request.lower() == "liveupdate" : live_update(resp)  #to view live updates one by one at time

        if request == "" : return ""
        
        # Parse @filenames and read their contents
        file_contents = []
        words = request.split()
        
        for word in words:
            if word.startswith('@') and len(word) > 1:
                filename = word[1:]
                if os.path.isfile(filename):
                    try:
                        with open(filename, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_contents.append(f"\n--- Content of {filename} ---\n{content}\n--- End of {filename} ---")
                            console.print(f"[bold green]Added context from file: {filename}[/bold green]")
                    except Exception as e:
                        console.print(f"[bold red]Failed to read file {filename}: {e}[/bold red]")
                else:
                    console.print(f"[bold yellow]Warning: file '{filename}' not found.[/bold yellow]")

        print(f"your request is {request}")
        
        # Append file contents to the request sent to the LLM
        if file_contents:
            request += "\n\n" + "\n".join(file_contents)
            
        return request
    except (EOFError, KeyboardInterrupt):
        return False
    except Exception as e:
        console = Console()
        console.print(f"[bold red]Error on request: {e}[/bold red]")
        return ""

def exit_program():
    exit()
    
def clear_consol():
    sys.platform == "win32" and os.system("cls")
    sys.platform == "linux" or sys.platform == "darwin" and os.system("clear && printf '\033[3J'")
    
