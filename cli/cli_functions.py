"""
cli/cli_functions.py — CLI helpers with PostgreSQL-backed auth system.
"""

from __future__ import annotations

import ctypes
import getpass
import importlib
import os
import platform
import re
import subprocess
import sys
import time
import uuid
from typing import Optional

import pyfiglet
from rich import print
from rich.console import Console
from rich.live import Live
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

# ── Auth imports ──────────────────────────────────────────────────────────────
from auth import auth_service, get_db, User, UserRole
from auth.models import SessionLocal

console = Console()

# Module-level state (populated after successful login)
current_user: Optional[User] = None
current_session_id: Optional[str] = None


# ── Package check ─────────────────────────────────────────────────────────────

def check_packages() -> None:
    packages = ["rich", "pyfiglet", "bcrypt", "sqlalchemy", "psycopg2",
                "getpass", "subprocess", "importlib", "os", "langchain"]
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
        Text("--- Hello! Welcome to Admin Mind by White house ---",
             justify="center", style="bold on green")
    )
    console.print(panel)


# ── System elevation helpers ──────────────────────────────────────────────────

#----system administrator-------
def is_windows() -> bool:
    return platform.system() == "Windows"


def is_elevated() -> bool:
    """Check if the current process is running with Administrator privileges."""
    if not is_windows():
        # On Linux/macOS, check for root (uid 0) — analogous to sudo
        return os.getuid() == 0
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def requires_elevation(user: "User") -> bool:
    """Return True if this role requires elevated privileges."""
    from auth import UserRole
    return user.role in (UserRole.admin, UserRole.root_admin)


def elevate_if_needed(user: "User") -> None:
    """
    If the user's role requires elevation and the process is not yet elevated,
    re-launch this script as Administrator (Windows UAC) or with sudo (Unix).
    Exits the current (unelevated) process after spawning the elevated one.
    """
    if not requires_elevation(user):
        return  # Regular users: no elevation needed or allowed

    if is_elevated():
        console.print(
            f"[bold green]✓ Running as Administrator "
            f"(elevated privileges active)[/bold green]"
        )
        return  # Already elevated — carry on

    # ── Not elevated yet ──────────────────────────────────────────────────────
    console.print(
        f"\n[bold yellow]⚠  Role '[cyan]{user.role.value}[/cyan]' requires "
        f"elevated (Administrator) privileges.[/bold yellow]"
    )

    if is_windows():
        _elevate_windows()
    else:
        _elevate_unix()

def _elevate_windows() -> None:
    import ctypes

    console.print(
        "[bold cyan]A UAC prompt will appear. "
        "Please click 'Yes' to continue as Administrator.[/bold cyan]\n"
    )
    time.sleep(1)

    script = os.path.abspath(sys.argv[0])

    # Build args without any existing --session_id
    old_args = []
    skip_next = False
    for a in sys.argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if a.startswith("--session_id"):
            if "=" not in a:
                skip_next = True
            continue
        old_args.append(a)

    # Pass session_id via env var instead — it's available before login completes
    args = f'"{script}"'
    if old_args:
        args += " " + " ".join(f'"{a}"' for a in old_args)

    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,   # ← python.exe directly, NOT cmd.exe
        args,
        os.getcwd(),      # ← Provide the current working directory
        1,
    )

    if ret <= 32:
        console.print(
            f"[bold red]UAC elevation failed or was denied "
            f"(code {ret}). Exiting.[/bold red]"
        )
        sys.exit(1)

    console.print("[yellow]Elevated process launched. This window will close.[/yellow]")
    sys.exit(0)

def _elevate_unix() -> None:
    """Re-launch under sudo on Linux / macOS."""
    console.print(
        "[bold cyan]Relaunching with sudo — enter your system password "
        "if prompted.[/bold cyan]\n"
    )
    time.sleep(0.5)

    cmd = ["sudo", sys.executable] + sys.argv
    try:
        os.execvp("sudo", cmd)   # replaces current process — no sys.exit needed
    except FileNotFoundError:
        console.print("[bold red]'sudo' not found. Cannot elevate.[/bold red]")
        sys.exit(1)


# ── Login ─────────────────────────────────────────────────────────────────────

def login_form() -> Optional[str]:
    """
    Interactive login backed by the PostgreSQL auth system.
    Returns a session_id string on success, or None on failure.
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

        # Cache the User object for this process lifetime
        db = SessionLocal()
        try:
            from auth.models import Session as DBSession, User as DBUser
            sess_row = db.query(DBSession).filter_by(session_id=session_id).first()
            current_user = db.query(DBUser).filter_by(id=sess_row.user_id).first()
            db.expunge(current_user)   # detach so we can use it outside the session
        finally:
            db.close()

        current_session_id = session_id
        clear_console()
        _print_role_banner(current_user)

        # ── NEW: elevate immediately after successful login ────────────────
        elevate_if_needed(current_user)

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


# ── Per-request session validation ────────────────────────────────────────────

def validate_current_session() -> Optional[User]:
    """
    Re-validate the active session on every request.
    Returns the User if valid, or None (with error printed) otherwise.
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


# ── Root-admin user management commands ───────────────────────────────────────

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
        new_user, error = auth_service.create_user(current_user, username, password, role, db)
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

    table = Table(title="Registered Users", show_header=True, header_style="bold cyan")
    table.add_column("ID",       style="dim",    width=6)
    table.add_column("Username", style="white",  min_width=16)
    table.add_column("Role",     style="yellow", min_width=12)
    table.add_column("Active",   style="green",  width=8)
    table.add_column("Last Login")

    for u in users:
        table.add_row(
            str(u.id), u.username, u.role.value,
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
        ok, error = auth_service.reset_password(current_user, username, new_password, db)
    finally:
        db.close()

    if error:
        console.print(f"[bold red]Error:[/bold red] {error}")
    else:
        console.print(f"[bold green]Password reset for '{username}'.[/bold green]")


# ── Help command ──────────────────────────────────────────────────────────────

def _cmd_help() -> None:
    table = Table(title="Available Commands", header_style="bold cyan")
    table.add_column("Command",     style="green")
    table.add_column("Description", style="white")
    table.add_column("Role",        style="yellow")

    all_commands = [
        ("help",           "Show this help",              "all"),
        ("exit",           "Logout and quit",             "all"),
        ("adduser",        "Create a new user",           "root_admin"),
        ("listusers",      "List all users",              "root_admin"),
        ("deactivateuser", "Deactivate a user account",   "root_admin"),
        ("resetpassword",  "Reset a user's password",     "root_admin"),
    ]

    role = current_user.role.value if current_user else "unknown"
    for cmd, desc, required_role in all_commands:
        if required_role == "all" or role == required_role:
            table.add_row(cmd, desc, required_role)

    console.print(table)


# ── File completer (@filename autocomplete) ───────────────────────────────────

class FileCompleter(Completer):
    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        words = text_before_cursor.split()
        if not words:
            return

        last_word = words[-1]
        if last_word.startswith('@'):
            search_prefix = last_word[1:]
            try:
                files = os.listdir('.')
                for file in files:
                    if file.startswith(search_prefix) and os.path.isfile(file):
                        yield Completion(
                            file,
                            start_position=-len(search_prefix),
                            display=file
                        )
            except Exception:
                pass


# ── Main prompt loop ──────────────────────────────────────────────────────────

def get_requests(session_id: str) -> str | bool:
    try:
        username = current_user.username if current_user else "unknown"

        style = Style.from_dict({
            'username': 'ansicyan bold',
            'at':       'ansigreen bold',
            'session':  'ansicyan bold',
            'path':     'ansigreen bold',
            'pound':    'ansigreen bold',
        })

        cwd = os.getcwd()
        prompt_text = HTML(
            f'<username>[{username}</username>'
            f'<at>@</at>'
            f'<session>{session_id}]</session>'
            f'-<path>[{cwd}]</path>\n'
            f'<pound>$ </pound>'
        )

        session = PromptSession(completer=FileCompleter(), style=style)
        request = session.prompt(prompt_text)

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
        if request.lower() == "help":
            _cmd_help(); return ""

        # ── Session validation on every request ───────────────────────────────
        user = validate_current_session()
        if user is None:
            return False

        if request == "":
            return ""

        # ── Prompt length guard ───────────────────────────────────────────────
        limit = get_prompt_limit()
        if len(request) > limit:
            console.print(
                f"[bold red]Prompt too long.[/bold red] "
                f"Your role allows max {limit} characters."
            )
            return ""

        # ── Parse @filenames and append their content ─────────────────────────
        file_contents = []
        words = request.split()

        for word in words:
            if word.startswith('@') and len(word) > 1:
                filename = word[1:]
                if os.path.isfile(filename):
                    try:
                        with open(filename, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_contents.append(
                                f"\n--- Content of {filename} ---\n{content}\n--- End of {filename} ---"
                            )
                            console.print(f"[bold green]Added context from file: {filename}[/bold green]")
                        request = request.replace(word, os.path.abspath(filename))
                    except Exception as e:
                        console.print(f"[bold red]Failed to read file {filename}: {e}[/bold red]")
                else:
                    console.print(f"[bold yellow]Warning: file '{filename}' not found.[/bold yellow]")

        console.print(f"your request is {request}")

        if file_contents:
            request += "\n\n" + "\n".join(file_contents)

        return request

    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
        return ""
    except Exception as e:
        console.print(f"[bold red]Error on request: {e}[/bold red]")
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


def live_update(responses: list = ()) -> None:
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


# Keep old name as alias for backward compat with any callers using clear_consol()
clear_consol = clear_console
