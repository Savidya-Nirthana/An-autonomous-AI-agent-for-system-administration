"""
cli/cli_functions.py — CLI helpers with PostgreSQL-backed auth system.
"""

from __future__ import annotations

import getpass
import importlib
import os
import subprocess
import sys
import time
import uuid
from typing import Optional

import pyfiglet
from rich import print
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.markup import escape

# ── Auth imports ──────────────────────────────────────────────────────────────
from auth import auth_service, get_db, User, UserRole
from auth.models import SessionLocal

console = Console()

# Module-level state (populated after successful login)
current_user: Optional[User] = None
current_session_id: Optional[str] = None


# ── Package check ─────────────────────────────────────────────────────────────

def check_packages() -> None:
    packages = ["rich", "pyfiglet", "bcrypt", "sqlalchemy", "psycopg2"]
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            console.print(f"[yellow]Installing missing package: {package}[/yellow]")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# ── Banners / messages ────────────────────────────────────────────────────────

def welcome_banner() -> None:
    try:
        ascii_banner = pyfiglet.figlet_format("Admin Mind", justify="center")
        console.print(Text(ascii_banner, style="bold magenta", justify="right"))
    except Exception:
        console.print(Text("AdminMind", style="bold magenta"))


def welcome_msg() -> None:
    panel = Panel(
        Text("--- Hello! Welcome to Admin Mind ---", justify="center",
             style="bold on green")
    )
    console.print(panel)


# ── Login ─────────────────────────────────────────────────────────────────────

def login_form() -> Optional[str]:
    """
    Interactive login.  Returns a session_id string on success, or None
    (after printing the error) so the caller can decide whether to retry
    or exit.
    """
    global current_user, current_session_id

    try:
        console.print("[bold cyan]Username[/bold cyan]:", end=" ")
        username = console.input().strip()

        console.print("[bold cyan]Password[/bold cyan]:", end=" ")
        password = getpass.getpass("")

        db = SessionLocal()
        try:
            session_id, error = auth_service.login(username, password, db)
        finally:
            db.close()

        if error:
            console.print(f"[bold red]Login failed:[/bold red] {error}")
            return None

        # Cache user for this process lifetime
        db = SessionLocal()
        try:
            from auth.models import Session as DBSession, User as DBUser
            sess_row = db.query(DBSession).filter_by(session_id=session_id).first()
            current_user = db.query(DBUser).filter_by(id=sess_row.user_id).first()
            db.expunge(current_user)          # detach so we can use outside session
        finally:
            db.close()

        current_session_id = session_id
        clear_console()
        _print_role_banner(current_user)
        return session_id

    except KeyboardInterrupt:
        console.print("\n[yellow]Login cancelled.[/yellow]")
        return None
    except Exception as exc:
        console.print(f"[bold red]Login error:[/bold red] {exc}")
        return None


def _print_role_banner(user: User) -> None:
    role_colours = {
        "root_admin": "bold red",
        "admin":      "bold yellow",
        "user":       "bold green",
    }
    colour = role_colours.get(user.role.value, "white")
    console.print(
        Panel(
            Text(
                f"Logged in as [b]{user.username}[/b]  |  role: [{colour}]{user.role.value}[/{colour}]",
                justify="center",
            )
        )
    )


# ── Per-request validation ────────────────────────────────────────────────────

def validate_current_session() -> Optional[User]:
    """
    Re-validate the active session on every request.
    Returns the User if valid, prints an error and returns None otherwise.
    """
    if not current_session_id:
        console.print("[bold red]No active session.[/bold red]")
        return None

    db = SessionLocal()
    try:
        user, error = auth_service.validate_session(current_session_id, db)
        if error:
            console.print(f"[bold red]Session error:[/bold red] {error}")
            return None
        auth_service.increment_request_count(current_session_id, db)
        return user
    finally:
        db.close()


def check_tool_permission(tool_name: str) -> bool:
    """Return True if the current user may use the given tool."""
    if current_user is None:
        return False
    allowed = auth_service.can_use_tool(current_user, tool_name)
    if not allowed:
        console.print(
            f"[bold red]Access denied:[/bold red] your role "
            f"([yellow]{current_user.role.value}[/yellow]) cannot use "
            f"tool '[cyan]{tool_name}[/cyan]'."
        )
    return allowed


def get_prompt_limit() -> int:
    if current_user is None:
        return 500
    return auth_service.get_prompt_limit(current_user)


# ── Root-admin user management ────────────────────────────────────────────────

def admin_create_user() -> None:
    """Interactive prompt to create a new user (root_admin only)."""
    if current_user is None or current_user.role != UserRole.root_admin:
        console.print("[bold red]Permission denied.[/bold red]")
        return

    console.print("[bold cyan]New username[/bold cyan]:", end=" ")
    username = console.input().strip()

    console.print("[bold cyan]New password[/bold cyan]:", end=" ")
    password = getpass.getpass("")

    console.print("[bold cyan]Role (admin / user)[/bold cyan]:", end=" ")
    role = console.input().strip().lower()

    db = SessionLocal()
    try:
        new_user, error = auth_service.create_user(
            current_user, username, password, role, db
        )
        if error:
            console.print(f"[bold red]Error:[/bold red] {error}")
        else:
            console.print(
                f"[bold green]User '{new_user.username}' created "
                f"with role '{new_user.role.value}'.[/bold green]"
            )
    finally:
        db.close()


def admin_list_users() -> None:
    if current_user is None or current_user.role != UserRole.root_admin:
        console.print("[bold red]Permission denied.[/bold red]")
        return

    db = SessionLocal()
    try:
        users = auth_service.list_users(current_user, db)
    finally:
        db.close()

    from rich.table import Table
    table = Table(title="Registered Users", show_header=True,
                  header_style="bold cyan")
    table.add_column("ID",       style="dim",    width=6)
    table.add_column("Username", style="white",  min_width=16)
    table.add_column("Role",     style="yellow", min_width=12)
    table.add_column("Active",   style="green",  width=8)
    table.add_column("Last Login")

    for u in users:
        table.add_row(
            str(u.id),
            u.username,
            u.role.value,
            "✓" if u.is_active else "✗",
            str(u.last_login)[:19] if u.last_login else "—",
        )
    console.print(table)


def admin_deactivate_user() -> None:
    if current_user is None or current_user.role != UserRole.root_admin:
        console.print("[bold red]Permission denied.[/bold red]")
        return

    console.print("[bold cyan]Username to deactivate[/bold cyan]:", end=" ")
    username = console.input().strip()

    db = SessionLocal()
    try:
        ok, error = auth_service.deactivate_user(current_user, username, db)
    finally:
        db.close()

    if error:
        console.print(f"[bold red]Error:[/bold red] {error}")
    else:
        console.print(f"[bold green]User '{username}' deactivated.[/bold green]")


def admin_reset_password() -> None:
    if current_user is None or current_user.role != UserRole.root_admin:
        console.print("[bold red]Permission denied.[/bold red]")
        return

    console.print("[bold cyan]Username[/bold cyan]:", end=" ")
    username = console.input().strip()
    console.print("[bold cyan]New password[/bold cyan]:", end=" ")
    new_password = getpass.getpass("")

    db = SessionLocal()
    try:
        ok, error = auth_service.reset_password(
            current_user, username, new_password, db
        )
    finally:
        db.close()

    if error:
        console.print(f"[bold red]Error:[/bold red] {error}")
    else:
        console.print(f"[bold green]Password reset for '{username}'.[/bold green]")


# ── Main prompt loop helpers ──────────────────────────────────────────────────

def get_requests(session_id: str) -> str | bool:
    try:
        username = current_user.username if current_user else "unknown"
        safe_user = escape(username)
        safe_session = escape(session_id)
        safe_cwd = escape(os.getcwd())
        console.print(
            f"[bold green]\\[{safe_user}@{safe_session}]-\\[{safe_cwd}][/bold green]\n",
            end="",
        )
        console.print("[bold green]$[/bold green]", end=" ")
        request = console.input()

        if request.lower() == "exit":
            _do_logout(session_id)
            return False

        # ── Root-admin management commands ────────────────────────────────────
        if request.lower() == "adduser":
            admin_create_user(); return ""
        if request.lower() == "listusers":
            admin_list_users(); return ""
        if request.lower() == "deactivateuser":
            admin_deactivate_user(); return ""
        if request.lower() == "resetpassword":
            admin_reset_password(); return ""

        # ── Session validation on every request ───────────────────────────────
        user = validate_current_session()
        if user is None:
            return False

        if request == "":
            return ""

        # Enforce prompt length limit
        limit = get_prompt_limit()
        if len(request) > limit:
            console.print(
                f"[bold red]Prompt too long.[/bold red] "
                f"Your role allows max {limit} characters."
            )
            return ""

        return request

    except KeyboardInterrupt:
        console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
        return ""
    except Exception as exc:
        console.print(f"[bold red]Input error:[/bold red] {exc}")
        return ""


def _do_logout(session_id: str) -> None:
    db = SessionLocal()
    try:
        auth_service.logout(session_id, db)
    finally:
        db.close()
    console.print("[bold yellow]Session ended. Goodbye![/bold yellow]")


# ── Misc helpers ──────────────────────────────────────────────────────────────

def pending_message(message: str = "") -> object:
    return console.status(f"[bold yellow]{message}[/bold yellow]", spinner="dots")


def live_update(responses: list[str] = ()) -> None:
    with Live(console=console, refresh_per_second=4) as live:
        for response in responses:
            live.update(f"[bold yellow]{response}[/bold yellow]")
            time.sleep(2)
        live.update("")


def exit_program() -> None:
    sys.exit(0)


def clear_console() -> None:
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear && printf '\\033[3J'")