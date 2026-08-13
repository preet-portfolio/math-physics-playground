"""Golden ratio spiral: a Fibonacci square tiling plus a log spiral.

Two overlaid constructions of the same idea:

  1. A FIXED flush tiling of squares whose side lengths are the true
     Fibonacci sequence (1, 1, 2, 3, 5, 8, ...). Only the exact additive
     Fibonacci recurrence tiles with no gaps or overlaps, so this part is
     drawn once from fixed values -- it is not slider-controlled.
  2. A logarithmic spiral r(theta) = r0 * b**theta, with
     b = growth ** (2/pi) so the radius multiplies by `growth` every
     quarter turn. THIS is the interactive part: growth = phi =
     (1+sqrt(5))/2 reproduces the classic golden spiral that nests near
     the square tiling; dragging the slider away from phi shows how
     special that one ratio is.
"""
from __future__ import annotations

import math

import pygame

from common import theme
from common.scene import Scene
from common.ui import Slider, draw_hud

PHI = (1 + 5 ** 0.5) / 2
GROWTH_RANGE = (1.0, 2.5)
SQUARE_COLOR = theme.WOOD
SPIRAL_COLOR = theme.CHALK_GOLD
GOLDEN_CALLOUT_TOL = 0.01
SPIRAL_TURNS = 4 * math.pi  # two full turns
SPIRAL_STEPS = 200
SPIRAL_R0 = 4.0  # starting radius, in the same local unit coords as the squares


class GoldenSpiralScene(Scene):
    title = "Golden Ratio Spiral"
    category = "math"
    formula = "r(theta) = r0 * growth^(2*theta/pi)"

    def reset(self) -> None:
        self.font = theme.mono_font(16)
        if not self.sliders:
            self.sliders = [
                Slider(20, 115, 230, *GROWTH_RANGE, PHI, "growth  (x per 1/4 turn)", fmt="{:.3f}"),
            ]

        # Fixed Fibonacci square tiling (not slider-controlled -- see module docstring).
        fib = [1, 1]
        n = 10
        for i in range(2, n):
            fib.append(fib[-1] + fib[-2])

        directions = ["left", "below", "right", "above"]  # cycle starting at i=1
        squares = [(0, 0, fib[0])]  # (top-left x, top-left y, side) in local unit coords
        left, top, right, bottom = 0, 0, fib[0], fib[0]

        for i in range(1, n):
            side = fib[i]
            d = directions[(i - 1) % 4]
            if d == "left":
                nx, ny = left - side, top
                left -= side
            elif d == "below":
                nx, ny = left, bottom
                bottom += side
            elif d == "right":
                nx, ny = right, top
                right += side
            else:  # "above"
                nx, ny = left, top - side
                top -= side
            squares.append((nx, ny, side))

        self.squares = squares
        self.square0_side = fib[0]

        bbox_w, bbox_h = right - left, bottom - top
        avail_w, avail_h = self.width * 0.55, self.height * 0.7
        self.px_scale = min(avail_w / bbox_w, avail_h / bbox_h)
        self.origin_x = self.width * 0.40 - (left + bbox_w / 2) * self.px_scale
        self.origin_y = self.height * 0.5 - (top + bbox_h / 2) * self.px_scale

    def update(self, dt: float) -> None:
        pass  # static tiling + spiral are recomputed from the slider each draw() call

    def _to_screen(self, local_x: float, local_y: float) -> tuple[float, float]:
        return (
            self.origin_x + local_x * self.px_scale,
            self.origin_y + local_y * self.px_scale,
        )

    def draw(self, surface: "pygame.Surface") -> None:
        for x, y, side in self.squares:
            top_left = self._to_screen(x, y)
            rect = pygame.Rect(top_left[0], top_left[1], side * self.px_scale, side * self.px_scale)
            pygame.draw.rect(surface, SQUARE_COLOR, rect, width=1)

        growth = self.sliders[0].value
        b = growth ** (2 / math.pi)
        # Spiral's local origin: the (left, bottom) corner of square 0, so it
        # visually nests near/inside the first unit square.
        origin_lx, origin_ly = 0.0, float(self.square0_side)

        points = []
        for i in range(SPIRAL_STEPS + 1):
            theta = SPIRAL_TURNS * i / SPIRAL_STEPS
            r = SPIRAL_R0 * b ** theta
            lx = origin_lx + r * math.cos(theta)
            ly = origin_ly + r * math.sin(theta)
            points.append(self._to_screen(lx, ly))

        if len(points) >= 2:
            pygame.draw.lines(surface, SPIRAL_COLOR, False, points, 2)

        self.draw_panel_backing(surface)
        hud_lines = [f"growth = {growth:.3f}   b = growth^(2/pi) = {b:.3f}"]
        draw_hud(surface, self.font, hud_lines, (20, 700))
        if abs(growth - PHI) < GOLDEN_CALLOUT_TOL:
            draw_hud(surface, self.font, ["== golden ratio (phi)!"], (20, 724), color=theme.CHALK_CORAL)
