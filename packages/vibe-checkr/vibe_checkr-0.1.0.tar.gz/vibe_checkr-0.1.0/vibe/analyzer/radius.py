"""
Border radius analyzer - Detect border radius inconsistencies.
"""

import re
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class BorderRadiusIssue:
    """A border radius inconsistency."""
    
    type: str  # "arbitrary", "too_many", "inconsistent"
    values: list[str]
    suggestion: str
    severity: str = "warning"


@dataclass
class BorderRadiusAnalysis:
    """Results of border radius analysis."""
    
    unique_values: list[str] = field(default_factory=list)
    value_counts: dict[str, int] = field(default_factory=dict)
    issues: list[BorderRadiusIssue] = field(default_factory=list)
    suggested_values: list[str] = field(default_factory=list)
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)


# Tailwind border radius scale
TAILWIND_RADIUS = ['none', 'sm', '', 'md', 'lg', 'xl', '2xl', '3xl', 'full']

# Pattern to extract radius value
RADIUS_PATTERN = r'^rounded(?:-([tblr]|tl|tr|bl|br))?(?:-(none|sm|md|lg|xl|2xl|3xl|full|\[.+\]))?$'


def analyze_border_radius(
    tailwind_classes: list[str],
    css_radius: list[str]
) -> BorderRadiusAnalysis:
    """
    Analyze border radius for inconsistencies.
    
    Args:
        tailwind_classes: Tailwind rounded classes
        css_radius: CSS border-radius values
        
    Returns:
        BorderRadiusAnalysis with findings and recommendations
    """
    analysis = BorderRadiusAnalysis()
    
    # Extract radius values
    radius_values: list[str] = []
    arbitrary_values: list[str] = []
    
    for cls in tailwind_classes:
        base_cls = _strip_prefixes(cls)
        match = re.match(RADIUS_PATTERN, base_cls)
        
        if match:
            size = match.group(2) or ''  # Default rounded has no size suffix
            
            if size.startswith('['):
                arbitrary_values.append(cls)
            else:
                # Normalize "rounded" to "rounded-DEFAULT"
                radius_values.append(size if size else 'DEFAULT')
    
    # Add CSS radius values
    for css_value in css_radius:
        radius_values.append(css_value)
    
    # Count occurrences
    value_counts = Counter(radius_values)
    analysis.value_counts = dict(value_counts)
    analysis.unique_values = list(set(radius_values))
    
    # Check for issues
    issues: list[BorderRadiusIssue] = []
    
    # Issue 1: Arbitrary values
    if arbitrary_values:
        issues.append(BorderRadiusIssue(
            type="arbitrary",
            values=arbitrary_values,
            suggestion="Replace arbitrary radius values with Tailwind scale (rounded-md, rounded-lg, etc.)",
            severity="warning"
        ))
    
    # Issue 2: Too many unique values
    if len(analysis.unique_values) > 3:
        issues.append(BorderRadiusIssue(
            type="too_many",
            values=analysis.unique_values,
            suggestion=f"Using {len(analysis.unique_values)} border radius values. Consider limiting to 2-3 for consistency.",
            severity="warning"
        ))
    
    # Issue 3: Mixing similar values (e.g., sm, DEFAULT, md all being used)
    similar_small = {'sm', 'DEFAULT', 'md'}
    used_small = similar_small.intersection(set(analysis.unique_values))
    if len(used_small) > 1:
        issues.append(BorderRadiusIssue(
            type="inconsistent",
            values=list(used_small),
            suggestion=f"Using similar radius values: {', '.join(used_small)}. Pick one for consistency.",
            severity="info"
        ))
    
    analysis.issues = issues
    analysis.suggested_values = _suggest_radius_values(value_counts)
    
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


def _suggest_radius_values(value_counts: Counter) -> list[str]:
    """Suggest a clean set of border radius values."""
    if not value_counts:
        return ['md', 'xl']
    
    # Get most used values
    most_common = value_counts.most_common(3)
    suggested = [value for value, _ in most_common]
    
    # If we have too many similar ones, consolidate
    if len(suggested) < 2:
        if 'full' not in suggested:
            suggested.append('full')
        if 'md' not in suggested and 'lg' not in suggested:
            suggested.append('md')
    
    return suggested[:3]
