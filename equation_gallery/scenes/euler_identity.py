"""Euler's identity: a unit vector rotating in the complex plane.

theta(t) = theta(t - dt) + omega * dt        (uniform circular motion, same
                                               integration as spiral_art_generator)
e^(i*theta) = cos(theta) + i*sin(theta)

Traces the classic "unit circle -> sine wave" relationship and calls out
e^(i*pi) + 1 = 0 whenever theta crosses pi (mod 2*pi).
"""
from __future__ import annotations

import math

import pygame

from common.scene import Scene
from common.ui import Slider, draw_hud

DEFAULT_SPEED = 1.0  # omega, rad/s
SPEED_RANGE = (-3.0, 3.0)


class EulerIdentityScene(Scene):
    title = "Euler's Identity"
    category = "math"
    formula = "e^(i*theta) = cos(theta) + i*sin(theta)"

    def reset(self) -> None:
        self.theta = 0.0
        self.font = pygame.font.SysFont("menlo,consolas,monospace", 16)
        self.callout_font = pygame.font.SysFont("menlo,consolas,monospace", 22, bold=True)
        self.sliders = [
            Slider(20, 80, 240, *SPEED_RANGE, DEFAULT_SPEED, "Speed  omega (rad/s)", fmt="{:.2f}"),
        ]

    def update(self, dt: float) -> None:
        omega = self.sliders[0].value
        self.theta += omega * dt

    def draw(self, surface: "pygame.Surface") -> None:
        cx, cy = self.width * 0.32, self.height * 0.55
        radius = min(self.width, self.height) * 0.28

        pygame.draw.circle(surface, (60, 60, 66), (int(cx), int(cy)), int(radius), 1)
        pygame.draw.line(surface, (90, 90, 96), (cx - radius - 20, cy), (cx + radius + 20, cy), 1)
        pygame.draw.line(surface, (90, 90, 96), (cx, cy - radius - 20), (cx, cy + radius + 20), 1)

        x = math.cos(self.theta) * radius
        y = math.sin(self.theta) * radius
        tip = (cx + x, cy - y)  # screen y grows downward; flip so +y is "up" like standard math

        pygame.draw.line(surface, (255, 255, 255), (cx, cy), tip, 2)
        pygame.draw.circle(surface, (255, 220, 90), (int(tip[0]), int(tip[1])), 6)

        pygame.draw.line(surface, (120, 200, 255), tip, (cx, cy - y), 1)  # projection onto y-axis (sin)
        pygame.draw.line(surface, (255, 150, 150), tip, (cx + x, cy), 1)  # projection onto x-axis (cos)

        theta_mod = self.theta % (2 * math.pi)
        near_pi = min(abs(theta_mod - math.pi), abs(theta_mod - math.pi - 2 * math.pi))
        if near_pi < 0.03:
            callout = self.callout_font.render("e^(i*pi) + 1 = 0", True, (255, 220, 90))
            surface.blit(callout, (self.width * 0.55, self.height * 0.3))

        cos_v, sin_v = math.cos(self.theta), math.sin(self.theta)
        hud_lines = [
            f"theta = {math.degrees(self.theta) % 360:6.1f} deg",
            f"e^(i*theta) = {cos_v:+.3f} {'+' if sin_v >= 0 else '-'} {abs(sin_v):.3f}i",
        ]
        draw_hud(surface, self.font, hud_lines, (self.width * 0.55, self.height * 0.55))
