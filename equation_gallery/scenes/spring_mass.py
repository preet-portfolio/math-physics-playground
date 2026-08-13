"""Spring-mass-damper: Hooke's law with linear damping.

m * x'' = -k * x - c * x'

x is displacement from equilibrium. Integrated with several semi-implicit
Euler substeps per frame for stability (same pattern as the other scenes in
this batch). Two small bar-meters show kinetic and potential energy trading
back and forth (and bleeding away under damping).
"""
from __future__ import annotations

import math

import pygame

from common import theme
from common.scene import Scene
from common.ui import Slider, draw_hud

K_RANGE = (1.0, 50.0)
DEFAULT_K = 10.0
M_RANGE = (0.5, 5.0)
DEFAULT_M = 1.0
DAMPING_RANGE = (0.0, 5.0)
DEFAULT_DAMPING = 0.3
X0_RANGE = (-2.0, 2.0)
DEFAULT_X0 = 1.5
SUBSTEPS = 8
PX_PER_UNIT = 120.0  # pixels per unit of x
EQUILIBRIUM_OFFSET = 150.0  # rest-length gap between wall and block, px


class SpringMassScene(Scene):
    title = "Spring-Mass Oscillator"
    category = "physics"
    formula = "m*x'' = -k*x - c*x'"

    def reset(self) -> None:
        # Build sliders only once: main.py calls reset() again on [R] on this
        # same scene instance, and x0 (like the other initial-condition
        # sliders in this batch) must re-launch from whatever the user has
        # it set to -- rebuilding the sliders here would snap it back to its
        # default every time.
        if not self.sliders:
            self.font = theme.mono_font(16)
            self.sliders = [
                Slider(20, 115, 230, *K_RANGE, DEFAULT_K, "k  spring const", fmt="{:.1f}"),
                Slider(20, 157, 230, *M_RANGE, DEFAULT_M, "m  mass", fmt="{:.2f}"),
                Slider(20, 199, 230, *DAMPING_RANGE, DEFAULT_DAMPING, "c  damping", fmt="{:.2f}"),
                Slider(20, 241, 230, *X0_RANGE, DEFAULT_X0, "x0  initial displacement", fmt="{:.2f}"),
            ]
        self.x = self.sliders[3].value
        self.v = 0.0
        k = self.sliders[0].value
        # Total initial energy, used to scale the KE/PE bar meters so a
        # reasonable max maps to full bar height.
        self.max_energy = 0.5 * k * self.x ** 2

    def update(self, dt: float) -> None:
        k = self.sliders[0].value
        m = self.sliders[1].value
        damping = self.sliders[2].value

        dt_sub = dt / SUBSTEPS
        for _ in range(SUBSTEPS):
            a = -(k / m) * self.x - (damping / m) * self.v
            self.v += a * dt_sub
            self.x += self.v * dt_sub

    def draw(self, surface: "pygame.Surface") -> None:
        k = self.sliders[0].value
        m = self.sliders[1].value
        damping = self.sliders[2].value

        anchor = (self.width * 0.4, self.height * 0.4)
        block_x = anchor[0] + EQUILIBRIUM_OFFSET + self.x * PX_PER_UNIT
        block_y = anchor[1]

        # Wall hatch.
        pygame.draw.line(surface, theme.WOOD, (anchor[0], anchor[1] - 40), (anchor[0], anchor[1] + 40), 4)

        # Zigzag spring from wall to block.
        segments = 7
        points = [anchor]
        for i in range(1, segments):
            t = i / segments
            zig_x = anchor[0] + t * (block_x - anchor[0])
            zig_y = block_y + (18 if i % 2 == 0 else -18)
            points.append((zig_x, zig_y))
        points.append((block_x, block_y))
        pygame.draw.lines(surface, theme.CHALK, False, points, 2)

        block_rect = pygame.Rect(0, 0, 40, 40)
        block_rect.center = (int(block_x), int(block_y))
        pygame.draw.rect(surface, theme.CHALK_GOLD, block_rect)

        # Energy bar meters.
        ke = 0.5 * m * self.v ** 2
        pe = 0.5 * k * self.x ** 2
        max_energy = max(self.max_energy, 1e-9)
        bar_max_h = 200.0
        bar_bottom = self.height * 0.75

        ke_x = self.width * 0.75
        pe_x = self.width * 0.82
        bar_w = 30.0

        ke_h = min(1.0, ke / max_energy) * bar_max_h
        pe_h = min(1.0, pe / max_energy) * bar_max_h

        pygame.draw.rect(surface, theme.WOOD, (ke_x, bar_bottom - bar_max_h, bar_w, bar_max_h), 1)
        pygame.draw.rect(surface, theme.WOOD, (pe_x, bar_bottom - bar_max_h, bar_w, bar_max_h), 1)
        pygame.draw.rect(surface, theme.CHALK_BLUE, (ke_x, bar_bottom - ke_h, bar_w, ke_h))
        pygame.draw.rect(surface, theme.CHALK_CORAL, (pe_x, bar_bottom - pe_h, bar_w, pe_h))

        self.draw_panel_backing(surface)

        ke_label = self.font.render("KE", True, theme.CHALK_BLUE)
        pe_label = self.font.render("PE", True, theme.CHALK_CORAL)
        surface.blit(ke_label, (ke_x + bar_w / 2 - ke_label.get_width() / 2, bar_bottom + 4))
        surface.blit(pe_label, (pe_x + bar_w / 2 - pe_label.get_width() / 2, bar_bottom + 4))

        omega0 = math.sqrt(k / m)
        period = 2 * math.pi / omega0
        zeta = damping / (2 * math.sqrt(m * k))
        if zeta < 0.999:
            regime = "underdamped"
        elif zeta > 1.001:
            regime = "overdamped"
        else:
            regime = "critically damped"

        hud_lines = [
            f"omega0 = sqrt(k/m) = {omega0:5.2f} rad/s",
            f"period = 2*pi/omega0 = {period:5.2f} s",
            f"zeta = c/(2*sqrt(mk)) = {zeta:5.3f}  ({regime})",
            f"x = {self.x:+.3f}   v = {self.v:+.3f}",
        ]
        draw_hud(surface, self.font, hud_lines, (self.width * 0.55, self.height * 0.15))
