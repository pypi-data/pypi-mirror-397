"""
vibe enforce command - Start MCP server for AI enforcement.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.option(
    "--port",
    type=int,
    default=3000,
    help="Port to run MCP server on"
)
@click.option(
    "--system-file",
    type=click.Path(exists=True),
    default=".vibe/system.json",
    help="Path to locked design system"
)
def enforce(port: int, system_file: str) -> None:
    """
    Start MCP server to enforce your design system.
    
    The MCP server provides your locked design system to AI tools
    (Claude, Cursor) so generated code follows your standards.
    
    Examples:
    
        vibe enforce
        
        vibe enforce --port 8080
        
        vibe enforce --system-file ./custom/system.json
    """
    system_path = Path(system_file)
    
    if not system_path.exists():
        console.print(
            f"[red]Error:[/red] Design system not found at {system_path}"
        )
        console.print()
        console.print("Run [bold]vibe lock[/bold] first to create your design system.")
        raise SystemExit(1)
    
    console.print()
    console.print(Panel.fit(
        f"[bold green]🚀 Starting MCP Server[/bold green]",
        border_style="green"
    ))
    console.print()
    console.print(f"  Design system: [bold]{system_path}[/bold]")
    console.print(f"  Port: [bold]{port}[/bold]")
    console.print()
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    console.print()
    
    # TODO: Implement MCP server
    # For now, placeholder
    try:
        from vibe.mcp.server import start_server
        start_server(system_path, port)
    except ImportError:
        console.print("[yellow]MCP server not yet implemented.[/yellow]")
        console.print()
        console.print("Coming soon! For now, you can use the .vibe/system.json")
        console.print("file directly in your AI prompts or .cursorrules.")
