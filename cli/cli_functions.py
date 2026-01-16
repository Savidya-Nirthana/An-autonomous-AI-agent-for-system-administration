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


def check_packages():
    packages = ["rich" ,"pyfiglet","getpass","sys","subprocess","importlib","os"]
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
            clear_consol()
            return
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

def get_requests():
    try:
        console = Console()
        
        console.print('[bold green]Request >>>[/bold green]' ,end=" ")
        request = console.input()
        
        if request.lower() == "exit" : return False

        print(f"your request is {request}")
        return True
    except :
        console.print("[bold red]Error on request[/bold red]")

def exit_program():
    exit()
    
def clear_consol():
    sys.platform == "win32" and os.system("cls")
    sys.platform == "linux" or sys.platform == "darwin" and os.system("clear && printf '\033[3J'")
    
