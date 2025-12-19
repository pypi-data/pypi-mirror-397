"""Lock module - Generate and save design system."""

from vibe.lock.generator import generate_design_system
from vibe.lock.schema import DesignSystem

__all__ = ["generate_design_system", "DesignSystem"]
