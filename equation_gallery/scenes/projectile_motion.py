"""Projectile motion: closed-form kinematics, or numerical integration when
quadratic air drag is enabled.

No drag (closed form):
    x(t) = v0*cos(theta)*t
    y(t) = v0*sin(theta)*t - 0.5*g*t^2

With drag (drag slider > 0), the closed form no longer applies, so velocity
is integrated instead. Quadratic drag opposes velocity proportional to
speed^2:
    ax = -drag*speed*vx
    ay = -g - drag*speed*vy
using the same semi-implicit Euler substep pattern as the other scenes in
this batch.

y is measured upward from the launch point; the screen's y axis grows
downward, so drawing flips it: screen_y = launch_screen_y - y*scale.
"""
from __future__ import annotations

import math

import pygame

from common import theme
from common.scene import Scene
from common.ui import Slider, draw_hud

ANGLE_RANGE = (5.0, 85.0)
DEFAULT_ANGLE_DEG = 45.0
V0_RANGE = (5.0, 60.0)
DEFAULT_V0 = 30.0
G_RANGE = (2.0, 20.0)
DEFAULT_G = 9.81
DRAG_RANGE = (0.0, 0.05)
DEFAULT_DRAG = 0.0
SUBSTEPS = 8
PX_PER_METER = 2.0


class ProjectileMotionScene(Scene):
    title = "Projectile Motion"
    category = "physics"
    formula = "x=v0 cos(th) t,  y=v0 sin(th) t - 0.5 g t^2"

    def reset(self) -> None:
        # Build sliders only once: main.py calls reset() again on [R] on this
        # same scene instance, and angle/v0 (the initial-condition sliders in
        # this scene) must re-launch from whatever the user has them set to
        # -- rebuilding the sliders here would snap them back to defaults
        # every time.
        if not self.sliders:
            self.font = theme.mono_font(16)
            self.sliders = [
                Slider(20, 115, 230, *ANGLE_RANGE, DEFAULT_ANGLE_DEG, "angle (deg)", fmt="{:.0f}"),
                Slider(20, 157, 230, *V0_RANGE, DEFAULT_V0, "v0  launch speed", fmt="{:.1f}"),
                Slider(20, 199, 230, *G_RANGE, DEFAULT_G, "g  gravity (m/s^2)", fmt="{:.2f}"),
                Slider(20, 241, 230, *DRAG_RANGE, DEFAULT_DRAG, "drag coeff", fmt="{:.3f}"),
            ]
        angle = math.radians(self.sliders[0].value)
        v0 = self.sliders[1].value

        # Cache the launch conditions so dragging angle/v0 mid-flight can't
        # teleport the running trajectory -- only reset() reads them as
        # initial conditions, per the convention used across this batch.
        self._launch_angle = angle
        self._launch_v0 = v0

        self.t = 0.0
        self.x = 0.0
        self.y = 0.0
        self.vx = v0 * math.cos(angle)
        self.vy = v0 * math.sin(angle)
        self.landed = False
        self.trajectory = [(0.0, 0.0)]
        self.landed_x = None

    def update(self, dt: float) -> None:
        if self.landed:
            return

        g = self.sliders[2].value
        drag = self.sliders[3].value

        if drag == 0.0:
            # Closed-form kinematics, driven by the cached launch conditions
            # (not the live sliders, so dragging angle/v0 mid-flight doesn't
            # teleport the trajectory).
            angle = self._launch_angle
            v0 = self._launch_v0
            self.t += dt
            self.x = v0 * math.cos(angle) * self.t
            self.y = v0 * math.sin(angle) * self.t - 0.5 * g * self.t ** 2
            self.vx = v0 * math.cos(angle)
            self.vy = v0 * math.sin(angle) - g * self.t
        else:
            # Numerical integration with quadratic drag, semi-implicit Euler
            # substeps for stability.
            dt_sub = dt / SUBSTEPS
            for _ in range(SUBSTEPS):
                speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
                ax = -drag * speed * self.vx
                ay = -g - drag * speed * self.vy
                self.vx += ax * dt_sub
                self.vy += ay * dt_sub
                self.x += self.vx * dt_sub
                self.y += self.vy * dt_sub
            self.t += dt

        self.trajectory.append((self.x, self.y))

        if self.y < 0 and self.t > 0.01:
            self.y = 0.0
            self.landed = True
            self.landed_x = self.x

    def draw(self, surface: "pygame.Surface") -> None:
        angle_deg = self.sliders[0].value
        v0 = self.sliders[1].value
        g = self.sliders[2].value
        drag = self.sliders[3].value

        origin = (self.width * 0.08, self.height * 0.75)

        pygame.draw.line(surface, theme.WOOD, (0, origin[1]), (self.width, origin[1]), 1)

        if len(self.trajectory) >= 2:
            points = [
                (origin[0] + px * PX_PER_METER, origin[1] - py * PX_PER_METER)
                for px, py in self.trajectory
            ]
            pygame.draw.lines(surface, theme.CHALK_BLUE, False, points, 2)

        # Current/final position marker.
        cur_x = origin[0] + self.x * PX_PER_METER
        cur_y = origin[1] - self.y * PX_PER_METER
        pygame.draw.circle(surface, theme.CHALK_GOLD, (int(cur_x), int(cur_y)), 6)

        if self.landed and self.landed_x is not None:
            land_x = origin[0] + self.landed_x * PX_PER_METER
            land_y = origin[1]
            size = 7
            pygame.draw.line(
                surface, theme.CHALK_CORAL,
                (land_x - size, land_y - size), (land_x + size, land_y + size), 2,
            )
            pygame.draw.line(
                surface, theme.CHALK_CORAL,
                (land_x - size, land_y + size), (land_x + size, land_y - size), 2,
            )

        self.draw_panel_backing(surface)

        r_analytic = v0 ** 2 * math.sin(2 * math.radians(angle_deg)) / g
        hud_lines = [
            f"R_analytic (no drag) = v0^2 sin(2*th)/g = {r_analytic:6.2f} m",
        ]
        if self.landed and self.landed_x is not None:
            hud_lines.append(f"R_actual (simulated landing)   = {self.landed_x:6.2f} m")
        else:
            hud_lines.append("R_actual: (in flight...)")
        hud_lines.append(f"t = {self.t:5.2f} s   drag = {drag:.3f}")
        draw_hud(surface, self.font, hud_lines, (self.width * 0.4, self.height * 0.15))
