"""
MCP Server - Expose design system to AI tools via Model Context Protocol.
"""

import json
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from vibe.lock.schema import DesignSystem


def load_design_system(system_path: Path) -> DesignSystem:
    """Load design system from JSON file."""
    with open(system_path) as f:
        data = json.load(f)
    return DesignSystem(**data)


def create_server(system_path: Path) -> "Server":
    """Create and configure the MCP server."""
    if not MCP_AVAILABLE:
        raise ImportError("MCP package not installed. Run: pip install mcp")
    
    server = Server("vibe-check")
    design_system = load_design_system(system_path)
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="get_design_system",
                description="Get the locked design system with all design tokens (colors, spacing, typography, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="validate_styles",
                description="Validate CSS/Tailwind styles against the design system. Returns violations if any.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "styles": {
                            "type": "string",
                            "description": "CSS classes or styles to validate (e.g., 'bg-blue-500 p-4 rounded-lg')"
                        }
                    },
                    "required": ["styles"]
                }
            ),
            Tool(
                name="suggest_fix",
                description="Get the correct design system value for an invalid style.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "invalid_style": {
                            "type": "string",
                            "description": "The invalid style to fix (e.g., 'bg-[#ff0000]' or 'p-5')"
                        }
                    },
                    "required": ["invalid_style"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        
        if name == "get_design_system":
            return [TextContent(
                type="text",
                text=json.dumps(design_system.model_dump(), indent=2)
            )]
        
        elif name == "validate_styles":
            styles = arguments.get("styles", "")
            violations = validate_styles_against_system(styles, design_system)
            
            if not violations:
                return [TextContent(
                    type="text",
                    text="✓ All styles are valid according to the design system."
                )]
            else:
                return [TextContent(
                    type="text",
                    text="Violations found:\n" + "\n".join(f"- {v}" for v in violations)
                )]
        
        elif name == "suggest_fix":
            invalid_style = arguments.get("invalid_style", "")
            suggestion = suggest_fix_for_style(invalid_style, design_system)
            return [TextContent(
                type="text",
                text=suggestion
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    return server


def validate_styles_against_system(styles: str, system: DesignSystem) -> list[str]:
    """Validate styles against the design system."""
    violations: list[str] = []
    classes = styles.split()
    
    for cls in classes:
        # Check for arbitrary values
        if "[" in cls and "]" in cls:
            violations.append(f"`{cls}` uses arbitrary value - use design system tokens instead")
            continue
        
        # Check spacing
        if cls.startswith(("p-", "m-", "px-", "py-", "mx-", "my-", "pt-", "pb-", "pl-", "pr-", "mt-", "mb-", "ml-", "mr-", "gap-")):
            if not _is_valid_spacing(cls, system):
                violations.append(f"`{cls}` not in spacing scale {system.spacing.scale}")
        
        # Check colors
        if cls.startswith(("bg-", "text-", "border-", "ring-")):
            if not _is_valid_color(cls, system):
                valid_colors = [c.value for c in system.colors[:5]]
                violations.append(f"`{cls}` not in color palette (valid: {', '.join(valid_colors)}...)")
        
        # Check border radius
        if cls.startswith("rounded"):
            if not _is_valid_radius(cls, system):
                violations.append(f"`{cls}` not in border radius scale {system.border_radius.scale}")
        
        # Check shadows
        if cls.startswith("shadow"):
            if not _is_valid_shadow(cls, system):
                violations.append(f"`{cls}` not in shadow scale {system.shadows.scale}")
    
    return violations


def _is_valid_spacing(cls: str, system: DesignSystem) -> bool:
    """Check if spacing class is valid."""
    # Extract the number from the class
    import re
    match = re.search(r'-(\d+(?:\.5)?)$', cls)
    if not match:
        return True  # Can't parse, assume valid
    
    value = float(match.group(1))
    return value in [float(s) for s in system.spacing.scale]


def _is_valid_color(cls: str, system: DesignSystem) -> bool:
    """Check if color class is valid."""
    # Extract color name from class
    import re
    match = re.match(r'^(?:bg|text|border|ring)-(.+)$', cls)
    if not match:
        return True
    
    color_value = match.group(1)
    
    # Check against system colors
    valid_values = [c.value for c in system.colors]
    
    # Also allow common defaults
    valid_values.extend(["white", "black", "transparent", "current", "inherit"])
    
    return color_value in valid_values


def _is_valid_radius(cls: str, system: DesignSystem) -> bool:
    """Check if border radius class is valid."""
    import re
    # Extract size from rounded-{size}
    match = re.match(r'^rounded(?:-(?:t|b|l|r|tl|tr|bl|br))?(?:-(.+))?$', cls)
    if not match:
        return True
    
    size = match.group(1) or "DEFAULT"
    return size in system.border_radius.scale or size == "DEFAULT"


def _is_valid_shadow(cls: str, system: DesignSystem) -> bool:
    """Check if shadow class is valid."""
    return cls in system.shadows.scale or cls == "shadow"


def suggest_fix_for_style(invalid_style: str, system: DesignSystem) -> str:
    """Suggest a fix for an invalid style."""
    import re
    
    # Arbitrary color
    if re.match(r'^(bg|text|border|ring)-\[#', invalid_style):
        colors = [f"{c.name}: {c.value}" for c in system.colors[:5]]
        return f"Replace `{invalid_style}` with a theme color:\n" + "\n".join(f"  - {c}" for c in colors)
    
    # Arbitrary spacing
    if re.match(r'^[pm][xytblr]?-\[', invalid_style):
        return f"Replace `{invalid_style}` with a scale value: {system.spacing.scale}"
    
    # Off-scale spacing
    if re.match(r'^[pm][xytblr]?-\d', invalid_style):
        match = re.search(r'-(\d+(?:\.5)?)$', invalid_style)
        if match:
            value = float(match.group(1))
            # Find closest scale value
            closest = min(system.spacing.scale, key=lambda x: abs(x - value))
            prefix = invalid_style.rsplit('-', 1)[0]
            return f"Replace `{invalid_style}` with `{prefix}-{int(closest) if closest == int(closest) else closest}`"
    
    # Arbitrary border radius
    if re.match(r'^rounded.*-\[', invalid_style):
        return f"Replace `{invalid_style}` with a scale value: {system.border_radius.scale}"
    
    # Generic suggestion
    return f"Check if `{invalid_style}` matches your design system. Valid scales:\n" \
           f"  - Spacing: {system.spacing.scale}\n" \
           f"  - Border radius: {system.border_radius.scale}\n" \
           f"  - Shadows: {system.shadows.scale}"


async def run_server(system_path: Path):
    """Run the MCP server."""
    if not MCP_AVAILABLE:
        raise ImportError("MCP package not installed. Run: pip install mcp")
    
    server = create_server(system_path)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def start_server(system_path: Path, port: int = 3000):
    """Start the MCP server (blocking)."""
    import asyncio
    asyncio.run(run_server(system_path))
