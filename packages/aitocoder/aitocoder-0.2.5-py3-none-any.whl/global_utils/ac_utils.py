import sys
from rich.console import Console

def clear_screen(console):
    """Clear the terminal screen and scrollback buffer."""

    console.clear()
    try:
        sys.stdout.write('\033[3J')
        sys.stdout.flush()
    except:
        pass

