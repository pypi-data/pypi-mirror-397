"""
vibe serve command - Start MCP server for AI tools.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.option(
    "--system-file",
    type=click.Path(exists=True),
    default=".vibe/system.json",
    help="Path to locked design system"
)
def serve(system_file: str) -> None:
    """
    Start MCP server for AI tool integration.
    
    This is typically called automatically by Claude Desktop
    based on the MCP configuration. You can also run it manually
    for testing.
    
    \b
    Examples:
        vibe serve
        vibe serve --system-file ./custom/system.json
    """
    system_path = Path(system_file)
    
    if not system_path.exists():
        console.print(
            f"[red]Error:[/red] Design system not found at {system_path}"
        )
        console.print()
        console.print("Run [bold]vibe init[/bold] first to create your design system.")
        raise SystemExit(1)
    
    try:
        from vibe.mcp.server import start_server
        start_server(system_path)
    except ImportError as e:
        console.print("[red]Error:[/red] MCP package not installed.")
        console.print()
        console.print("Install with: [bold]pip install mcp[/bold]")
        console.print()
        console.print(f"[dim]Details: {e}[/dim]")
        raise SystemExit(1)
