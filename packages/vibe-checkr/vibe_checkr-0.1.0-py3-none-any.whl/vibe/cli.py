"""
Vibe Check CLI - Main entry point.
"""

import click
from rich.console import Console

from vibe import __version__
from vibe.commands.check import check
from vibe.commands.lock import lock
from vibe.commands.enforce import enforce
from vibe.commands.init import init
from vibe.commands.serve import serve

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="vibe")
def main() -> None:
    """
    🎨 Vibe Check - Design system observability for AI-native development.
    
    \b
    Quick start:
        vibe init ./src     # Full setup in one command
    
    \b
    Individual commands:
        vibe check ./src    # Scan for inconsistencies
        vibe lock ./src     # Lock design system
        vibe serve          # Start MCP server
    """
    pass


# Register commands
main.add_command(init)      # vibe init - full setup
main.add_command(check)     # vibe check - scan only
main.add_command(lock)      # vibe lock - lock only
main.add_command(serve)     # vibe serve - MCP server
main.add_command(enforce)   # vibe enforce - alias for serve (legacy)


if __name__ == "__main__":
    main()
