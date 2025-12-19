"""
vibe lock command - Lock your design system.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from vibe.scanner import scan_directory
from vibe.analyzer import analyze_design_system
from vibe.lock.generator import generate_design_system

console = Console()


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing .vibe/system.json"
)
@click.option(
    "--output-dir",
    type=click.Path(),
    default=".vibe",
    help="Output directory for system.json"
)
def lock(path: str, force: bool, output_dir: str) -> None:
    """
    Lock your design system to .vibe/system.json.
    
    This captures your current design tokens (colors, spacing, typography, etc.)
    and saves them as your source of truth.
    
    Examples:
    
        vibe lock
        
        vibe lock --force
        
        vibe lock ./src --output-dir ./design-system
    """
    target_path = Path(path).resolve()
    output_path = Path(output_dir)
    system_file = output_path / "system.json"
    
    # Check if already exists
    if system_file.exists() and not force:
        if not Confirm.ask(
            f"[yellow]{system_file} already exists. Overwrite?[/yellow]"
        ):
            console.print("[dim]Aborted.[/dim]")
            return
    
    console.print()
    console.print(Panel.fit(
        f"[bold blue]🔒 Locking design system[/bold blue] from {target_path}",
        border_style="blue"
    ))
    console.print()
    
    # Step 1: Scan
    with console.status("[bold green]Scanning files..."):
        scan_result = scan_directory(target_path)
    
    # Step 2: Analyze
    with console.status("[bold green]Analyzing design system..."):
        analysis = analyze_design_system(scan_result)
    
    # Step 3: Generate locked system
    with console.status("[bold green]Generating design system..."):
        design_system = generate_design_system(analysis)
    
    # Step 4: Write to file
    output_path.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(system_file, "w") as f:
        json.dump(design_system.model_dump(), f, indent=2)
    
    console.print(f"[green]✓[/green] Design system locked to [bold]{system_file}[/bold]")
    console.print()
    
    # Summary
    console.print("[dim]Locked:[/dim]")
    console.print(f"  • {len(design_system.colors)} colors")
    console.print(f"  • {len(design_system.spacing.scale)} spacing values")
    console.print(f"  • {len(design_system.typography.font_sizes)} font sizes")
    console.print(f"  • {len(design_system.typography.font_families)} font families")
    console.print(f"  • {len(design_system.border_radius.scale)} border radius values")
    console.print()
    console.print(
        "Run [bold]vibe enforce[/bold] to start the MCP server "
        "and enforce your design system."
    )
