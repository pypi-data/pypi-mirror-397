"""
Console reporter - Beautiful terminal output using Rich.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markup import escape

from vibe.analyzer import DesignAnalysis


class ActionItem:
    """A single actionable item for the user."""
    
    def __init__(
        self,
        severity: str,
        category: str,
        action: str,
        details: list[str] | None = None
    ):
        self.severity = severity  # "error", "warning", "info"
        self.category = category  # "colors", "spacing", etc.
        self.action = action      # What to do
        self.details = details    # Specific values involved


class ConsoleReporter:
    """Report analysis results to the console."""
    
    def __init__(self, console: Console | None = None, verbose: bool = False):
        self.console = console or Console()
        self.verbose = verbose
    
    def report(self, analysis: DesignAnalysis) -> None:
        """Print analysis results to console."""
        
        # Collect all actionable items
        actions = self._collect_actions(analysis)
        
        # Group by severity
        errors = [a for a in actions if a.severity == "error"]
        warnings = [a for a in actions if a.severity == "warning"]
        infos = [a for a in actions if a.severity == "info"]
        
        # Print category summaries first
        self._print_category_summaries(analysis)
        
        # Print actionable items by severity
        self.console.print()
        self.console.print("─" * 60)
        self.console.print()
        
        if errors:
            self._print_action_group("🔴 ERRORS", "Must fix", errors, "red")
        
        if warnings:
            self._print_action_group("🟡 WARNINGS", "Should fix", warnings, "yellow")
        
        if infos:
            self._print_action_group("🔵 SUGGESTIONS", "Consider fixing", infos, "blue")
        
        # Print summary
        self.console.print("─" * 60)
        self.console.print()
        
        total = len(errors) + len(warnings) + len(infos)
        if total == 0:
            self.console.print("[bold green]✓ No issues found! Your design system is consistent.[/bold green]")
        else:
            summary_parts = []
            if errors:
                summary_parts.append(f"[red]{len(errors)} error{'s' if len(errors) != 1 else ''}[/red]")
            if warnings:
                summary_parts.append(f"[yellow]{len(warnings)} warning{'s' if len(warnings) != 1 else ''}[/yellow]")
            if infos:
                summary_parts.append(f"[blue]{len(infos)} suggestion{'s' if len(infos) != 1 else ''}[/blue]")
            
            self.console.print(f"[bold]Summary:[/bold] {' · '.join(summary_parts)}")
    
    def _collect_actions(self, analysis: DesignAnalysis) -> list[ActionItem]:
        """Collect all actionable items from analysis."""
        actions: list[ActionItem] = []
        
        # Spacing actions
        for issue in analysis.spacing.issues:
            if issue.type == "arbitrary":
                for value in issue.values:
                    actions.append(ActionItem(
                        severity="error",
                        category="spacing",
                        action=f"Replace arbitrary spacing `{escape(value)}` with a scale value",
                        details=[value]
                    ))
            elif issue.type == "inconsistent":
                actions.append(ActionItem(
                    severity="warning",
                    category="spacing",
                    action=f"Consolidate {len(issue.values)} spacing values to 6-8",
                    details=issue.values[:8]
                ))
            elif issue.type == "off_scale":
                actions.append(ActionItem(
                    severity="info",
                    category="spacing",
                    action=f"Values {issue.values[:5]} break the spacing scale",
                    details=issue.values
                ))
        
        # Color actions
        for issue in analysis.colors.issues:
            if issue.type == "arbitrary":
                for value in issue.values:
                    actions.append(ActionItem(
                        severity="error",
                        category="colors",
                        action=f"Replace arbitrary color `{escape(value)}` with a theme color",
                        details=[value]
                    ))
            elif issue.type == "one_off":
                actions.append(ActionItem(
                    severity="info",
                    category="colors",
                    action=f"Consolidate {len(issue.values)} one-off colors (used only 1-2x)",
                    details=issue.values[:6]
                ))
            elif issue.type == "similar":
                actions.append(ActionItem(
                    severity="info",
                    category="colors",
                    action=f"Reduce {len(issue.values)} shades to 2-3: {', '.join(issue.values[:4])}",
                    details=issue.values
                ))
            elif issue.type == "inconsistent":
                actions.append(ActionItem(
                    severity="warning",
                    category="colors",
                    action=f"Too many colors ({len(analysis.colors.unique_colors)}). Limit to 10-12.",
                    details=None
                ))
        
        # Typography actions
        for issue in analysis.typography.issues:
            if issue.type == "arbitrary" and issue.category == "font_size":
                for value in issue.values:
                    actions.append(ActionItem(
                        severity="error",
                        category="typography",
                        action=f"Replace arbitrary font size `{escape(value)}` with scale value",
                        details=[value]
                    ))
            elif issue.type == "arbitrary" and issue.category == "font_weight":
                for value in issue.values:
                    actions.append(ActionItem(
                        severity="error",
                        category="typography",
                        action=f"Replace arbitrary font weight `{escape(value)}` with named weight",
                        details=[value]
                    ))
            elif issue.type == "arbitrary" and issue.category == "font_family":
                for value in issue.values:
                    actions.append(ActionItem(
                        severity="error",
                        category="typography",
                        action=f"Move `{escape(value)}` to tailwind.config.js",
                        details=[value]
                    ))
            elif issue.type == "too_many_fonts":
                actions.append(ActionItem(
                    severity="warning",
                    category="typography",
                    action=f"Reduce font families from {len(issue.values)} to 1-2",
                    details=issue.values
                ))
            elif issue.type == "inconsistent_weights":
                actions.append(ActionItem(
                    severity="info",
                    category="typography",
                    action=f"Reduce font weights from {len(issue.values)} to 2-3 (normal, medium, bold)",
                    details=issue.values
                ))
            elif issue.type == "off_scale":
                actions.append(ActionItem(
                    severity="info",
                    category="typography",
                    action=f"Reduce font sizes from {len(issue.values)} to 5-6",
                    details=issue.values
                ))
        
        # Border radius actions
        for issue in analysis.border_radius.issues:
            if issue.type == "arbitrary":
                for value in issue.values:
                    actions.append(ActionItem(
                        severity="error",
                        category="border-radius",
                        action=f"Replace arbitrary radius `{escape(value)}` with scale value",
                        details=[value]
                    ))
            elif issue.type == "too_many":
                actions.append(ActionItem(
                    severity="warning",
                    category="border-radius",
                    action=f"Reduce border radius from {len(issue.values)} to 2-3 values",
                    details=issue.values
                ))
            elif issue.type == "inconsistent":
                actions.append(ActionItem(
                    severity="info",
                    category="border-radius",
                    action=f"Pick one of similar values: {', '.join(issue.values)}",
                    details=issue.values
                ))
        
        # Shadow actions
        for issue in analysis.shadows.issues:
            if issue.type == "arbitrary":
                for value in issue.values:
                    actions.append(ActionItem(
                        severity="error",
                        category="shadows",
                        action=f"Replace arbitrary shadow `{escape(value)}` with scale value",
                        details=[value]
                    ))
            elif issue.type == "too_many":
                actions.append(ActionItem(
                    severity="warning",
                    category="shadows",
                    action=f"Reduce shadows from {len(issue.values)} to 2-3 values",
                    details=issue.values
                ))
            elif issue.type == "inconsistent":
                actions.append(ActionItem(
                    severity="info",
                    category="shadows",
                    action=f"Pick one of similar values: {', '.join(issue.values)}",
                    details=issue.values
                ))
        
        return actions
    
    def _print_category_summaries(self, analysis: DesignAnalysis) -> None:
        """Print a summary for each category."""
        
        # Spacing
        self.console.print()
        if analysis.spacing.has_issues:
            self.console.print(f"[yellow]SPACING[/yellow] — {len(analysis.spacing.unique_values)} values")
        else:
            self.console.print(f"[green]✓ SPACING[/green] — {len(analysis.spacing.unique_values)} values")
        if self.verbose and analysis.spacing.unique_values:
            self.console.print(f"  [dim]{', '.join(analysis.spacing.unique_values[:10])}[/dim]")
        
        # Colors
        if analysis.colors.has_issues:
            self.console.print(f"[yellow]COLORS[/yellow] — {len(analysis.colors.unique_colors)} colors")
        else:
            self.console.print(f"[green]✓ COLORS[/green] — {len(analysis.colors.unique_colors)} colors")
        if self.verbose and analysis.colors.unique_colors:
            top_colors = [f"{c.value} ({c.count}x)" for c in analysis.colors.unique_colors[:5]]
            self.console.print(f"  [dim]{', '.join(top_colors)}[/dim]")
        
        # Typography
        type_summary = f"{len(analysis.typography.font_sizes)} sizes, {len(analysis.typography.font_weights)} weights"
        if analysis.typography.font_families:
            type_summary += f", {len(analysis.typography.font_families)} families"
        
        if analysis.typography.has_issues:
            self.console.print(f"[yellow]TYPOGRAPHY[/yellow] — {type_summary}")
        else:
            self.console.print(f"[green]✓ TYPOGRAPHY[/green] — {type_summary}")
        if self.verbose:
            self.console.print(f"  [dim]Sizes: {', '.join(analysis.typography.font_sizes[:6])}[/dim]")
            self.console.print(f"  [dim]Weights: {', '.join(analysis.typography.font_weights[:4])}[/dim]")
        
        # Border radius
        if analysis.border_radius.has_issues:
            self.console.print(f"[yellow]BORDER RADIUS[/yellow] — {len(analysis.border_radius.unique_values)} values")
        else:
            self.console.print(f"[green]✓ BORDER RADIUS[/green] — {len(analysis.border_radius.unique_values)} values")
        if self.verbose and analysis.border_radius.unique_values:
            self.console.print(f"  [dim]{', '.join(analysis.border_radius.unique_values)}[/dim]")
        
        # Shadows
        if analysis.shadows.has_issues:
            self.console.print(f"[yellow]SHADOWS[/yellow] — {len(analysis.shadows.unique_values)} values")
        else:
            self.console.print(f"[green]✓ SHADOWS[/green] — {len(analysis.shadows.unique_values)} values")
        if self.verbose and analysis.shadows.unique_values:
            self.console.print(f"  [dim]{', '.join(analysis.shadows.unique_values)}[/dim]")
    
    def _print_action_group(
        self,
        title: str,
        subtitle: str,
        actions: list[ActionItem],
        color: str
    ) -> None:
        """Print a group of actions."""
        self.console.print(f"[bold {color}]{title}[/bold {color}] — {subtitle}")
        self.console.print()
        
        for i, action in enumerate(actions, 1):
            self.console.print(f"  {i}. [{color}]{action.category}[/{color}]: {action.action}")
            
            if self.verbose and action.details:
                details_str = ', '.join(escape(str(d)) for d in action.details[:6])
                if len(action.details) > 6:
                    details_str += f" (+{len(action.details) - 6} more)"
                self.console.print(f"     [dim]→ {details_str}[/dim]")
        
        self.console.print()
