"""Lissajous curves: two perpendicular sinusoids at different frequencies.

x(t) = A*sin(a*t + delta)
y(t) = B*sin(b*t)

The x:y frequency ratio a:b and the phase offset delta determine the
curve's shape (circles, figure-eights, more intricate closed loops for
higher integer ratios). Time is integrated the same way as
spiral_art_generator (self.t += speed * dt each frame), and a fading
trail -- owned by this scene since draw() has no persistent state of its
own -- traces the curve out over time using the same fade-blit technique
as spiral_art_generator/main.py.
"""
from __future__ import annotations

import math

import pygame

from common.scene import Scene
from common.ui import Slider, draw_hud

BACKGROUND = (10, 10, 12)
TRAIL_ALPHA = 25  # lower = longer-lived trail

A_FREQ_RANGE = (1, 10)
B_FREQ_RANGE = (1, 10)
DELTA_RANGE = (0.0, 2 * math.pi)
SPEED_RANGE = (0.1, 4.0)

DEFAULT_A = 3
DEFAULT_B = 2
DEFAULT_DELTA = math.pi / 2
DEFAULT_SPEED = 1.0


class LissajousScene(Scene):
    title = "Lissajous Curves"
    category = "math"
    formula = "x=A sin(at+d), y=B sin(bt)"

    def reset(self) -> None:
        self.t = 0.0
        self.last_point = None
        self.font = pygame.font.SysFont("menlo,consolas,monospace", 16)

        self.trail = pygame.Surface((self.width, self.height))
        self.trail.fill(BACKGROUND)
        self.fade_overlay = pygame.Surface((self.width, self.height))
        self.fade_overlay.fill(BACKGROUND)
        self.fade_overlay.set_alpha(TRAIL_ALPHA)

        panel_size = (260, 214)
        self.panel_surface = pygame.Surface(panel_size)
        self.panel_surface.set_alpha(180)
        self.panel_surface.fill((20, 20, 24))

        self.sliders = [
            Slider(20, 65, 230, *A_FREQ_RANGE, DEFAULT_A, "a  (x-frequency)", fmt="{:.0f}"),
            Slider(20, 107, 230, *B_FREQ_RANGE, DEFAULT_B, "b  (y-frequency)", fmt="{:.0f}"),
            Slider(20, 149, 230, *DELTA_RANGE, DEFAULT_DELTA, "delta  (phase, rad)", fmt="{:.2f}"),
            Slider(20, 191, 230, *SPEED_RANGE, DEFAULT_SPEED, "speed", fmt="{:.2f}"),
        ]

    def update(self, dt: float) -> None:
        speed = self.sliders[3].value
        self.t += speed * dt

    def draw(self, surface: "pygame.Surface") -> None:
        a = round(self.sliders[0].value)  # rounded so the curve stays a clean closed figure
        b = round(self.sliders[1].value)
        delta = self.sliders[2].value

        cx, cy = self.width * 0.6, self.height * 0.55
        amp = min(self.width, self.height) * 0.32

        x = cx + amp * math.sin(a * self.t + delta)
        y = cy + amp * math.sin(b * self.t)
        point = (x, y)

        self.trail.blit(self.fade_overlay, (0, 0))
        if self.last_point is None:
            pygame.draw.circle(self.trail, (255, 220, 90), (int(x), int(y)), 2)
        else:
            pygame.draw.line(self.trail, (120, 200, 255), self.last_point, point, 2)
        self.last_point = point

        surface.blit(self.trail, (0, 0))
        pygame.draw.circle(surface, (255, 220, 90), (int(x), int(y)), 4)

        surface.blit(self.panel_surface, (10, 40))
        hud_lines = [
            f"a:b = {a}:{b}   delta = {delta:.2f} rad",
            f"x(t) = A sin({a}t + {delta:.2f})",
            f"y(t) = A sin({b}t)",
            f"t = {self.t:6.2f} s",
        ]
        draw_hud(surface, self.font, hud_lines, (20, 260))
