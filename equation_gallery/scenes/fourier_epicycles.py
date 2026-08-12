"""Fourier epicycles: a chain of rotating vectors drawing a square wave.

A square wave can be built from a sum of its odd harmonics (3Blue1Brown's
"epicycles" demo):

    f(t) = (4/pi) * sum over odd k=1,3,5,... of sin(k*omega*t)/k

Rather than plotting the sum directly, each odd term is represented as a
vector of length amplitude_k = (4/(pi*k)) * scale spinning at angle k*t,
chained tip-to-tail. The final tip's height traces the (approximate) square
wave, which is plotted scrolling off to the right. As N (the number of
harmonic terms) increases, the plotted wave visibly sharpens toward a true
square wave, with the classic overshoot "ringing" at each edge -- the Gibbs
phenomenon -- that never fully disappears no matter how many terms are used.
"""
from __future__ import annotations

import collections
import math

import pygame

from common.scene import Scene
from common.ui import Slider, draw_hud

N_RANGE = (1, 15)
DEFAULT_N = 5
SPEED_RANGE = (0.1, 3.0)
DEFAULT_SPEED = 0.5
SCALE = 80.0  # pixel scale for the k=1 amplitude (~1.27 * SCALE at most)
HISTORY_LEN = 300


class FourierEpicyclesScene(Scene):
    title = "Fourier Epicycles"
    category = "math"
    formula = "f(t) = (4/pi) * sum[k odd] sin(k*omega*t)/k"

    def reset(self) -> None:
        self.t = 0.0
        self.history = collections.deque(maxlen=HISTORY_LEN)
        self.font = pygame.font.SysFont("menlo,consolas,monospace", 16)
        self.sliders = [
            Slider(20, 65, 230, *N_RANGE, DEFAULT_N, "Lines  N (terms)", fmt="{:.0f}"),
            Slider(20, 107, 230, *SPEED_RANGE, DEFAULT_SPEED, "Speed  omega (rad/s)", fmt="{:.2f}"),
        ]

    def update(self, dt: float) -> None:
        speed = self.sliders[1].value
        self.t += speed * dt

    def draw(self, surface: "pygame.Surface") -> None:
        n_terms = int(round(self.sliders[0].value))

        # Small backing rect so the two sliders stay legible over the chain.
        backing = pygame.Surface((250, 100), pygame.SRCALPHA)
        backing.fill((10, 10, 12, 160))
        surface.blit(backing, (10, 55))

        anchor = (self.width * 0.30, self.height * 0.55)
        pos = anchor
        angle_base = self.t
        for i in range(n_terms):
            k = 2 * i + 1  # odd harmonics: 1, 3, 5, ...
            amplitude = (4.0 / (math.pi * k)) * SCALE
            angle = k * angle_base
            next_pos = (pos[0] + amplitude * math.cos(angle), pos[1] + amplitude * math.sin(angle))

            pygame.draw.circle(surface, (70, 70, 78), (int(pos[0]), int(pos[1])), int(amplitude), 1)
            pygame.draw.line(surface, (150, 200, 255), pos, next_pos, 2)

            pos = next_pos

        tip = pos
        pygame.draw.circle(surface, (255, 220, 90), (int(tip[0]), int(tip[1])), 5)

        # Plot region on the right: a horizontal guide from the tip to the
        # plot, then the scrolling history of the tip's height (relative to
        # the anchor/zero-line).
        plot_left = tip[0]
        plot_right = self.width * 0.95
        plot_width = plot_right - plot_left
        plot_center_y = anchor[1]

        pygame.draw.line(surface, (120, 120, 120), (plot_left, tip[1]), (plot_right, tip[1]), 1)
        pygame.draw.line(surface, (60, 60, 66), (plot_left, plot_center_y), (plot_right, plot_center_y), 1)

        self.history.appendleft(tip[1] - anchor[1])
        points = []
        for i, y_offset in enumerate(self.history):
            x = plot_left + i * (plot_width / HISTORY_LEN)
            y = plot_center_y + y_offset
            points.append((x, y))
        if len(points) >= 2:
            pygame.draw.lines(surface, (255, 220, 90), False, points, 2)

        hud_lines = [
            f"N = {n_terms} term(s) (k = 1..{2 * n_terms - 1})",
            f"t = {self.t:6.2f} s",
        ]
        draw_hud(surface, self.font, hud_lines, (self.width * 0.62, self.height * 0.15))
