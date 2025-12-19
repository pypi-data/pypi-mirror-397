"""
vibe init command - One-command setup for design system + AI enforcement.
"""

import json
import os
import platform
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from vibe.scanner import scan_directory
from vibe.analyzer import analyze_design_system
from vibe.lock.generator import generate_design_system
from vibe.reporter.console import ConsoleReporter

console = Console()


def get_claude_desktop_config_path() -> Path:
    """Get the Claude Desktop config path for the current platform."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"


def get_cursor_mcp_config_path() -> Path:
    """Get the Cursor MCP config path."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / ".cursor" / "mcp.json"
    elif system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Cursor" / "mcp.json"
    else:  # Linux
        return Path.home() / ".config" / "cursor" / "mcp.json"


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "--skip-mcp",
    is_flag=True,
    help="Skip MCP server configuration"
)
@click.option(
    "--skip-rules",
    is_flag=True,
    help="Skip .cursorrules and CLAUDE.md generation"
)
@click.option(
    "-y", "--yes",
    is_flag=True,
    help="Skip confirmation prompts"
)
def init(path: str, skip_mcp: bool, skip_rules: bool, yes: bool) -> None:
    """
    Initialize design system with full AI enforcement setup.
    
    This command will:
    
    1. Scan your codebase for design tokens
    
    2. Lock your design system to .vibe/system.json
    
    3. Generate .cursorrules and CLAUDE.md for AI tools
    
    4. Configure MCP server for Claude Desktop
    
    \b
    Examples:
        vibe init
        vibe init ./src
        vibe init --skip-mcp
    """
    target_path = Path(path).resolve()
    
    console.print()
    console.print(Panel.fit(
        "[bold blue]🚀 Vibe Check - Design System Setup[/bold blue]",
        border_style="blue"
    ))
    console.print()
    
    # Step 1: Scan
    console.print("[bold]Step 1/4:[/bold] Scanning codebase...")
    with console.status("[green]Scanning files..."):
        scan_result = scan_directory(target_path)
    console.print(f"  Found {scan_result.files_scanned} files, {scan_result.total_classes} Tailwind classes")
    
    # Step 2: Analyze
    console.print("[bold]Step 2/4:[/bold] Analyzing design system...")
    with console.status("[green]Analyzing..."):
        analysis = analyze_design_system(scan_result)
    
    # Show quick summary
    if analysis.has_issues:
        reporter = ConsoleReporter(console, verbose=False)
        reporter.report(analysis)
        console.print()
        
        # Count errors vs warnings vs suggestions
        actions = reporter._collect_actions(analysis)
        errors = [a for a in actions if a.severity == "error"]
        warnings = [a for a in actions if a.severity == "warning"]
        suggestions = [a for a in actions if a.severity == "info"]
        
        if not yes:
            # Build prompt message based on what was found
            if errors:
                prompt_msg = f"[red]{len(errors)} error(s)[/red] found. Lock anyway?"
                default_choice = False
            elif warnings:
                prompt_msg = f"[yellow]{len(warnings)} warning(s)[/yellow] found. Lock anyway?"
                default_choice = True
            else:
                prompt_msg = f"[blue]{len(suggestions)} suggestion(s)[/blue] found. Lock anyway?"
                default_choice = True
            
            if not Confirm.ask(prompt_msg, default=default_choice):
                console.print()
                console.print("[dim]Aborted. Fix issues and run again.[/dim]")
                return
    else:
        console.print("  [green]✓[/green] No issues found!")
    
    # Step 3: Lock
    console.print()
    console.print("[bold]Step 3/4:[/bold] Locking design system...")
    
    with console.status("[green]Generating design system..."):
        design_system = generate_design_system(analysis)
    
    # Write .vibe/system.json
    vibe_dir = target_path / ".vibe"
    vibe_dir.mkdir(parents=True, exist_ok=True)
    system_file = vibe_dir / "system.json"
    
    with open(system_file, "w") as f:
        json.dump(design_system.model_dump(), f, indent=2)
    
    console.print(f"  [green]✓[/green] Saved to {system_file}")
    
    # Step 4: Generate AI configs
    console.print()
    console.print("[bold]Step 4/4:[/bold] Configuring AI tools...")
    
    if not skip_rules:
        # Generate .cursorrules
        cursorrules_path = target_path / ".cursorrules"
        cursorrules_content = generate_cursorrules(design_system)
        
        with open(cursorrules_path, "w") as f:
            f.write(cursorrules_content)
        console.print(f"  [green]✓[/green] Generated {cursorrules_path}")
        
        # Generate CLAUDE.md
        claude_md_path = target_path / "CLAUDE.md"
        claude_md_content = generate_claude_md(design_system)
        
        with open(claude_md_path, "w") as f:
            f.write(claude_md_content)
        console.print(f"  [green]✓[/green] Generated {claude_md_path}")
    
    if not skip_mcp:
        # Configure MCP for all supported tools
        console.print("  [dim]Configuring MCP servers...[/dim]")
        
        mcp_results = configure_all_mcp_servers(system_file, yes)
        
        for tool_name, success, message in mcp_results:
            if success:
                console.print(f"  [green]✓[/green] {tool_name}: {message}")
            else:
                console.print(f"  [yellow]–[/yellow] {tool_name}: {message}")
    
    # Done!
    console.print()
    console.print("─" * 60)
    console.print()
    console.print("[bold green]✓ Setup complete![/bold green]")
    console.print()
    console.print("[dim]Your AI tools will now follow your design system:[/dim]")
    console.print()
    console.print(f"  • [bold].vibe/system.json[/bold] — Design system source of truth")
    if not skip_rules:
        console.print(f"  • [bold].cursorrules[/bold] — Cursor reads this automatically")
        console.print(f"  • [bold]CLAUDE.md[/bold] — Claude Code reads this automatically")
    if not skip_mcp:
        console.print(f"  • [bold]MCP Server[/bold] — Configured for Claude Desktop, Claude Code, Cursor")
    console.print()
    console.print("[dim]Restart your AI tools to activate MCP server.[/dim]")


def generate_cursorrules(system) -> str:
    """Generate .cursorrules content from design system."""
    lines = [
        "# Design System Rules",
        "",
        "When generating code, follow these design system constraints:",
        "",
        "## Spacing",
        "",
        f"Use only these spacing values: {', '.join(f'`{s}`' for s in system.spacing.scale)}",
        "",
        "Valid Tailwind classes:",
        "```",
    ]
    
    # Add spacing examples
    for prefix in ["p", "m", "px", "py", "mx", "my", "gap"]:
        examples = [f"{prefix}-{s}" for s in system.spacing.scale[:5]]
        lines.append(f"{prefix}-*: {', '.join(examples)}")
    
    lines.extend([
        "```",
        "",
        "❌ Never use arbitrary spacing like `p-[10px]` or `m-[1.5rem]`",
        "",
        "## Colors",
        "",
        "Use only these colors:",
        "",
    ])
    
    for color in system.colors[:10]:
        usage = f" — {color.usage}" if color.usage else ""
        lines.append(f"- **{color.name}**: `{color.value}`{usage}")
    
    lines.extend([
        "",
        "❌ Never use arbitrary colors like `bg-[#ff0000]`",
        "",
        "## Typography",
        "",
        f"**Font sizes**: {', '.join(f'`text-{s}`' for s in system.typography.font_sizes)}",
        "",
        f"**Font weights**: {', '.join(f'`font-{w}`' for w in system.typography.font_weights)}",
        "",
    ])
    
    if system.typography.font_families:
        lines.append(f"**Font families**: {', '.join(f'`font-{f}`' for f in system.typography.font_families)}")
        lines.append("")
    
    lines.extend([
        "❌ Never use arbitrary typography like `text-[42px]` or `font-[CustomFont]`",
        "",
        "## Border Radius",
        "",
        f"Use only: {', '.join(f'`rounded-{r}`' for r in system.border_radius.scale)}",
        "",
        "## Shadows",
        "",
        f"Use only: {', '.join(f'`{s}`' for s in system.shadows.scale)}",
        "",
        "---",
        "",
        "This design system was generated by [Vibe Check](https://github.com/ihlamury/vibe-check).",
        "Run `vibe check` to verify consistency.",
    ])
    
    return "\n".join(lines)


def generate_claude_md(system) -> str:
    """Generate CLAUDE.md content from design system."""
    lines = [
        "# Design System",
        "",
        "This project uses a locked design system. Follow these rules when generating code.",
        "",
        "## Quick Reference",
        "",
        "| Category | Allowed Values |",
        "|----------|----------------|",
        f"| Spacing | {', '.join(str(s) for s in system.spacing.scale)} |",
        f"| Font Sizes | {', '.join(system.typography.font_sizes)} |",
        f"| Font Weights | {', '.join(system.typography.font_weights)} |",
        f"| Border Radius | {', '.join(system.border_radius.scale)} |",
        f"| Shadows | {', '.join(system.shadows.scale)} |",
        "",
        "## Colors",
        "",
    ]
    
    for color in system.colors[:10]:
        hex_str = f" ({color.hex})" if color.hex else ""
        lines.append(f"- **{color.name}**: `{color.value}`{hex_str}")
    
    lines.extend([
        "",
        "## Rules",
        "",
        "1. **No arbitrary values** — Don't use `bg-[#fff]`, `p-[10px]`, etc.",
        "2. **Stick to the scale** — Use values from the tables above",
        "3. **Use semantic colors** — Use `primary`, `neutral`, etc. not raw colors",
        "",
        "## Validation",
        "",
        "Run `vibe check` to validate your changes against this design system.",
        "",
        "---",
        "",
        "*Generated by [Vibe Check](https://github.com/ihlamury/vibe-check)*",
    ])
    
    return "\n".join(lines)


def configure_all_mcp_servers(system_file: Path, auto_yes: bool) -> list[tuple[str, bool, str]]:
    """
    Configure MCP server for all supported tools.
    
    Returns list of (tool_name, success, message) tuples.
    """
    results: list[tuple[str, bool, str]] = []
    
    # Get absolute path to system file
    system_file_abs = system_file.resolve()
    
    # MCP server config for JSON-based tools
    mcp_config = {
        "command": "vibe",
        "args": ["serve", "--system-file", str(system_file_abs)]
    }
    
    # 1. Claude Desktop (uses JSON config)
    result = _configure_mcp_json(
        tool_name="Claude Desktop",
        config_path=get_claude_desktop_config_path(),
        mcp_config=mcp_config,
        auto_yes=auto_yes
    )
    results.append(result)
    
    # 2. Claude Code (uses CLI command)
    result = _configure_claude_code_mcp(
        system_file_abs=system_file_abs,
        auto_yes=auto_yes
    )
    results.append(result)
    
    # 3. Cursor (uses JSON config)
    result = _configure_mcp_json(
        tool_name="Cursor",
        config_path=get_cursor_mcp_config_path(),
        mcp_config=mcp_config,
        auto_yes=auto_yes
    )
    results.append(result)
    
    return results


def _configure_claude_code_mcp(
    system_file_abs: Path,
    auto_yes: bool
) -> tuple[str, bool, str]:
    """
    Configure MCP server for Claude Code using CLI.
    
    Returns (tool_name, success, message).
    """
    import subprocess
    import shutil
    
    tool_name = "Claude Code"
    
    # Check if claude CLI is installed
    claude_path = shutil.which("claude")
    if not claude_path:
        return (tool_name, False, "CLI not installed")
    
    # Check if vibe-check is already configured
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "vibe-check" in result.stdout:
            # Already configured - check if same path
            if str(system_file_abs) in result.stdout:
                return (tool_name, True, "Already configured")
            else:
                # Different path - need to remove and re-add
                if not auto_yes:
                    if not Confirm.ask(f"  [yellow]{tool_name}: Update existing config?[/yellow]", default=True):
                        return (tool_name, False, "Skipped (existing config)")
                
                # Remove old config
                subprocess.run(
                    ["claude", "mcp", "remove", "vibe-check"],
                    capture_output=True,
                    timeout=10
                )
    except subprocess.TimeoutExpired:
        return (tool_name, False, "CLI timeout")
    except Exception as e:
        return (tool_name, False, f"CLI error: {e}")
    
    # Add MCP server using claude CLI
    try:
        result = subprocess.run(
            [
                "claude", "mcp", "add", "vibe-check", "--",
                "vibe", "serve", "--system-file", str(system_file_abs)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return (tool_name, True, "Configured")
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            return (tool_name, False, f"Failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        return (tool_name, False, "CLI timeout")
    except Exception as e:
        return (tool_name, False, f"Failed: {e}")


def _configure_mcp_json(
    tool_name: str,
    config_path: Path,
    mcp_config: dict,
    auto_yes: bool
) -> tuple[str, bool, str]:
    """
    Configure MCP server for tools that use JSON config files.
    
    Returns (tool_name, success, message).
    """
    # Check if config directory exists (indicates tool is installed)
    if not config_path.parent.exists():
        return (tool_name, False, "Not installed")
    
    # Load existing config or create new
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check if already configured
    if "vibe-check" in config["mcpServers"]:
        existing = config["mcpServers"]["vibe-check"]
        if existing == mcp_config:
            return (tool_name, True, "Already configured")
        
        if not auto_yes:
            if not Confirm.ask(f"  [yellow]{tool_name}: Overwrite existing config?[/yellow]", default=True):
                return (tool_name, False, "Skipped (existing config)")
    
    # Add vibe-check server config
    config["mcpServers"]["vibe-check"] = mcp_config
    
    # Write config
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return (tool_name, True, "Configured")
    except Exception as e:
        return (tool_name, False, f"Failed: {e}")
