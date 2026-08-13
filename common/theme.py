"""Chalkboard Lecture Hall: the shared visual theme for equation_gallery
(and available to any future project in this repo).

Palette, fonts, and small rendering helpers live here so every scene draws
from one source of truth instead of inventing its own RGB tuples.
"""
from __future__ import annotations

import random

import pygame

BOARD = (27, 43, 34)          # main content background -- deep chalkboard green
BOARD_DARK = (20, 32, 25)     # sidebar/ledge background
CHALK = (237, 234, 224)       # primary lines/text -- off-white chalk
CHALK_GOLD = (232, 185, 77)   # math category, active states, primary emphasis
CHALK_BLUE = (127, 176, 204)  # physics category, secondary data/HUD numbers
CHALK_CORAL = (217, 119, 87)  # sparing use: special callouts
WOOD = (92, 70, 48)           # sidebar divider, tile outlines, frame accents

# Two chalk faces, used deliberately for different jobs:
#  - DISPLAY is Chalkduster: rough, literal chalk texture. Reads great big
#    and rough, harder to read small -- reserved for the one big signature
#    formula headline per scene.
#  - UI is Chalkboard SE: a cleaner handwriting face, legible at the smaller
#    sizes used everywhere else (titles, labels, sidebar rows).
_DISPLAY_FAMILY = "chalkduster,chalkboardse,bradleyhand,comicsansms"
_UI_FAMILY = "chalkboardse,bradleyhand,noteworthy,comicsansms"
_MONO_FAMILY = "menlo,consolas,monospace"

_font_cache: dict[tuple[str, int, bool], pygame.font.Font] = {}


def _cached_font(family: str, size: int, bold: bool) -> pygame.font.Font:
    key = (family, size, bold)
    if key not in _font_cache:
        font = pygame.font.SysFont(family, size, bold=bold)
        _font_cache[key] = font
    return _font_cache[key]


def display_font(size: int, bold: bool = False) -> pygame.font.Font:
    """The big rough-chalk face -- for the one signature formula per scene."""
    return _cached_font(_DISPLAY_FAMILY, size, bold)


def chalk_font(size: int, bold: bool = False) -> pygame.font.Font:
    """The general handwriting face -- titles, labels, sidebar rows."""
    return _cached_font(_UI_FAMILY, size, bold)


def mono_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Precise monospace -- equations-as-data and HUD numbers."""
    return _cached_font(_MONO_FAMILY, size, bold)


def fit_display_text(text: str, max_width: int, max_size: int = 34, min_size: int = 18):
    """Pick the largest display-font size (within [min_size, max_size]) that
    renders `text` no wider than max_width, and return (font, rendered_surface).

    Long formulas (Fourier's, projectile motion's) shrink to fit; short ones
    (Mandelbrot's "z = z^2 + c") get to stay big and dramatic.
    """
    size = max_size
    font = display_font(size)
    surface = font.render(text, True, CHALK)
    while surface.get_width() > max_width and size > min_size:
        size -= 1
        font = display_font(size)
        surface = font.render(text, True, CHALK)
    return font, surface


_texture_cache: dict[tuple[int, int], pygame.Surface] = {}


def chalk_texture(width: int, height: int) -> pygame.Surface:
    """A static field of faint chalk-dust flecks. Cached and reused --
    real chalk dust doesn't shift from frame to frame, so this must only be
    generated once per size, not redrawn every draw() call.
    """
    key = (width, height)
    if key in _texture_cache:
        return _texture_cache[key]

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    rng = random.Random(20260812)  # fixed seed: the same dust every run
    for _ in range(280):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        alpha = rng.randint(6, 22)
        radius = rng.choice((1, 1, 1, 2))
        pygame.draw.circle(surface, (*CHALK, alpha), (x, y), radius)
    _texture_cache[key] = surface
    return surface
