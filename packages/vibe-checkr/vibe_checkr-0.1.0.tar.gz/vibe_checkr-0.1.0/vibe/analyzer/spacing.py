"""
Spacing analyzer - Detect spacing inconsistencies.
"""

import re
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class SpacingIssue:
    """A spacing inconsistency."""
    
    type: str  # "off_scale", "arbitrary", "inconsistent"
    values: list[str]
    suggestion: str
    severity: str = "warning"  # "error", "warning", "info"


@dataclass
class SpacingAnalysis:
    """Results of spacing analysis."""
    
    unique_values: list[str] = field(default_factory=list)
    value_counts: dict[str, int] = field(default_factory=dict)
    detected_scale: list[int] = field(default_factory=list)
    issues: list[SpacingIssue] = field(default_factory=list)
    suggested_scale: list[int] = field(default_factory=list)
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)


# Standard Tailwind spacing scale (in Tailwind units, 1 unit = 0.25rem = 4px)
STANDARD_SCALES = {
    "compact": [0, 1, 2, 4, 6, 8, 12, 16],      # 0, 4, 8, 16, 24, 32, 48, 64px
    "default": [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24],
    "relaxed": [0, 2, 4, 8, 12, 16, 24, 32],    # 0, 8, 16, 32, 48, 64, 96, 128px
}

# Tailwind spacing class pattern
SPACING_PATTERN = r'^-?([pm])([xytblr])?-(\d+(?:\.5)?|\[.+\])$'


def analyze_spacing(
    tailwind_classes: list[str],
    css_spacing: list[str]
) -> SpacingAnalysis:
    """
    Analyze spacing values for inconsistencies.
    
    Args:
        tailwind_classes: Tailwind spacing classes (p-4, mx-2, etc.)
        css_spacing: CSS spacing values (16px, 1rem, etc.)
        
    Returns:
        SpacingAnalysis with findings and recommendations
    """
    analysis = SpacingAnalysis()
    
    # Extract spacing values from Tailwind classes
    spacing_values: list[str] = []
    arbitrary_values: list[str] = []
    
    for cls in tailwind_classes:
        # Strip prefixes (responsive, states)
        base_cls = _strip_prefixes(cls)
        match = re.match(SPACING_PATTERN, base_cls)
        
        if match:
            value = match.group(3)
            if value.startswith('['):
                arbitrary_values.append(cls)
            else:
                spacing_values.append(value)
    
    # Count occurrences
    value_counts = Counter(spacing_values)
    analysis.value_counts = dict(value_counts)
    analysis.unique_values = sorted(set(spacing_values), key=_sort_spacing_key)
    
    # Detect the scale being used
    numeric_values = [float(v) for v in spacing_values if v.replace('.', '').isdigit()]
    unique_numeric = sorted(set(numeric_values))
    analysis.detected_scale = [int(v) if v.is_integer() else v for v in unique_numeric]
    
    # Check for issues
    issues: list[SpacingIssue] = []
    
    # Issue 1: Arbitrary values
    if arbitrary_values:
        issues.append(SpacingIssue(
            type="arbitrary",
            values=arbitrary_values,
            suggestion="Replace arbitrary values with Tailwind scale values",
            severity="warning"
        ))
    
    # Issue 2: Too many unique values (suggests no consistent scale)
    if len(analysis.unique_values) > 8:
        issues.append(SpacingIssue(
            type="inconsistent",
            values=analysis.unique_values,
            suggestion=f"Found {len(analysis.unique_values)} spacing values. Consider consolidating to 6-8 values.",
            severity="warning"
        ))
    
    # Issue 3: Off-scale values (values that don't fit common patterns)
    off_scale = _find_off_scale_values(unique_numeric)
    if off_scale:
        issues.append(SpacingIssue(
            type="off_scale",
            values=[str(v) for v in off_scale],
            suggestion=f"Values {off_scale} break the spacing scale. Consider using: {_suggest_scale(unique_numeric)}",
            severity="info"
        ))
    
    analysis.issues = issues
    analysis.suggested_scale = _suggest_scale(unique_numeric)
    
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


def _sort_spacing_key(value: str) -> float:
    """Sort key for spacing values."""
    try:
        return float(value)
    except ValueError:
        return 999


def _find_off_scale_values(values: list[float]) -> list[float]:
    """Find values that don't fit a consistent scale."""
    if len(values) < 3:
        return []
    
    # Check if values follow a pattern (doubling, +4, etc.)
    off_scale: list[float] = []
    
    # Common scales: 0, 1, 2, 4, 8, 16 (doubling) or 0, 2, 4, 6, 8 (linear +2)
    for value in values:
        # Skip 0 and common values
        if value in [0, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64]:
            continue
        
        # Flag odd values that don't fit
        if value not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64]:
            off_scale.append(value)
    
    return off_scale


def _suggest_scale(values: list[float]) -> list[int]:
    """Suggest a clean scale based on current values."""
    if not values:
        return [0, 1, 2, 4, 6, 8, 12, 16]
    
    max_val = max(values)
    
    # Choose scale based on range
    if max_val <= 8:
        return [0, 1, 2, 4, 6, 8]
    elif max_val <= 16:
        return [0, 2, 4, 6, 8, 12, 16]
    elif max_val <= 32:
        return [0, 2, 4, 8, 12, 16, 24, 32]
    else:
        return [0, 2, 4, 8, 16, 24, 32, 48, 64]
