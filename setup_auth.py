"""
One-time setup script to initialize database and create admin user
Run this before first use: python setup_auth.py
"""

from auth.auth_manager import AuthManager
from rich.console import Console
from rich.prompt import Prompt
import getpass

console = Console()

def main():
    console.print("[bold cyan]Admin Mind - Authentication Setup[/bold cyan]\n")
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Initialize database tables
    console.print("[yellow]Initializing database tables...[/yellow]")
    try:
        auth_manager.initialize()
        console.print("[green]✓ Database tables created successfully[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Database initialization failed: {e}[/red]")
        return
    
    # Create admin user
    console.print("[bold]Create Admin User[/bold]")
    
    while True:
        username = Prompt.ask("[cyan]Enter admin username[/cyan]")
        
        if len(username) < 3:
            console.print("[red]Username must be at least 3 characters[/red]")
            continue
        
        console.print("[cyan]Enter admin password[/cyan]:", end=" ")
        password = getpass.getpass('')
        
        if len(password) < 4:
            console.print("[red]Password must be at least 4 characters[/red]")
            continue
        
        console.print("[cyan]Confirm password[/cyan]:", end=" ")
        password_confirm = getpass.getpass('')
        
        if password != password_confirm:
            console.print("[red]Passwords do not match. Try again.[/red]\n")
            continue
        
        # Create user
        if auth_manager.register_user(username, password):
            console.print(f"\n[green]✓ Admin user '{username}' created successfully![/green]")
            break
        else:
            console.print(f"[red]✗ User '{username}' already exists. Choose a different username.[/red]\n")
    
    # Create additional users (optional)
    while True:
        add_more = Prompt.ask("\n[cyan]Add another user?[/cyan]", choices=["y", "n"], default="n")
        
        if add_more == "n":
            break
        
        username = Prompt.ask("[cyan]Enter username[/cyan]")
        console.print("[cyan]Enter password[/cyan]:", end=" ")
        password = getpass.getpass('')
        
        if auth_manager.register_user(username, password):
            console.print(f"[green]✓ User '{username}' created successfully![/green]")
        else:
            console.print(f"[red]✗ User '{username}' already exists.[/red]")
    
    console.print("\n[bold green]Setup complete! You can now run: uv run main.py[/bold green]")
    
    # Close connections
    auth_manager.close()

if __name__ == "__main__":
    main()