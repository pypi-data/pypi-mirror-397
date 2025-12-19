"""
JSON reporter - Output analysis as JSON.
"""

import json
from dataclasses import asdict

from vibe.analyzer import DesignAnalysis


class JsonReporter:
    """Report analysis results as JSON."""
    
    def report(self, analysis: DesignAnalysis) -> str:
        """Convert analysis to JSON string."""
        
        data = {
            "spacing": {
                "unique_values": analysis.spacing.unique_values,
                "value_counts": analysis.spacing.value_counts,
                "detected_scale": analysis.spacing.detected_scale,
                "suggested_scale": analysis.spacing.suggested_scale,
                "issues": [asdict(issue) for issue in analysis.spacing.issues],
                "has_issues": analysis.spacing.has_issues,
            },
            "colors": {
                "unique_count": len(analysis.colors.unique_colors),
                "colors": [
                    {
                        "value": c.value,
                        "count": c.count,
                        "tailwind_class": c.tailwind_class,
                        "hex_value": c.hex_value,
                    }
                    for c in analysis.colors.unique_colors
                ],
                "suggested_palette": analysis.colors.suggested_palette,
                "issues": [asdict(issue) for issue in analysis.colors.issues],
                "has_issues": analysis.colors.has_issues,
            },
            "typography": {
                "font_sizes": analysis.typography.font_sizes,
                "font_size_counts": analysis.typography.font_size_counts,
                "font_weights": analysis.typography.font_weights,
                "font_weight_counts": analysis.typography.font_weight_counts,
                "font_families": analysis.typography.font_families,
                "font_family_counts": analysis.typography.font_family_counts,
                "line_heights": analysis.typography.line_heights,
                "letter_spacings": analysis.typography.letter_spacings,
                "issues": [asdict(issue) for issue in analysis.typography.issues],
                "has_issues": analysis.typography.has_issues,
            },
            "border_radius": {
                "unique_values": analysis.border_radius.unique_values,
                "value_counts": analysis.border_radius.value_counts,
                "suggested_values": analysis.border_radius.suggested_values,
                "issues": [asdict(issue) for issue in analysis.border_radius.issues],
                "has_issues": analysis.border_radius.has_issues,
            },
            "shadows": {
                "unique_values": analysis.shadows.unique_values,
                "value_counts": analysis.shadows.value_counts,
                "suggested_values": analysis.shadows.suggested_values,
                "issues": [asdict(issue) for issue in analysis.shadows.issues],
                "has_issues": analysis.shadows.has_issues,
            },
            "summary": {
                "has_issues": analysis.has_issues,
                "total_issues": analysis.total_issues,
            },
        }
        
        return json.dumps(data, indent=2)
