"""Main application module for test project."""

import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
import typer

app = typer.Typer()
console = Console()


@app.command()
def hello(name: str = "World") -> None:
    """Say hello to someone."""
    console.print(f"[green]Hello, {name}![/green]")


@app.command()
def serve(port: int = 8000, host: str = "localhost") -> None:
    """Start a simple server (simulated)."""
    console.print(
        Panel(
            f"[green]Server starting on {host}:{port}[/green]\n"
            "Press Ctrl+C to stop",
            title="Test Server",
            border_style="green",
        )
    )
    try:
        while True:
            time.sleep(1)
            console.print(f"[dim]Server running on {host}:{port}...[/dim]", end="\r")
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")


@app.command()
def version() -> None:
    """Show version information."""
    from test_project import __version__

    console.print(f"[bold]test-project[/bold] version [cyan]{__version__}[/cyan]")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()

