"""
Analyzer module - Detect design inconsistencies.
"""

from dataclasses import dataclass, field
from vibe.scanner import ScanResult
from vibe.analyzer.spacing import analyze_spacing, SpacingAnalysis
from vibe.analyzer.colors import analyze_colors, ColorAnalysis
from vibe.analyzer.typography import analyze_typography, TypographyAnalysis
from vibe.analyzer.radius import analyze_border_radius, BorderRadiusAnalysis
from vibe.analyzer.shadows import analyze_shadows, ShadowAnalysis


@dataclass
class DesignAnalysis:
    """Complete design system analysis."""
    
    spacing: SpacingAnalysis = field(default_factory=SpacingAnalysis)
    colors: ColorAnalysis = field(default_factory=ColorAnalysis)
    typography: TypographyAnalysis = field(default_factory=TypographyAnalysis)
    border_radius: BorderRadiusAnalysis = field(default_factory=BorderRadiusAnalysis)
    shadows: ShadowAnalysis = field(default_factory=ShadowAnalysis)
    
    @property
    def has_issues(self) -> bool:
        """Check if any category has issues."""
        return (
            self.spacing.has_issues or
            self.colors.has_issues or
            self.typography.has_issues or
            self.border_radius.has_issues or
            self.shadows.has_issues
        )
    
    @property
    def total_issues(self) -> int:
        """Total number of issues across all categories."""
        return (
            self.spacing.issue_count +
            self.colors.issue_count +
            self.typography.issue_count +
            self.border_radius.issue_count +
            self.shadows.issue_count
        )


def analyze_design_system(scan_result: ScanResult) -> DesignAnalysis:
    """
    Analyze scan results for design inconsistencies.
    
    Args:
        scan_result: Results from scanning codebase
        
    Returns:
        DesignAnalysis with issues and recommendations
    """
    return DesignAnalysis(
        spacing=analyze_spacing(
            scan_result.spacing_classes,
            scan_result.css_spacing
        ),
        colors=analyze_colors(
            scan_result.color_classes,
            scan_result.css_colors,
            scan_result.arbitrary_values
        ),
        typography=analyze_typography(
            scan_result.typography_classes,
            scan_result.css_typography
        ),
        border_radius=analyze_border_radius(
            scan_result.border_radius_classes,
            scan_result.css_border_radius
        ),
        shadows=analyze_shadows(
            scan_result.shadow_classes,
            scan_result.css_shadows
        ),
    )
