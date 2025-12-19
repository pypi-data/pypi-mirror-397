"""
Color analyzer - Detect color inconsistencies.
"""

import re
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class ColorIssue:
    """A color inconsistency."""
    
    type: str  # "arbitrary", "one_off", "similar", "undeclared"
    values: list[str]
    suggestion: str
    severity: str = "warning"


@dataclass 
class ColorInfo:
    """Information about a color."""
    
    value: str
    count: int
    tailwind_class: str | None = None
    hex_value: str | None = None


@dataclass
class ColorAnalysis:
    """Results of color analysis."""
    
    unique_colors: list[ColorInfo] = field(default_factory=list)
    color_counts: dict[str, int] = field(default_factory=dict)
    issues: list[ColorIssue] = field(default_factory=list)
    suggested_palette: list[str] = field(default_factory=list)
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)


# Tailwind color palette
TAILWIND_COLORS = {
    'slate', 'gray', 'zinc', 'neutral', 'stone',
    'red', 'orange', 'amber', 'yellow', 'lime',
    'green', 'emerald', 'teal', 'cyan', 'sky',
    'blue', 'indigo', 'violet', 'purple', 'fuchsia',
    'pink', 'rose',
}

TAILWIND_SHADES = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950']

# Pattern to extract color from Tailwind class
COLOR_CLASS_PATTERN = r'^(?:bg|text|border|ring|fill|stroke|outline|accent|caret|decoration|from|via|to)-(.+)$'
ARBITRARY_COLOR_PATTERN = r'\[(?:#[0-9a-fA-F]{3,8}|rgb[a]?\([^)]+\)|hsl[a]?\([^)]+\))\]'


def analyze_colors(
    tailwind_classes: list[str],
    css_colors: list[str],
    arbitrary_values: list[str]
) -> ColorAnalysis:
    """
    Analyze color usage for inconsistencies.
    
    Args:
        tailwind_classes: Tailwind color classes
        css_colors: CSS color values
        arbitrary_values: Arbitrary Tailwind values (may contain colors)
        
    Returns:
        ColorAnalysis with findings and recommendations
    """
    analysis = ColorAnalysis()
    
    # Extract and count colors
    all_colors: list[str] = []
    arbitrary_colors: list[str] = []
    
    for cls in tailwind_classes:
        base_cls = _strip_prefixes(cls)
        match = re.match(COLOR_CLASS_PATTERN, base_cls)
        
        if match:
            color_value = match.group(1)
            
            # Check if arbitrary
            if re.search(ARBITRARY_COLOR_PATTERN, color_value):
                arbitrary_colors.append(cls)
            else:
                all_colors.append(color_value)
    
    # Add CSS colors
    for css_color in css_colors:
        all_colors.append(css_color)
    
    # Count occurrences
    color_counts = Counter(all_colors)
    analysis.color_counts = dict(color_counts)
    
    # Build unique color list with counts
    for color, count in color_counts.most_common():
        analysis.unique_colors.append(ColorInfo(
            value=color,
            count=count,
            tailwind_class=_get_tailwind_class(color),
            hex_value=_get_hex_value(color)
        ))
    
    # Check for issues
    issues: list[ColorIssue] = []
    
    # Issue 1: Arbitrary color values
    if arbitrary_colors:
        issues.append(ColorIssue(
            type="arbitrary",
            values=arbitrary_colors,
            suggestion="Replace arbitrary colors with Tailwind palette colors or add to theme",
            severity="warning"
        ))
    
    # Issue 2: One-off colors (used only once or twice)
    one_offs = [color for color, count in color_counts.items() if count <= 2]
    if len(one_offs) > 3:
        issues.append(ColorIssue(
            type="one_off",
            values=one_offs[:10],  # Show first 10
            suggestion=f"Found {len(one_offs)} colors used only 1-2 times. Consider consolidating.",
            severity="info"
        ))
    
    # Issue 3: Too many unique colors
    if len(color_counts) > 15:
        issues.append(ColorIssue(
            type="inconsistent",
            values=[],
            suggestion=f"Found {len(color_counts)} unique colors. Consider limiting to 10-12 for consistency.",
            severity="warning"
        ))
    
    # Issue 4: Similar colors (different shades of same color used inconsistently)
    similar_issues = _find_similar_color_issues(color_counts)
    issues.extend(similar_issues)
    
    analysis.issues = issues
    analysis.suggested_palette = _suggest_palette(color_counts)
    
    return analysis


def _strip_prefixes(cls: str) -> str:
    """Strip responsive and state prefixes."""
    prefixes = [
        "sm:", "md:", "lg:", "xl:", "2xl:",
        "dark:", "hover:", "focus:", "active:", "disabled:",
        "group-hover:", "peer-hover:", "first:", "last:",
    ]
    
    result = cls
    for prefix in prefixes:
        while result.startswith(prefix):
            result = result[len(prefix):]
    
    return result


def _get_tailwind_class(color: str) -> str | None:
    """Get the full Tailwind class for a color value."""
    # Check if it's already a Tailwind color
    for base_color in TAILWIND_COLORS:
        if color.startswith(base_color):
            return f"bg-{color}"
    
    if color in ['black', 'white', 'transparent', 'current', 'inherit']:
        return f"bg-{color}"
    
    return None


def _get_hex_value(color: str) -> str | None:
    """Try to get hex value for a color."""
    # If it's already a hex color
    if re.match(r'^#[0-9a-fA-F]{3,8}$', color):
        return color
    
    # Common Tailwind colors to hex (subset)
    tailwind_to_hex = {
        'blue-500': '#3b82f6',
        'blue-600': '#2563eb',
        'gray-900': '#111827',
        'gray-500': '#6b7280',
        'white': '#ffffff',
        'black': '#000000',
    }
    
    return tailwind_to_hex.get(color)


def _find_similar_color_issues(color_counts: Counter) -> list[ColorIssue]:
    """Find issues with similar colors being used."""
    issues: list[ColorIssue] = []
    
    # Group colors by base color
    color_groups: dict[str, list[str]] = {}
    
    for color in color_counts.keys():
        for base_color in TAILWIND_COLORS:
            if color.startswith(base_color + '-'):
                if base_color not in color_groups:
                    color_groups[base_color] = []
                color_groups[base_color].append(color)
                break
    
    # Flag base colors with too many variants
    for base_color, variants in color_groups.items():
        if len(variants) > 4:
            issues.append(ColorIssue(
                type="similar",
                values=variants,
                suggestion=f"Using {len(variants)} shades of {base_color}. Consider limiting to 2-3 shades.",
                severity="info"
            ))
    
    return issues


def _suggest_palette(color_counts: Counter) -> list[str]:
    """Suggest a consolidated color palette."""
    # Get most used colors
    most_common = color_counts.most_common(12)
    return [color for color, _ in most_common]
