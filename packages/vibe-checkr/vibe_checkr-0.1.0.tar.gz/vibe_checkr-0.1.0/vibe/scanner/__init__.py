"""
Scanner module - Extract design tokens from codebase.
"""

from pathlib import Path
from dataclasses import dataclass, field

from vibe.scanner.files import discover_files
from vibe.scanner.tailwind import extract_tailwind_classes
from vibe.scanner.css import extract_css_properties


@dataclass
class ScanResult:
    """Results from scanning a codebase."""
    
    # Metadata
    files_scanned: int = 0
    
    # Tailwind classes by category
    spacing_classes: list[str] = field(default_factory=list)
    color_classes: list[str] = field(default_factory=list)
    typography_classes: list[str] = field(default_factory=list)
    border_radius_classes: list[str] = field(default_factory=list)
    shadow_classes: list[str] = field(default_factory=list)
    
    # CSS properties
    css_colors: list[str] = field(default_factory=list)
    css_spacing: list[str] = field(default_factory=list)
    css_typography: list[dict] = field(default_factory=list)
    css_border_radius: list[str] = field(default_factory=list)
    css_shadows: list[str] = field(default_factory=list)
    
    # Arbitrary Tailwind values (e.g., bg-[#ff0000])
    arbitrary_values: list[str] = field(default_factory=list)
    
    @property
    def total_classes(self) -> int:
        return (
            len(self.spacing_classes) +
            len(self.color_classes) +
            len(self.typography_classes) +
            len(self.border_radius_classes) +
            len(self.shadow_classes)
        )
    
    @property
    def total_css_properties(self) -> int:
        return (
            len(self.css_colors) +
            len(self.css_spacing) +
            len(self.css_typography) +
            len(self.css_border_radius) +
            len(self.css_shadows)
        )


def scan_directory(path: Path) -> ScanResult:
    """
    Scan a directory for design tokens.
    
    Args:
        path: Directory to scan
        
    Returns:
        ScanResult with all extracted design tokens
    """
    result = ScanResult()
    
    # Discover all relevant files
    files = discover_files(path)
    result.files_scanned = len(files)
    
    for file_path in files:
        if file_path.suffix in [".tsx", ".jsx", ".html", ".vue", ".svelte"]:
            # Extract Tailwind classes
            tailwind_result = extract_tailwind_classes(file_path)
            
            result.spacing_classes.extend(tailwind_result.spacing)
            result.color_classes.extend(tailwind_result.colors)
            result.typography_classes.extend(tailwind_result.typography)
            result.border_radius_classes.extend(tailwind_result.border_radius)
            result.shadow_classes.extend(tailwind_result.shadows)
            result.arbitrary_values.extend(tailwind_result.arbitrary_values)
            
        elif file_path.suffix in [".css", ".scss"]:
            # Extract CSS properties
            css_result = extract_css_properties(file_path)
            
            result.css_colors.extend(css_result.colors)
            result.css_spacing.extend(css_result.spacing)
            result.css_typography.extend(css_result.typography)
            result.css_border_radius.extend(css_result.border_radius)
            result.css_shadows.extend(css_result.shadows)
    
    return result
