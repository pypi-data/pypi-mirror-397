"""
File discovery - Find all relevant files to scan.
"""

from pathlib import Path


# File extensions to scan
SCANNABLE_EXTENSIONS = {
    # Component files (Tailwind classes)
    ".tsx",
    ".jsx",
    ".html",
    ".vue",
    ".svelte",
    # Stylesheets (CSS properties)
    ".css",
    ".scss",
}

# Directories to skip
SKIP_DIRECTORIES = {
    "node_modules",
    ".git",
    ".next",
    ".nuxt",
    "dist",
    "build",
    ".vibe",
    "__pycache__",
    ".pytest_cache",
    "coverage",
    ".turbo",
    ".vercel",
}


def discover_files(path: Path) -> list[Path]:
    """
    Discover all scannable files in a directory.
    
    Args:
        path: Root directory to search
        
    Returns:
        List of file paths to scan
    """
    files: list[Path] = []
    
    if path.is_file():
        if path.suffix in SCANNABLE_EXTENSIONS:
            return [path]
        return []
    
    for item in path.rglob("*"):
        # Skip directories in SKIP_DIRECTORIES
        if any(skip_dir in item.parts for skip_dir in SKIP_DIRECTORIES):
            continue
        
        # Only include files with scannable extensions
        if item.is_file() and item.suffix in SCANNABLE_EXTENSIONS:
            files.append(item)
    
    return sorted(files)
