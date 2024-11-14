from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_nice(content):
    text = Text(content)
    text.justify = "left"
    panel = Panel(text, expand=False, border_style="blue")
    console.print(panel)
