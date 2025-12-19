"""
CSS property extractor - Extract design tokens from CSS/SCSS files.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class CSSExtraction:
    """Extracted CSS properties by category."""
    
    colors: list[str] = field(default_factory=list)
    spacing: list[str] = field(default_factory=list)
    typography: list[dict] = field(default_factory=list)
    border_radius: list[str] = field(default_factory=list)
    shadows: list[str] = field(default_factory=list)
    custom_properties: dict[str, str] = field(default_factory=dict)


# Regex patterns for CSS values
HEX_COLOR_PATTERN = r'#(?:[0-9a-fA-F]{3}){1,2}(?:[0-9a-fA-F]{2})?'
RGB_COLOR_PATTERN = r'rgba?\([^)]+\)'
HSL_COLOR_PATTERN = r'hsla?\([^)]+\)'
NAMED_COLORS = {
    'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
    'gray', 'grey', 'orange', 'purple', 'pink', 'brown', 'transparent',
    'inherit', 'currentColor',
}

# CSS property patterns
COLOR_PROPERTIES = [
    'color', 'background-color', 'background', 'border-color',
    'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
    'outline-color', 'fill', 'stroke', 'text-decoration-color',
    'caret-color', 'accent-color',
]

SPACING_PROPERTIES = [
    'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
    'gap', 'row-gap', 'column-gap',
]

TYPOGRAPHY_PROPERTIES = [
    'font-family', 'font-size', 'font-weight', 'line-height',
    'letter-spacing', 'text-transform',
]

BORDER_RADIUS_PROPERTIES = [
    'border-radius',
    'border-top-left-radius', 'border-top-right-radius',
    'border-bottom-left-radius', 'border-bottom-right-radius',
]

SHADOW_PROPERTIES = [
    'box-shadow', 'text-shadow', 'filter',
]


def extract_css_properties(file_path: Path) -> CSSExtraction:
    """
    Extract CSS properties from a CSS/SCSS file.
    
    Args:
        file_path: Path to the CSS file
        
    Returns:
        CSSExtraction with properties categorized by type
    """
    result = CSSExtraction()
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return result
    
    # Remove comments
    content = _remove_comments(content)
    
    # Extract custom properties (CSS variables)
    result.custom_properties = _extract_custom_properties(content)
    
    # Extract property values
    for prop, value in _extract_properties(content):
        prop_lower = prop.lower().strip()
        value_clean = value.strip().rstrip(';')
        
        # Categorize by property type
        if prop_lower in COLOR_PROPERTIES:
            colors = _extract_colors_from_value(value_clean)
            result.colors.extend(colors)
            
        elif prop_lower in SPACING_PROPERTIES:
            result.spacing.append(value_clean)
            
        elif prop_lower in TYPOGRAPHY_PROPERTIES:
            result.typography.append({
                'property': prop_lower,
                'value': value_clean,
            })
            
        elif prop_lower in BORDER_RADIUS_PROPERTIES:
            result.border_radius.append(value_clean)
            
        elif prop_lower in SHADOW_PROPERTIES:
            result.shadows.append(value_clean)
    
    return result


def _remove_comments(content: str) -> str:
    """Remove CSS comments from content."""
    # Remove /* ... */ comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Remove // comments (SCSS)
    content = re.sub(r'//[^\n]*', '', content)
    return content


def _extract_custom_properties(content: str) -> dict[str, str]:
    """Extract CSS custom properties (variables)."""
    custom_props: dict[str, str] = {}
    
    # Match --property-name: value;
    pattern = r'(--[\w-]+)\s*:\s*([^;]+);'
    matches = re.findall(pattern, content)
    
    for name, value in matches:
        custom_props[name.strip()] = value.strip()
    
    return custom_props


def _extract_properties(content: str) -> list[tuple[str, str]]:
    """Extract all property: value pairs from CSS."""
    properties: list[tuple[str, str]] = []
    
    # Match property: value; (but not custom properties)
    pattern = r'(?<!-)([\w-]+)\s*:\s*([^;{}]+);'
    matches = re.findall(pattern, content)
    
    for prop, value in matches:
        # Skip custom properties (they start with --)
        if not prop.startswith('--'):
            properties.append((prop, value))
    
    return properties


def _extract_colors_from_value(value: str) -> list[str]:
    """Extract color values from a CSS property value."""
    colors: list[str] = []
    
    # Hex colors
    hex_matches = re.findall(HEX_COLOR_PATTERN, value)
    colors.extend(hex_matches)
    
    # RGB/RGBA colors
    rgb_matches = re.findall(RGB_COLOR_PATTERN, value)
    colors.extend(rgb_matches)
    
    # HSL/HSLA colors
    hsl_matches = re.findall(HSL_COLOR_PATTERN, value)
    colors.extend(hsl_matches)
    
    # Named colors
    words = re.findall(r'\b(\w+)\b', value)
    for word in words:
        if word.lower() in NAMED_COLORS:
            colors.append(word.lower())
    
    return colors
