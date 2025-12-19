"""
Shadow analyzer - Detect shadow inconsistencies.
"""

import re
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class ShadowIssue:
    """A shadow inconsistency."""
    
    type: str  # "arbitrary", "too_many", "inconsistent"
    values: list[str]
    suggestion: str
    severity: str = "warning"


@dataclass
class ShadowAnalysis:
    """Results of shadow analysis."""
    
    unique_values: list[str] = field(default_factory=list)
    value_counts: dict[str, int] = field(default_factory=dict)
    issues: list[ShadowIssue] = field(default_factory=list)
    suggested_values: list[str] = field(default_factory=list)
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)


# Tailwind shadow scale
TAILWIND_SHADOWS = ['none', 'sm', '', 'md', 'lg', 'xl', '2xl', 'inner']

# Pattern to extract shadow value
SHADOW_PATTERN = r'^shadow(?:-(none|sm|md|lg|xl|2xl|inner|\[.+\]))?$'
DROP_SHADOW_PATTERN = r'^drop-shadow(?:-(none|sm|md|lg|xl|2xl|\[.+\]))?$'


def analyze_shadows(
    tailwind_classes: list[str],
    css_shadows: list[str]
) -> ShadowAnalysis:
    """
    Analyze shadow usage for inconsistencies.
    
    Args:
        tailwind_classes: Tailwind shadow classes
        css_shadows: CSS box-shadow values
        
    Returns:
        ShadowAnalysis with findings and recommendations
    """
    analysis = ShadowAnalysis()
    
    # Extract shadow values
    shadow_values: list[str] = []
    arbitrary_values: list[str] = []
    
    for cls in tailwind_classes:
        base_cls = _strip_prefixes(cls)
        
        # Check box shadow
        match = re.match(SHADOW_PATTERN, base_cls)
        if match:
            size = match.group(1) or 'DEFAULT'
            
            if size.startswith('['):
                arbitrary_values.append(cls)
            else:
                shadow_values.append(f"shadow-{size}" if size != 'DEFAULT' else 'shadow')
            continue
        
        # Check drop shadow
        drop_match = re.match(DROP_SHADOW_PATTERN, base_cls)
        if drop_match:
            size = drop_match.group(1) or 'DEFAULT'
            
            if size.startswith('['):
                arbitrary_values.append(cls)
            else:
                shadow_values.append(f"drop-shadow-{size}" if size != 'DEFAULT' else 'drop-shadow')
    
    # Add CSS shadows (simplified)
    for css_value in css_shadows:
        if css_value and css_value != 'none':
            shadow_values.append(css_value[:50])  # Truncate long shadows
    
    # Count occurrences
    value_counts = Counter(shadow_values)
    analysis.value_counts = dict(value_counts)
    analysis.unique_values = list(set(shadow_values))
    
    # Check for issues
    issues: list[ShadowIssue] = []
    
    # Issue 1: Arbitrary values
    if arbitrary_values:
        issues.append(ShadowIssue(
            type="arbitrary",
            values=arbitrary_values,
            suggestion="Replace arbitrary shadow values with Tailwind scale (shadow-sm, shadow-lg, etc.)",
            severity="warning"
        ))
    
    # Issue 2: Too many unique shadow values
    if len(analysis.unique_values) > 4:
        issues.append(ShadowIssue(
            type="too_many",
            values=analysis.unique_values,
            suggestion=f"Using {len(analysis.unique_values)} shadow values. Consider limiting to 2-3 for consistency.",
            severity="info"
        ))
    
    # Issue 3: Mixing similar values
    similar_medium = {'shadow', 'shadow-sm', 'shadow-md'}
    box_shadows = {v for v in analysis.unique_values if v.startswith('shadow')}
    used_similar = similar_medium.intersection(box_shadows)
    if len(used_similar) > 1:
        issues.append(ShadowIssue(
            type="inconsistent",
            values=list(used_similar),
            suggestion=f"Using similar shadow values: {', '.join(used_similar)}. Pick one for consistency.",
            severity="info"
        ))
    
    analysis.issues = issues
    analysis.suggested_values = _suggest_shadow_values(value_counts)
    
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


def _suggest_shadow_values(value_counts: Counter) -> list[str]:
    """Suggest a clean set of shadow values."""
    if not value_counts:
        return ['shadow-sm', 'shadow-lg']
    
    # Get most used values
    most_common = value_counts.most_common(3)
    return [value for value, _ in most_common][:3]
