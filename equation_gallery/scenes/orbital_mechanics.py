"""Orbital mechanics: a single body orbiting a fixed central mass under
real inverse-square gravity.

    r  = sqrt(x**2 + y**2)
    ax = -GM * x / r**3
    ay = -GM * y / r**3

i.e. acceleration a = -GM * r_hat / r^2, pointing from the orbiting body
toward the fixed central mass at the origin.

Integrated with semi-implicit (symplectic) Euler, deliberately not RK4:
velocity is updated first from the acceleration at the *current* position,
then position is updated using the *new* velocity. That ordering is what
makes semi-implicit Euler symplectic -- it conserves a "shadow" energy close
to the true orbital energy over long integrations, so a circular orbit stays
circular for many periods. A naive (non-symplectic) integrator of the same
order -- explicit Euler, or even RK4 for that matter -- has no such
conservation property here and would visibly spiral in or out over time.
"""
from __future__ import annotations

import math
from collections import deque

import pygame

from common import theme
from common.scene import Scene
from common.ui import Slider, draw_hud

GM = 4_500_000.0  # fixed, not slider-controlled
R0 = 200.0  # initial orbital radius (pixels; 1 unit = 1 pixel)
V_CIRCULAR = math.sqrt(GM / R0)  # ~150.0
V_ESCAPE = math.sqrt(2 * GM / R0)  # ~212.1

V0_RANGE = (0.0, 320.0)
DEFAULT_V0 = V_CIRCULAR

SUBSTEPS = 4
TRAIL_MAXLEN = 5000

# Tolerance band around epsilon = 0 for the "parabolic" classification --
# epsilon here runs into the thousands, so +/-1.0 is a tight band that just
# avoids flicker exactly at the escape threshold.
EPSILON_BAND = 1.0


class OrbitalMechanicsScene(Scene):
    title = "Orbital Mechanics"
    category = "physics"
    formula = "a = -GM * r_hat / r^2"

    def reset(self) -> None:
        self.font = theme.mono_font(16)
        if not self.sliders:
            self.sliders = [
                Slider(20, 115, 230, *V0_RANGE, DEFAULT_V0, "v0  tangential speed", fmt="{:.1f}"),
            ]

        self.x = R0
        self.y = 0.0
        self.vx = 0.0
        self.vy = -self.sliders[0].value

        self.trail: deque = deque(maxlen=TRAIL_MAXLEN)
        self.trail.append((self.x, self.y))

    def update(self, dt: float) -> None:
        dt_sub = dt / SUBSTEPS
        for _ in range(SUBSTEPS):
            r = math.hypot(self.x, self.y)
            ax = -GM * self.x / r ** 3
            ay = -GM * self.y / r ** 3
            # Symplectic Euler: velocity from the *current* position first,
            # then position from the *new* velocity -- order matters.
            self.vx += ax * dt_sub
            self.vy += ay * dt_sub
            self.x += self.vx * dt_sub
            self.y += self.vy * dt_sub
        self.trail.append((self.x, self.y))

    def draw(self, surface: "pygame.Surface") -> None:
        center = (self.width * 0.62, self.height * 0.5)

        pygame.draw.circle(surface, theme.CHALK_GOLD, (int(center[0]), int(center[1])), 14)

        if len(self.trail) >= 2:
            points = [(center[0] + px, center[1] + py) for px, py in self.trail]
            pygame.draw.lines(surface, theme.CHALK_BLUE, False, points, 1)

        body_pos = (center[0] + self.x, center[1] + self.y)
        pygame.draw.circle(surface, theme.CHALK, (int(body_pos[0]), int(body_pos[1])), 8)
        self.draw_panel_backing(surface)

        r = math.hypot(self.x, self.y)
        speed = math.hypot(self.vx, self.vy)
        epsilon = 0.5 * speed ** 2 - GM / r  # specific orbital energy

        if epsilon < -EPSILON_BAND:
            classification = "elliptical/circular orbit"
        elif epsilon <= EPSILON_BAND:
            classification = "parabolic (near escape threshold)"
        else:
            classification = "hyperbolic (escaping)"

        hud_lines = [
            f"v_circular = sqrt(GM/r0)   = {V_CIRCULAR:6.1f}",
            f"v_escape   = sqrt(2GM/r0)  = {V_ESCAPE:6.1f}",
            f"speed = {speed:6.1f}   r = {r:7.1f}",
            f"epsilon (specific energy) = {epsilon:+9.2f}",
            classification,
        ]
        draw_hud(surface, self.font, hud_lines, (self.width * 0.55, self.height * 0.72))
