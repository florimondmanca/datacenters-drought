from rich.console import Console

_console = Console()


def success(text: str) -> None:
    _console.print(text, style="bold green")


def info(text: str) -> None:
    _console.print(text, style="bold blue")
