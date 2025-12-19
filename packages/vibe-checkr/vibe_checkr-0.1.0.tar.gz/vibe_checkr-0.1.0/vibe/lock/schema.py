"""
Design system schema - Pydantic models for .vibe/system.json
"""

from pydantic import BaseModel, Field
from typing import Any


class SpacingSystem(BaseModel):
    """Spacing scale definition."""
    
    scale: list[int] = Field(default_factory=list, description="Spacing scale in Tailwind units")
    tailwind_classes: list[str] = Field(default_factory=list, description="Allowed Tailwind spacing classes")


class ColorDefinition(BaseModel):
    """A single color in the palette."""
    
    name: str = Field(description="Semantic name for the color")
    value: str = Field(description="Color value (Tailwind class or hex)")
    hex: str | None = Field(default=None, description="Hex value if known")
    usage: str | None = Field(default=None, description="Intended usage (primary, secondary, etc.)")


class TypographySystem(BaseModel):
    """Typography scale definition."""
    
    font_sizes: list[str] = Field(default_factory=list, description="Allowed font sizes")
    font_weights: list[str] = Field(default_factory=list, description="Allowed font weights")
    font_families: list[str] = Field(default_factory=list, description="Allowed font families")
    line_heights: list[str] = Field(default_factory=list, description="Allowed line heights")
    letter_spacings: list[str] = Field(default_factory=list, description="Allowed letter spacings")


class BorderRadiusSystem(BaseModel):
    """Border radius scale definition."""
    
    scale: list[str] = Field(default_factory=list, description="Allowed border radius values")


class ShadowSystem(BaseModel):
    """Shadow scale definition."""
    
    scale: list[str] = Field(default_factory=list, description="Allowed shadow values")


class DesignSystem(BaseModel):
    """Complete design system definition."""
    
    version: str = Field(default="1.0", description="Schema version")
    locked: bool = Field(default=True, description="Whether the system is locked")
    
    spacing: SpacingSystem = Field(default_factory=SpacingSystem)
    colors: list[ColorDefinition] = Field(default_factory=list)
    typography: TypographySystem = Field(default_factory=TypographySystem)
    border_radius: BorderRadiusSystem = Field(default_factory=BorderRadiusSystem)
    shadows: ShadowSystem = Field(default_factory=ShadowSystem)
    
    # Metadata
    generated_at: str | None = Field(default=None, description="When the system was generated")
    source_path: str | None = Field(default=None, description="Path that was scanned")
    
    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "locked": True,
                "spacing": {
                    "scale": [0, 1, 2, 4, 6, 8, 12, 16],
                    "tailwind_classes": ["p-0", "p-1", "p-2", "p-4", "p-6", "p-8", "p-12", "p-16"]
                },
                "colors": [
                    {"name": "primary", "value": "blue-500", "hex": "#3b82f6", "usage": "primary"},
                    {"name": "secondary", "value": "gray-600", "hex": "#4b5563", "usage": "secondary"}
                ],
                "typography": {
                    "font_sizes": ["sm", "base", "lg", "xl", "2xl"],
                    "font_weights": ["normal", "medium", "bold"],
                    "font_families": ["sans"],
                    "line_heights": ["normal", "relaxed"],
                    "letter_spacings": ["normal"]
                },
                "border_radius": {
                    "scale": ["md", "lg", "full"]
                },
                "shadows": {
                    "scale": ["sm", "md", "lg"]
                }
            }
        }
