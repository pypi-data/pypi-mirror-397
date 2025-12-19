"""
Tailwind class extractor - Extract and categorize Tailwind utility classes.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class TailwindExtraction:
    """Extracted Tailwind classes by category."""
    
    spacing: list[str] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)
    typography: list[str] = field(default_factory=list)
    border_radius: list[str] = field(default_factory=list)
    shadows: list[str] = field(default_factory=list)
    arbitrary_values: list[str] = field(default_factory=list)


# Regex patterns for extracting class strings
CLASS_PATTERNS = [
    # className="..." or className='...'
    r'className=["\']([^"\']+)["\']',
    # className={`...`} (template literals)
    r'className=\{`([^`]+)`\}',
    # class="..." or class='...' (HTML/Vue)
    r'class=["\']([^"\']+)["\']',
    # :class="..." (Vue dynamic)
    r':class=["\']([^"\']+)["\']',
    # clsx(...), cn(...), classNames(...) - common utilities
    r'(?:clsx|cn|classNames)\(([^)]+)\)',
]

# Tailwind class patterns by category
SPACING_PATTERNS = [
    r'^-?[pm][xytblr]?-\d+(?:\.5)?$',      # p-4, mx-2, -mt-4, py-0.5
    r'^-?[pm][xytblr]?-\[.+\]$',            # p-[10px], m-[2rem]
    r'^gap-\d+(?:\.5)?$',                   # gap-4
    r'^gap-[xy]-\d+(?:\.5)?$',              # gap-x-4
    r'^gap-\[.+\]$',                        # gap-[10px]
    r'^space-[xy]-\d+(?:\.5)?$',            # space-x-4
    r'^space-[xy]-\[.+\]$',                 # space-x-[10px]
]

COLOR_PATTERNS = [
    r'^(?:bg|text|border|ring|fill|stroke|outline|accent|caret|decoration)-(?:inherit|current|transparent|black|white)$',
    r'^(?:bg|text|border|ring|fill|stroke|outline|accent|caret|decoration)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d+$',
    r'^(?:bg|text|border|ring|fill|stroke|outline|accent|caret|decoration)-\[.+\]$',  # Arbitrary colors
    r'^from-',    # Gradient from
    r'^via-',     # Gradient via
    r'^to-',      # Gradient to
]

TYPOGRAPHY_PATTERNS = [
    # Font size
    r'^text-(?:xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)$',
    r'^text-\[.+\]$',                       # Arbitrary font size
    # Font weight
    r'^font-(?:thin|extralight|light|normal|medium|semibold|bold|extrabold|black)$',
    r'^font-\[\d+\]$',                      # Arbitrary font weight
    # Font family
    r'^font-(?:sans|serif|mono)$',
    r'^font-\[.+\]$',                       # Arbitrary font family
    # Line height
    r'^leading-(?:none|tight|snug|normal|relaxed|loose|\d+)$',
    r'^leading-\[.+\]$',                    # Arbitrary line height
    # Letter spacing
    r'^tracking-(?:tighter|tight|normal|wide|wider|widest)$',
    r'^tracking-\[.+\]$',                   # Arbitrary letter spacing
    # Text align, transform, etc.
    r'^(?:uppercase|lowercase|capitalize|normal-case)$',
    r'^(?:truncate|text-ellipsis|text-clip)$',
    r'^(?:underline|overline|line-through|no-underline)$',
]

BORDER_RADIUS_PATTERNS = [
    r'^rounded(?:-(?:none|sm|md|lg|xl|2xl|3xl|full))?$',
    r'^rounded-[tblr](?:-(?:none|sm|md|lg|xl|2xl|3xl|full))?$',
    r'^rounded-(?:tl|tr|bl|br)(?:-(?:none|sm|md|lg|xl|2xl|3xl|full))?$',
    r'^rounded-\[.+\]$',                    # Arbitrary border radius
]

SHADOW_PATTERNS = [
    r'^shadow(?:-(?:sm|md|lg|xl|2xl|inner|none))?$',
    r'^shadow-\[.+\]$',                     # Arbitrary shadow
    r'^drop-shadow(?:-(?:sm|md|lg|xl|2xl|none))?$',
    r'^drop-shadow-\[.+\]$',                # Arbitrary drop shadow
]

# Arbitrary value pattern
ARBITRARY_PATTERN = r'^.+-\[.+\]$'


def extract_tailwind_classes(file_path: Path) -> TailwindExtraction:
    """
    Extract Tailwind classes from a file and categorize them.
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        TailwindExtraction with classes categorized by type
    """
    result = TailwindExtraction()
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return result
    
    # Extract all class strings
    all_classes: list[str] = []
    
    for pattern in CLASS_PATTERNS:
        matches = re.findall(pattern, content)
        for match in matches:
            # Split class string into individual classes
            classes = match.split()
            all_classes.extend(classes)
    
    # Categorize each class
    for cls in all_classes:
        # Remove responsive/state prefixes for categorization
        base_class = _strip_prefixes(cls)
        
        # Check for arbitrary values
        if re.match(ARBITRARY_PATTERN, base_class):
            result.arbitrary_values.append(cls)
        
        # Categorize by type
        if _matches_any(base_class, SPACING_PATTERNS):
            result.spacing.append(cls)
        elif _matches_any(base_class, COLOR_PATTERNS):
            result.colors.append(cls)
        elif _matches_any(base_class, TYPOGRAPHY_PATTERNS):
            result.typography.append(cls)
        elif _matches_any(base_class, BORDER_RADIUS_PATTERNS):
            result.border_radius.append(cls)
        elif _matches_any(base_class, SHADOW_PATTERNS):
            result.shadows.append(cls)
    
    return result


def _strip_prefixes(cls: str) -> str:
    """
    Strip responsive and state prefixes from a Tailwind class.
    
    Examples:
        md:p-4 -> p-4
        hover:bg-blue-500 -> bg-blue-500
        dark:md:hover:text-white -> text-white
    """
    # Common prefixes to strip
    prefixes = [
        # Responsive
        "sm:", "md:", "lg:", "xl:", "2xl:",
        # Dark mode
        "dark:",
        # States
        "hover:", "focus:", "active:", "disabled:", "visited:",
        "focus-within:", "focus-visible:",
        # Group/peer states
        "group-hover:", "group-focus:", "peer-hover:", "peer-focus:",
        # First/last/odd/even
        "first:", "last:", "odd:", "even:",
        # Before/after
        "before:", "after:",
        # Placeholder
        "placeholder:",
        # Selection
        "selection:",
        # Print
        "print:",
    ]
    
    result = cls
    changed = True
    
    while changed:
        changed = False
        for prefix in prefixes:
            if result.startswith(prefix):
                result = result[len(prefix):]
                changed = True
                break
    
    return result


def _matches_any(cls: str, patterns: list[str]) -> bool:
    """Check if a class matches any of the given regex patterns."""
    for pattern in patterns:
        if re.match(pattern, cls):
            return True
    return False
