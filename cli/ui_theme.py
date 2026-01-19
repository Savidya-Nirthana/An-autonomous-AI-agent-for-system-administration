from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "title": "bold cyan",
    "success": "bold green",
    "error": "bold red",
    "key": "bold yellow",
    "value": "white",
})

console = Console(theme=custom_theme)