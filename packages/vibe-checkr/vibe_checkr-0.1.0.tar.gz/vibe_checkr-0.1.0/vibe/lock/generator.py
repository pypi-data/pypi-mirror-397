"""
Design system generator - Create design system from analysis.
"""

from datetime import datetime

from vibe.analyzer import DesignAnalysis
from vibe.lock.schema import (
    DesignSystem,
    SpacingSystem,
    ColorDefinition,
    TypographySystem,
    BorderRadiusSystem,
    ShadowSystem,
)


def generate_design_system(analysis: DesignAnalysis) -> DesignSystem:
    """
    Generate a design system from analysis results.
    
    Uses suggested values when available, otherwise uses detected values.
    
    Args:
        analysis: DesignAnalysis from analyzing a codebase
        
    Returns:
        DesignSystem ready to save as .vibe/system.json
    """
    
    # Generate spacing
    spacing_scale = analysis.spacing.suggested_scale or analysis.spacing.detected_scale
    spacing = SpacingSystem(
        scale=spacing_scale,
        tailwind_classes=_generate_spacing_classes(spacing_scale),
    )
    
    # Generate colors
    colors = _generate_colors(analysis.colors)
    
    # Generate typography
    typography = TypographySystem(
        font_sizes=analysis.typography.font_sizes or ["sm", "base", "lg", "xl", "2xl"],
        font_weights=analysis.typography.font_weights or ["normal", "medium", "bold"],
        font_families=analysis.typography.font_families or ["sans"],
        line_heights=analysis.typography.line_heights or ["normal", "relaxed"],
        letter_spacings=analysis.typography.letter_spacings or ["normal"],
    )
    
    # Generate border radius
    border_radius = BorderRadiusSystem(
        scale=analysis.border_radius.suggested_values or analysis.border_radius.unique_values or ["md", "lg", "full"],
    )
    
    # Generate shadows
    shadows = ShadowSystem(
        scale=analysis.shadows.suggested_values or analysis.shadows.unique_values or ["sm", "md", "lg"],
    )
    
    return DesignSystem(
        version="1.0",
        locked=True,
        spacing=spacing,
        colors=colors,
        typography=typography,
        border_radius=border_radius,
        shadows=shadows,
        generated_at=datetime.now().isoformat(),
    )


def _generate_spacing_classes(scale: list[int]) -> list[str]:
    """Generate Tailwind spacing classes from a scale."""
    classes: list[str] = []
    
    prefixes = ["p", "m", "px", "py", "mx", "my", "pt", "pr", "pb", "pl", "mt", "mr", "mb", "ml", "gap"]
    
    for value in scale:
        for prefix in prefixes[:5]:  # Just main prefixes for example
            classes.append(f"{prefix}-{value}")
    
    return classes


def _generate_colors(color_analysis) -> list[ColorDefinition]:
    """Generate color definitions from analysis."""
    colors: list[ColorDefinition] = []
    
    # Use suggested palette or top colors from analysis
    palette = color_analysis.suggested_palette or [c.value for c in color_analysis.unique_colors[:12]]
    
    # Assign semantic names based on common patterns
    semantic_names = _infer_semantic_names(palette)
    
    for i, color_value in enumerate(palette):
        # Try to find the color info
        color_info = next(
            (c for c in color_analysis.unique_colors if c.value == color_value),
            None
        )
        
        name = semantic_names.get(color_value, f"color-{i + 1}")
        
        colors.append(ColorDefinition(
            name=name,
            value=color_value,
            hex=color_info.hex_value if color_info else None,
            usage=_infer_usage(color_value, name),
        ))
    
    return colors


def _infer_semantic_names(palette: list[str]) -> dict[str, str]:
    """Infer semantic names for colors based on common patterns."""
    names: dict[str, str] = {}
    
    # Common semantic mappings
    semantic_patterns = {
        "blue": "primary",
        "indigo": "primary",
        "violet": "primary",
        "gray": "neutral",
        "slate": "neutral",
        "zinc": "neutral",
        "neutral": "neutral",
        "red": "danger",
        "green": "success",
        "emerald": "success",
        "yellow": "warning",
        "amber": "warning",
        "orange": "accent",
    }
    
    used_names: set[str] = set()
    
    for color in palette:
        # Check for base color match
        for base, semantic in semantic_patterns.items():
            if color.startswith(base):
                # Add number suffix if name already used
                name = semantic
                counter = 1
                while name in used_names:
                    counter += 1
                    name = f"{semantic}-{counter}"
                
                names[color] = name
                used_names.add(name)
                break
        
        # Handle special cases
        if color == "white":
            names[color] = "background"
            used_names.add("background")
        elif color == "black":
            names[color] = "foreground"
            used_names.add("foreground")
    
    return names


def _infer_usage(color_value: str, name: str) -> str | None:
    """Infer the intended usage of a color."""
    usage_map = {
        "primary": "Primary brand color, CTAs, links",
        "secondary": "Secondary actions, less prominent elements",
        "neutral": "Text, borders, backgrounds",
        "danger": "Errors, destructive actions",
        "success": "Success states, confirmations",
        "warning": "Warnings, cautions",
        "accent": "Highlights, badges, accents",
        "background": "Page backgrounds",
        "foreground": "Primary text color",
    }
    
    # Check if name starts with any known usage
    for key, usage in usage_map.items():
        if name.startswith(key):
            return usage
    
    return None
