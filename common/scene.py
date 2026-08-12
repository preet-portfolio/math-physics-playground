"""Shared contract for equation_gallery scenes.

The gallery's main loop only ever calls these methods, so any scene that
implements them can be dropped into the menu. Each scene owns its own
sliders (from common.ui.Slider) and its own numerical integration -- there's
no shared "physics engine" since the equations are all different shapes.
"""
from __future__ import annotations

import pygame


class Scene:
    title: str = "Untitled"
    category: str = "math"  # "math" or "physics", controls menu column
    formula: str = ""  # short equation string shown in the header

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.sliders: list = []  # populated by subclasses in reset()
        self.reset()

    def reset(self) -> None:
        """Reset simulation state (and rebuild self.sliders) to initial conditions."""

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle a non-reset, non-menu event. Default: forward to sliders."""
        for slider in self.sliders:
            slider.handle_event(event)

    def update(self, dt: float) -> None:
        """Advance the simulation by dt seconds."""

    def draw(self, surface: "pygame.Surface") -> None:
        """Render current simulation state (not sliders/HUD)."""

    def draw_sliders(self, surface: "pygame.Surface", font) -> None:
        for slider in self.sliders:
            slider.draw(surface, font)
