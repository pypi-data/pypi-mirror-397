"""Tests for the scanner module."""

import pytest
from pathlib import Path

from vibe.scanner import scan_directory
from vibe.scanner.files import discover_files
from vibe.scanner.tailwind import extract_tailwind_classes


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestFileDiscovery:
    """Tests for file discovery."""
    
    def test_discover_tsx_files(self):
        """Should discover .tsx files."""
        files = discover_files(FIXTURES_DIR)
        tsx_files = [f for f in files if f.suffix == ".tsx"]
        assert len(tsx_files) >= 1
        assert any("sample_components" in str(f) for f in tsx_files)
    
    def test_skip_node_modules(self, tmp_path):
        """Should skip node_modules directory."""
        # Create a file in node_modules
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "test.tsx").write_text("const x = 1;")
        
        # Create a file outside node_modules
        (tmp_path / "app.tsx").write_text("const y = 2;")
        
        files = discover_files(tmp_path)
        assert len(files) == 1
        assert "app.tsx" in str(files[0])


class TestTailwindExtractor:
    """Tests for Tailwind class extraction."""
    
    def test_extract_spacing_classes(self):
        """Should extract spacing classes."""
        file_path = FIXTURES_DIR / "sample_components.tsx"
        result = extract_tailwind_classes(file_path)
        
        # Should find p-4, p-3, px-4, py-2, etc.
        assert len(result.spacing) > 0
        assert any("p-4" in cls for cls in result.spacing)
    
    def test_extract_color_classes(self):
        """Should extract color classes."""
        file_path = FIXTURES_DIR / "sample_components.tsx"
        result = extract_tailwind_classes(file_path)
        
        # Should find bg-white, text-gray-600, bg-blue-500, etc.
        assert len(result.colors) > 0
        assert any("bg-white" in cls for cls in result.colors)
        assert any("blue" in cls for cls in result.colors)
    
    def test_extract_typography_classes(self):
        """Should extract typography classes."""
        file_path = FIXTURES_DIR / "sample_components.tsx"
        result = extract_tailwind_classes(file_path)
        
        # Should find text-xl, font-bold, etc.
        assert len(result.typography) > 0
        assert any("text-xl" in cls or "text-lg" in cls for cls in result.typography)
        assert any("font-bold" in cls or "font-medium" in cls for cls in result.typography)
    
    def test_extract_arbitrary_values(self):
        """Should extract arbitrary values."""
        file_path = FIXTURES_DIR / "sample_components.tsx"
        result = extract_tailwind_classes(file_path)
        
        # Should find bg-[#ff6b6b], text-[42px], font-[Fira_Code]
        assert len(result.arbitrary_values) > 0
        assert any("#ff6b6b" in cls for cls in result.arbitrary_values)
    
    def test_strip_responsive_prefixes(self):
        """Should handle responsive prefixes."""
        file_path = FIXTURES_DIR / "sample_components.tsx"
        result = extract_tailwind_classes(file_path)
        
        # md:grid-cols-2, lg:grid-cols-3 should be found
        # (they're in CardGrid component)
        # These aren't spacing/color/typography, but the extractor should handle them


class TestScanDirectory:
    """Tests for full directory scanning."""
    
    def test_scan_fixtures(self):
        """Should scan fixture files."""
        result = scan_directory(FIXTURES_DIR)
        
        assert result.files_scanned >= 1
        assert result.total_classes > 0
    
    def test_scan_counts(self):
        """Should count all extracted values."""
        result = scan_directory(FIXTURES_DIR)
        
        assert len(result.spacing_classes) > 0
        assert len(result.color_classes) > 0
        assert len(result.typography_classes) > 0
        assert len(result.arbitrary_values) > 0
