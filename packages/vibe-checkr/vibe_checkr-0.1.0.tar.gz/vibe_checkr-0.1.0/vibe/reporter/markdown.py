"""
Markdown reporter - Output analysis as Markdown.
"""

from vibe.analyzer import DesignAnalysis


class MarkdownReporter:
    """Report analysis results as Markdown."""
    
    def report(self, analysis: DesignAnalysis) -> str:
        """Convert analysis to Markdown string."""
        
        lines: list[str] = []
        
        lines.append("# Vibe Check Report")
        lines.append("")
        
        # Summary
        if analysis.has_issues:
            lines.append(f"**Status:** ⚠️ Found {analysis.total_issues} inconsistencies")
        else:
            lines.append("**Status:** ✅ No inconsistencies found")
        lines.append("")
        
        # Spacing
        lines.append("## Spacing")
        lines.append("")
        if analysis.spacing.has_issues:
            lines.append(f"Found **{len(analysis.spacing.unique_values)}** unique spacing values.")
            lines.append("")
            for issue in analysis.spacing.issues:
                lines.append(f"- {self._severity_emoji(issue.severity)} {issue.suggestion}")
            if analysis.spacing.suggested_scale:
                lines.append(f"\n**Suggested scale:** `{analysis.spacing.suggested_scale}`")
        else:
            lines.append("✅ Spacing is consistent.")
            if analysis.spacing.unique_values:
                lines.append(f"\nUsing {len(analysis.spacing.unique_values)} values: `{', '.join(analysis.spacing.unique_values[:8])}`")
        lines.append("")
        
        # Colors
        lines.append("## Colors")
        lines.append("")
        if analysis.colors.has_issues:
            lines.append(f"Found **{len(analysis.colors.unique_colors)}** unique colors.")
            lines.append("")
            for issue in analysis.colors.issues:
                lines.append(f"- {self._severity_emoji(issue.severity)} {issue.suggestion}")
            if analysis.colors.suggested_palette:
                lines.append(f"\n**Suggested palette:** `{', '.join(analysis.colors.suggested_palette[:8])}`")
        else:
            lines.append("✅ Colors are consistent.")
            lines.append(f"\nUsing {len(analysis.colors.unique_colors)} colors.")
        lines.append("")
        
        # Typography
        lines.append("## Typography")
        lines.append("")
        if analysis.typography.has_issues:
            lines.append(f"- Font sizes: **{len(analysis.typography.font_sizes)}** (`{', '.join(analysis.typography.font_sizes[:6])}`)")
            lines.append(f"- Font weights: **{len(analysis.typography.font_weights)}** (`{', '.join(analysis.typography.font_weights[:4])}`)")
            if analysis.typography.font_families:
                lines.append(f"- Font families: **{len(analysis.typography.font_families)}** (`{', '.join(analysis.typography.font_families)}`)")
            lines.append("")
            for issue in analysis.typography.issues:
                lines.append(f"- {self._severity_emoji(issue.severity)} [{issue.category}] {issue.suggestion}")
        else:
            lines.append("✅ Typography is consistent.")
            if analysis.typography.font_sizes:
                lines.append(f"\nFont sizes: `{', '.join(analysis.typography.font_sizes[:6])}`")
        lines.append("")
        
        # Border Radius
        lines.append("## Border Radius")
        lines.append("")
        if analysis.border_radius.has_issues:
            lines.append(f"Found **{len(analysis.border_radius.unique_values)}** unique values: `{', '.join(analysis.border_radius.unique_values)}`")
            lines.append("")
            for issue in analysis.border_radius.issues:
                lines.append(f"- {self._severity_emoji(issue.severity)} {issue.suggestion}")
            if analysis.border_radius.suggested_values:
                lines.append(f"\n**Suggested values:** `{', '.join(analysis.border_radius.suggested_values)}`")
        else:
            lines.append("✅ Border radius is consistent.")
            if analysis.border_radius.unique_values:
                lines.append(f"\nUsing: `{', '.join(analysis.border_radius.unique_values)}`")
        lines.append("")
        
        # Shadows
        lines.append("## Shadows")
        lines.append("")
        if analysis.shadows.has_issues:
            lines.append(f"Found **{len(analysis.shadows.unique_values)}** unique values.")
            lines.append("")
            for issue in analysis.shadows.issues:
                lines.append(f"- {self._severity_emoji(issue.severity)} {issue.suggestion}")
            if analysis.shadows.suggested_values:
                lines.append(f"\n**Suggested values:** `{', '.join(analysis.shadows.suggested_values)}`")
        else:
            lines.append("✅ Shadows are consistent.")
            if analysis.shadows.unique_values:
                lines.append(f"\nUsing: `{', '.join(analysis.shadows.unique_values)}`")
        lines.append("")
        
        # Next steps
        lines.append("---")
        lines.append("")
        if analysis.has_issues:
            lines.append("**Next steps:**")
            lines.append("1. Fix the inconsistencies above")
            lines.append("2. Run `vibe lock` to save your design system")
            lines.append("3. Run `vibe enforce` to prevent future drift")
        else:
            lines.append("**Next steps:**")
            lines.append("1. Run `vibe lock` to save your design system")
            lines.append("2. Run `vibe enforce` to prevent future drift")
        lines.append("")
        
        return "\n".join(lines)
    
    def _severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level."""
        emojis = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
        }
        return emojis.get(severity, "•")
