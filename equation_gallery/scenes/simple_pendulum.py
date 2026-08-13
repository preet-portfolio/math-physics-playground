"""Simple pendulum: the full nonlinear equation of motion, not the small-angle
linear approximation.

theta'' = -(g/L) * sin(theta) - b * theta'

theta is measured from the downward vertical (theta = 0 hangs straight down),
b is a linear damping coefficient acting on angular velocity. Integrated with
several semi-implicit Euler substeps per frame for stability (see other
scenes in this batch for the same pattern).

The classic small-angle period T = 2*pi*sqrt(L/g) is only exact in the limit
theta0 -> 0; it's shown as a reference line in the HUD, but at large initial
angles the true nonlinear swing takes noticeably longer per cycle than that
approximation predicts.
"""
from __future__ import annotations

import math

import pygame

from common import theme
from common.scene import Scene
from common.ui import Slider, draw_hud

L_RANGE = (0.5, 3.0)
DEFAULT_L = 1.5
G_RANGE = (2.0, 20.0)
DEFAULT_G = 9.81
DAMPING_RANGE = (0.0, 2.0)
DEFAULT_DAMPING = 0.1
THETA0_RANGE = (10.0, 170.0)
DEFAULT_THETA0_DEG = 60.0
SUBSTEPS = 8
PX_PER_LENGTH = 150.0  # pixels per meter of rod length


class SimplePendulumScene(Scene):
    title = "Simple Pendulum"
    category = "physics"
    formula = "theta'' = -(g/L) sin(theta) - b*theta'"

    def reset(self) -> None:
        # Build sliders only once: main.py calls reset() again on [R] on this
        # same scene instance, and theta0 (like the other initial-condition
        # sliders in this batch) must re-launch from whatever the user has
        # it set to -- rebuilding the sliders here would snap it back to its
        # default every time.
        if not self.sliders:
            self.font = theme.mono_font(16)
            self.sliders = [
                Slider(20, 115, 230, *L_RANGE, DEFAULT_L, "L  length (m)", fmt="{:.2f}"),
                Slider(20, 157, 230, *G_RANGE, DEFAULT_G, "g  gravity (m/s^2)", fmt="{:.2f}"),
                Slider(20, 199, 230, *DAMPING_RANGE, DEFAULT_DAMPING, "b  damping", fmt="{:.2f}"),
                Slider(20, 241, 230, *THETA0_RANGE, DEFAULT_THETA0_DEG, "theta0 (deg)", fmt="{:.0f}"),
            ]
        self.theta = math.radians(self.sliders[3].value)
        self.omega = 0.0

    def update(self, dt: float) -> None:
        L = self.sliders[0].value
        g = self.sliders[1].value
        damping = self.sliders[2].value

        dt_sub = dt / SUBSTEPS
        for _ in range(SUBSTEPS):
            alpha = -(g / L) * math.sin(self.theta) - damping * self.omega
            self.omega += alpha * dt_sub
            self.theta += self.omega * dt_sub

    def draw(self, surface: "pygame.Surface") -> None:
        L = self.sliders[0].value
        g = self.sliders[1].value

        pivot = (self.width * 0.6, self.height * 0.25)
        rod_len = L * PX_PER_LENGTH
        bob = (
            pivot[0] + rod_len * math.sin(self.theta),
            pivot[1] + rod_len * math.cos(self.theta),
        )

        pygame.draw.line(surface, theme.CHALK, pivot, bob, 2)
        pygame.draw.circle(surface, theme.CHALK_GOLD, (int(bob[0]), int(bob[1])), 14)
        pygame.draw.circle(surface, theme.WOOD, (int(pivot[0]), int(pivot[1])), 4)
        self.draw_panel_backing(surface)

        t_small = 2 * math.pi * math.sqrt(L / g)
        hud_lines = [
            f"T_small = 2*pi*sqrt(L/g) = {t_small:5.2f} s  (small-angle approx)",
            f"theta = {math.degrees(self.theta):7.1f} deg",
            f"omega = {self.omega:+6.2f} rad/s",
            "note: at large theta0 the real period exceeds T_small",
        ]
        draw_hud(surface, self.font, hud_lines, (self.width * 0.55, self.height * 0.55))
