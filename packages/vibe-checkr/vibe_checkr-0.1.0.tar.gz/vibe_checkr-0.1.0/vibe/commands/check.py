"""
vibe check command - Scan for design inconsistencies.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from vibe.scanner import scan_directory
from vibe.analyzer import analyze_design_system
from vibe.reporter.console import ConsoleReporter

console = Console()


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "-o", "--output",
    type=click.Choice(["console", "json", "markdown"]),
    default="console",
    help="Output format"
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to vibe config file"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Show detailed output"
)
def check(path: str, output: str, config: str | None, verbose: bool) -> None:
    """
    Scan for design inconsistencies in your codebase.
    
    PATH is the directory to scan (defaults to current directory).
    
    Examples:
    
        vibe check
        
        vibe check ./src
        
        vibe check --output json > report.json
    """
    target_path = Path(path).resolve()
    
    console.print()
    console.print(Panel.fit(
        f"[bold blue]🔍 Scanning[/bold blue] {target_path}",
        border_style="blue"
    ))
    console.print()
    
    # Step 1: Scan files and extract design tokens
    with console.status("[bold green]Scanning files..."):
        scan_result = scan_directory(target_path)
    
    if verbose:
        console.print(f"  Found {scan_result.files_scanned} files")
        console.print(f"  Extracted {scan_result.total_classes} Tailwind classes")
        console.print(f"  Extracted {scan_result.total_css_properties} CSS properties")
        console.print()
    
    # Step 2: Analyze for inconsistencies
    with console.status("[bold green]Analyzing design system..."):
        analysis = analyze_design_system(scan_result)
    
    # Step 3: Report results
    if output == "console":
        reporter = ConsoleReporter(console, verbose=verbose)
        reporter.report(analysis)
        
        # Next steps
        console.print()
        if analysis.has_issues:
            console.print("[dim]Next:[/dim] Fix errors above, then run [bold]vibe lock[/bold] to save your design system.")
        else:
            console.print("[dim]Next:[/dim] Run [bold]vibe lock[/bold] to save your design system.")
    elif output == "json":
        from vibe.reporter.json_report import JsonReporter
        json_reporter = JsonReporter()
        click.echo(json_reporter.report(analysis))
    elif output == "markdown":
        from vibe.reporter.markdown import MarkdownReporter
        md_reporter = MarkdownReporter()
        click.echo(md_reporter.report(analysis))
