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
import uuid


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

def get_requests():
    try:
        console = Console()
        console.print('[bold green]Request >>>[/bold green]' ,end=" ")
        request = console.input()
        
        if request.lower() == "exit" : return False             #end the program
        if request.lower() == "pending" : pending_message(message = "")     #show pending screen
        resp =[ "Hello, how can I help?", "Here’s some context about your query...", "Final answer: use Rich Live to update dynamically!" ]
        if request.lower() == "liveupdate" : live_update(resp)  #to view live updates one by one at time

        if request == "" : return ""
        print(f"your request is {request}")
        return request
    except :
        console.print("[bold red]Error on request[/bold red]")

def exit_program():
    exit()
    
def clear_consol():
    sys.platform == "win32" and os.system("cls")
    sys.platform == "linux" or sys.platform == "darwin" and os.system("clear && printf '\033[3J'")
    
