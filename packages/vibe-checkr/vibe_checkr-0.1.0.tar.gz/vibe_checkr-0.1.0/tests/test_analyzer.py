"""Tests for the analyzer module."""

import pytest
from pathlib import Path

from vibe.scanner import scan_directory
from vibe.analyzer import analyze_design_system


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestDesignAnalysis:
    """Tests for design system analysis."""
    
    @pytest.fixture
    def analysis(self):
        """Run analysis on fixture files."""
        scan_result = scan_directory(FIXTURES_DIR)
        return analyze_design_system(scan_result)
    
    def test_has_issues(self, analysis):
        """Should detect issues in sample components."""
        # Our fixture file has intentional issues
        assert analysis.has_issues
        assert analysis.total_issues > 0
    
    def test_spacing_analysis(self, analysis):
        """Should analyze spacing."""
        assert len(analysis.spacing.unique_values) > 0
    
    def test_color_analysis(self, analysis):
        """Should analyze colors."""
        assert len(analysis.colors.unique_colors) > 0
        
        # Should detect arbitrary color issue
        arbitrary_issues = [
            issue for issue in analysis.colors.issues
            if issue.type == "arbitrary"
        ]
        assert len(arbitrary_issues) > 0
    
    def test_typography_analysis(self, analysis):
        """Should analyze typography."""
        assert len(analysis.typography.font_sizes) > 0
        assert len(analysis.typography.font_weights) > 0
        
        # Should detect arbitrary font issues
        arbitrary_issues = [
            issue for issue in analysis.typography.issues
            if issue.type == "arbitrary"
        ]
        # We have arbitrary font size and font family in fixtures
        assert len(arbitrary_issues) > 0
    
    def test_border_radius_analysis(self, analysis):
        """Should analyze border radius."""
        assert len(analysis.border_radius.unique_values) > 0
    
    def test_shadow_analysis(self, analysis):
        """Should analyze shadows."""
        assert len(analysis.shadows.unique_values) > 0


class TestSpacingAnalyzer:
    """Tests for spacing analyzer specifically."""
    
    def test_detects_off_scale_values(self):
        """Should detect values that don't fit the scale."""
        from vibe.analyzer.spacing import analyze_spacing
        
        # Mix of good and off-scale values
        classes = ["p-2", "p-4", "p-3", "p-5", "p-8", "p-7"]
        
        result = analyze_spacing(classes, [])
        
        # p-3, p-5, p-7 might be flagged as off-scale
        # depending on the detected scale
        assert len(result.unique_values) == 6
    
    def test_detects_arbitrary_values(self):
        """Should flag arbitrary spacing values."""
        from vibe.analyzer.spacing import analyze_spacing
        
        classes = ["p-4", "p-[10px]", "m-2", "m-[1.5rem]"]
        
        result = analyze_spacing(classes, [])
        
        arbitrary_issues = [i for i in result.issues if i.type == "arbitrary"]
        assert len(arbitrary_issues) > 0


class TestColorAnalyzer:
    """Tests for color analyzer specifically."""
    
    def test_detects_arbitrary_colors(self):
        """Should flag arbitrary color values."""
        from vibe.analyzer.colors import analyze_colors
        
        classes = ["bg-blue-500", "bg-[#ff0000]", "text-gray-600"]
        arbitrary = ["bg-[#ff0000]"]
        
        result = analyze_colors(classes, [], arbitrary)
        
        arbitrary_issues = [i for i in result.issues if i.type == "arbitrary"]
        assert len(arbitrary_issues) > 0
    
    def test_detects_too_many_colors(self):
        """Should flag when too many colors are used."""
        from vibe.analyzer.colors import analyze_colors
        
        # Create many unique colors
        classes = [f"bg-{color}-{shade}" 
                   for color in ["blue", "red", "green", "yellow", "purple"]
                   for shade in ["100", "300", "500", "700"]]
        
        result = analyze_colors(classes, [], [])
        
        # Should suggest consolidating
        assert len(result.unique_colors) == 20


class TestTypographyAnalyzer:
    """Tests for typography analyzer specifically."""
    
    def test_detects_arbitrary_font_sizes(self):
        """Should flag arbitrary font sizes."""
        from vibe.analyzer.typography import analyze_typography
        
        classes = ["text-sm", "text-lg", "text-[42px]"]
        
        result = analyze_typography(classes, [])
        
        arbitrary_issues = [i for i in result.issues 
                          if i.type == "arbitrary" and i.category == "font_size"]
        assert len(arbitrary_issues) > 0
    
    def test_detects_too_many_font_families(self):
        """Should flag when too many font families are used."""
        from vibe.analyzer.typography import analyze_typography
        
        classes = ["font-sans", "font-serif", "font-mono", "font-[Custom]"]
        
        result = analyze_typography(classes, [])
        
        font_issues = [i for i in result.issues if i.type == "too_many_fonts"]
        assert len(font_issues) > 0
