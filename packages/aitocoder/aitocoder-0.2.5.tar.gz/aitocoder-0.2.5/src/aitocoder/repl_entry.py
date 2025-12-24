"""repl_entry.py

This module is the entry to the AitoCoder REPL.
"""
import sys
import warnings
from importlib.metadata import version

# Suppress all warnings
warnings.filterwarnings("ignore")
from login_modules import Auth, ModelManager
from autocoder.chat_auto_coder import main as autocoder_repl

from rich.console import Console
from rich.panel import Panel

import pwinput
from global_utils import clear_screen, COLORS

console = Console()
BLUE = COLORS.BLUE
ORANGE = COLORS.ORANGE

# Get version from package metadata (synced with pyproject.toml)
try:
    __version__ = version("aitocoder")
except Exception:
    __version__ = "v.beta"

def chat_login():
    """Simple login flow: prompt credentials, login, initialize models"""

    WelcomePanel = Panel(f"[bold {BLUE}]Welcome to[/bold {BLUE}]\n"
                         f"[bold][{ORANGE}]AitoCoder CLI - REPL[/bold][/{ORANGE}]\n"
                         f"[{ORANGE}]v{__version__}[/{ORANGE}]\n\n"
                         f"[{BLUE}]Type /help to see available commands.[/{BLUE}]\n"
                         f"[{BLUE}]─────────────────────────────────────[/{BLUE}]\n\n"
                         f"[{ORANGE}]>>[/{ORANGE}] [{BLUE}]Visit https://aitocoder.com \n   for sign-up, web platform and more.[/{BLUE}]\n\n"
                         f"[{ORANGE}]>>[/{ORANGE}] [{BLUE}]Ctrl+C to force quit a task.[/{BLUE}]\n"     
                         f"[{ORANGE}]>>[/{ORANGE}] [{BLUE}]Ctrl+D to exit.[/{BLUE}]",
                         title="beta", title_align="right",
                         width=50, border_style=f"{BLUE}",
                         padding=(1,3),
                         highlight=False)
    console.print(WelcomePanel)
    console.print()

    # Check if already logged in
    auth = Auth()
    if auth.is_authenticated():
        user = auth.get_user_info()
        username = user.get('user', {}).get('userName', 'User')
        console.print(f"[{BLUE}]Logged in:[/{BLUE}] {username}")

        # Check if models exist
        manager = ModelManager()
        info = manager.get_model_info()
        if info['model_count'] > 0:
            console.print(f"[{BLUE}]Models:[/{BLUE}] {info['model_count']} available")
            return True
        else:
            console.print(f"[{BLUE}]Initializing models...[/{BLUE}]")

    # Prompt for credentials
    username = console.input(f"[{BLUE}]Username:[/{BLUE}] ").strip()
    if not username:
        console.print("[red]Username required[/red]")
        return False

    if pwinput:
        console.print(f"[{BLUE}]Password:[/{BLUE}] ", end="")
        password = pwinput.pwinput(prompt="", mask="*")
    else:
        password = console.input(f"[{BLUE}]Password:[/{BLUE}] ", password=True)

    if not password:
        console.print("[red]Password required[/red]")
        return False

    # Login
    console.print(f"[{BLUE}]Logging in...[/{BLUE}]")
    if not auth.login(username, password):
        console.print("[red]Login failed[/red]")
        return False

    # Initialize models
    console.print(f"[{BLUE}]Initializing models...[/{BLUE}]")
    auth_data = auth.storage.load()
    token = auth_data.get("token")

    manager = ModelManager()
    if manager.initialize_models(token):
        console.print(f"\n[bold {BLUE}]Ready[/bold {BLUE}]")
        return True
    else:
        console.print("\n[yellow]Model initialization failed[/yellow]")
        console.print("[dim]Retry: python -m login_modules.chat_login[/dim]")
        return True  # Still logged in


def main():
    """Entry point"""
    try:
        chat_login()
        autocoder_repl()
    except KeyboardInterrupt:
        console.print(f"\n[{BLUE}]Cancelled[/{BLUE}]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
