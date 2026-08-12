"""Math/physics core for the spiral art generator.

The pattern is N chords through a fixed center point, all rotating together
under uniform circular motion, with a constant angular offset between
adjacent lines:

    theta_i(t)  = theta0(t) + i * delta_phi          for i = 0 .. N-1
    theta0(t)   = theta0(t - dt) + omega * dt         (Euler-integrated angular velocity)

At delta_phi = 360/N the lines are evenly spaced into a symmetric radial
star. Detuning delta_phi away from that breaks the symmetry, and combined
with a fading trail (drawn by the caller), the rotating pattern traces out
drifting spiral / moire shapes.
"""
from __future__ import annotations

import math

import pygame

DEFAULT_NUM_LINES = 12
DEFAULT_LINE_WIDTH = 2
DEFAULT_SPEED = 1.0  # omega, radians/second
DEFAULT_ROTATION_DEG = 360.0 / DEFAULT_NUM_LINES  # delta_phi, degrees between adjacent lines

NUM_LINES_RANGE = (2, 60)
LINE_WIDTH_RANGE = (1, 10)
SPEED_RANGE = (-5.0, 5.0)
ROTATION_RANGE_DEG = (0.0, 180.0)


class SpiralField:
    def __init__(
        self,
        num_lines: int = DEFAULT_NUM_LINES,
        line_width: int = DEFAULT_LINE_WIDTH,
        speed: float = DEFAULT_SPEED,
        rotation_deg: float = DEFAULT_ROTATION_DEG,
    ) -> None:
        self.num_lines = num_lines
        self.line_width = line_width
        self.speed = speed  # omega, rad/s
        self.rotation_deg = rotation_deg  # delta_phi, degrees
        self.theta0 = 0.0  # radians, integrated over time

    def update(self, dt: float) -> None:
        self.theta0 += self.speed * dt

    @property
    def theta0_deg(self) -> float:
        return math.degrees(self.theta0) % 360.0

    @property
    def speed_deg(self) -> float:
        return math.degrees(self.speed)

    def line_angles(self):
        delta_phi = math.radians(self.rotation_deg)
        for i in range(self.num_lines):
            yield self.theta0 + i * delta_phi

    def draw(self, surface: "pygame.Surface", center: tuple[float, float], radius: float, color) -> None:
        cx, cy = center
        for theta in self.line_angles():
            dx, dy = math.cos(theta) * radius, math.sin(theta) * radius
            start = (cx - dx, cy - dy)
            end = (cx + dx, cy + dy)
            pygame.draw.line(surface, color, start, end, self.line_width)
