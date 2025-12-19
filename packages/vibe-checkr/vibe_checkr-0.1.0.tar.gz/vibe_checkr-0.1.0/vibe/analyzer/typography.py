"""
Typography analyzer - Detect typography inconsistencies.
"""

import re
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class TypographyIssue:
    """A typography inconsistency."""
    
    type: str  # "arbitrary", "off_scale", "inconsistent_weights", "too_many_fonts"
    category: str  # "font_size", "font_weight", "font_family", "line_height"
    values: list[str]
    suggestion: str
    severity: str = "warning"


@dataclass
class TypographyAnalysis:
    """Results of typography analysis."""
    
    # Font sizes
    font_sizes: list[str] = field(default_factory=list)
    font_size_counts: dict[str, int] = field(default_factory=dict)
    
    # Font weights
    font_weights: list[str] = field(default_factory=list)
    font_weight_counts: dict[str, int] = field(default_factory=dict)
    
    # Font families
    font_families: list[str] = field(default_factory=list)
    font_family_counts: dict[str, int] = field(default_factory=dict)
    
    # Line heights
    line_heights: list[str] = field(default_factory=list)
    
    # Letter spacing
    letter_spacings: list[str] = field(default_factory=list)
    
    # Issues
    issues: list[TypographyIssue] = field(default_factory=list)
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)


# Tailwind font size scale
TAILWIND_FONT_SIZES = [
    'xs', 'sm', 'base', 'lg', 'xl',
    '2xl', '3xl', '4xl', '5xl', '6xl', '7xl', '8xl', '9xl'
]

# Tailwind font weights
TAILWIND_FONT_WEIGHTS = [
    'thin', 'extralight', 'light', 'normal',
    'medium', 'semibold', 'bold', 'extrabold', 'black'
]

# Patterns
FONT_SIZE_PATTERN = r'^text-(xs|sm|base|lg|xl|[2-9]xl|\[.+\])$'
FONT_WEIGHT_PATTERN = r'^font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black|\[\d+\])$'
FONT_FAMILY_PATTERN = r'^font-(sans|serif|mono|\[.+\])$'
LINE_HEIGHT_PATTERN = r'^leading-(none|tight|snug|normal|relaxed|loose|\d+|\[.+\])$'
LETTER_SPACING_PATTERN = r'^tracking-(tighter|tight|normal|wide|wider|widest|\[.+\])$'


def analyze_typography(
    tailwind_classes: list[str],
    css_typography: list[dict]
) -> TypographyAnalysis:
    """
    Analyze typography for inconsistencies.
    
    Args:
        tailwind_classes: Tailwind typography classes
        css_typography: CSS typography properties
        
    Returns:
        TypographyAnalysis with findings and recommendations
    """
    analysis = TypographyAnalysis()
    
    # Categorize Tailwind classes
    font_sizes: list[str] = []
    font_weights: list[str] = []
    font_families: list[str] = []
    line_heights: list[str] = []
    letter_spacings: list[str] = []
    
    arbitrary_sizes: list[str] = []
    arbitrary_weights: list[str] = []
    arbitrary_families: list[str] = []
    
    for cls in tailwind_classes:
        base_cls = _strip_prefixes(cls)
        
        # Font size
        size_match = re.match(FONT_SIZE_PATTERN, base_cls)
        if size_match:
            value = size_match.group(1)
            if value.startswith('['):
                arbitrary_sizes.append(cls)
            else:
                font_sizes.append(value)
            continue
        
        # Font weight
        weight_match = re.match(FONT_WEIGHT_PATTERN, base_cls)
        if weight_match:
            value = weight_match.group(1)
            if value.startswith('['):
                arbitrary_weights.append(cls)
            else:
                font_weights.append(value)
            continue
        
        # Font family
        family_match = re.match(FONT_FAMILY_PATTERN, base_cls)
        if family_match:
            value = family_match.group(1)
            if value.startswith('['):
                arbitrary_families.append(cls)
            else:
                font_families.append(value)
            continue
        
        # Line height
        leading_match = re.match(LINE_HEIGHT_PATTERN, base_cls)
        if leading_match:
            line_heights.append(leading_match.group(1))
            continue
        
        # Letter spacing
        tracking_match = re.match(LETTER_SPACING_PATTERN, base_cls)
        if tracking_match:
            letter_spacings.append(tracking_match.group(1))
            continue
    
    # Process CSS typography
    for prop in css_typography:
        prop_name = prop.get('property', '')
        value = prop.get('value', '')
        
        if prop_name == 'font-size':
            font_sizes.append(value)
        elif prop_name == 'font-weight':
            font_weights.append(value)
        elif prop_name == 'font-family':
            font_families.append(_extract_font_family(value))
        elif prop_name == 'line-height':
            line_heights.append(value)
        elif prop_name == 'letter-spacing':
            letter_spacings.append(value)
    
    # Count occurrences
    analysis.font_size_counts = dict(Counter(font_sizes))
    analysis.font_weight_counts = dict(Counter(font_weights))
    analysis.font_family_counts = dict(Counter(font_families))
    
    analysis.font_sizes = sorted(set(font_sizes), key=_font_size_sort_key)
    analysis.font_weights = sorted(set(font_weights), key=_font_weight_sort_key)
    analysis.font_families = list(set(font_families))
    analysis.line_heights = list(set(line_heights))
    analysis.letter_spacings = list(set(letter_spacings))
    
    # Check for issues
    issues: list[TypographyIssue] = []
    
    # Issue 1: Arbitrary font sizes
    if arbitrary_sizes:
        issues.append(TypographyIssue(
            type="arbitrary",
            category="font_size",
            values=arbitrary_sizes,
            suggestion="Replace arbitrary font sizes with Tailwind scale (text-sm, text-base, etc.)",
            severity="warning"
        ))
    
    # Issue 2: Arbitrary font weights
    if arbitrary_weights:
        issues.append(TypographyIssue(
            type="arbitrary",
            category="font_weight",
            values=arbitrary_weights,
            suggestion="Replace arbitrary weights with Tailwind scale (font-normal, font-medium, font-bold)",
            severity="warning"
        ))
    
    # Issue 3: Too many font sizes
    if len(analysis.font_sizes) > 6:
        issues.append(TypographyIssue(
            type="off_scale",
            category="font_size",
            values=analysis.font_sizes,
            suggestion=f"Using {len(analysis.font_sizes)} font sizes. Consider limiting to 5-6 for a cleaner type scale.",
            severity="info"
        ))
    
    # Issue 4: Inconsistent font weights
    if len(analysis.font_weights) > 4:
        issues.append(TypographyIssue(
            type="inconsistent_weights",
            category="font_weight",
            values=analysis.font_weights,
            suggestion=f"Using {len(analysis.font_weights)} font weights. Consider using 2-3 weights (normal, medium, bold).",
            severity="info"
        ))
    
    # Issue 5: Too many font families
    if len(analysis.font_families) > 2:
        issues.append(TypographyIssue(
            type="too_many_fonts",
            category="font_family",
            values=analysis.font_families,
            suggestion="Using more than 2 font families. Consider limiting to 1-2 for consistency.",
            severity="warning"
        ))
    
    # Issue 6: Arbitrary font families
    if arbitrary_families:
        issues.append(TypographyIssue(
            type="arbitrary",
            category="font_family",
            values=arbitrary_families,
            suggestion="Add custom fonts to your Tailwind config instead of using arbitrary values.",
            severity="warning"
        ))
    
    analysis.issues = issues
    
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


def _font_size_sort_key(size: str) -> int:
    """Sort key for font sizes."""
    order = {
        'xs': 0, 'sm': 1, 'base': 2, 'lg': 3, 'xl': 4,
        '2xl': 5, '3xl': 6, '4xl': 7, '5xl': 8, '6xl': 9,
        '7xl': 10, '8xl': 11, '9xl': 12
    }
    return order.get(size, 99)


def _font_weight_sort_key(weight: str) -> int:
    """Sort key for font weights."""
    order = {
        'thin': 0, 'extralight': 1, 'light': 2, 'normal': 3,
        'medium': 4, 'semibold': 5, 'bold': 6, 'extrabold': 7, 'black': 8
    }
    return order.get(weight, 99)


def _extract_font_family(value: str) -> str:
    """Extract primary font family from a CSS font-family value."""
    # Take first font in the stack
    fonts = value.split(',')
    if fonts:
        return fonts[0].strip().strip('"\'')
    return value
