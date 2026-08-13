"""Double pendulum: the classic demonstration of deterministic chaos.

Two double pendulums (point masses m1, m2 on massless rigid rods of length
L1, L2) share the same pivot and start at nearly identical angles, differing
only by a tiny slider-controlled offset in pendulum B's initial theta1. The
exact nonlinear Lagrangian equations of motion (standard textbook form, not
re-derived here) are:

    denom      = L1 * (2*m1 + m2 - m2*cos(2*theta1 - 2*theta2))
    theta1'' = (
        -g*(2*m1+m2)*sin(theta1)
        - m2*g*sin(theta1 - 2*theta2)
        - 2*sin(theta1-theta2)*m2*(omega2**2*L2 + omega1**2*L1*cos(theta1-theta2))
    ) / denom

    denom2     = L2 * (2*m1 + m2 - m2*cos(2*theta1 - 2*theta2))   (same expr as
                                                                    denom, just
                                                                    divided by L2)
    theta2'' = (
        2*sin(theta1-theta2) * (
            omega1**2*L1*(m1+m2)
            + g*(m1+m2)*cos(theta1)
            + omega2**2*L2*m2*cos(theta1-theta2)
        )
    ) / denom2

Integrated with classic 4th-order Runge-Kutta (RK4), not Euler -- plain
Euler visibly gains energy on this stiff, chaotic system and the pendulum
flies apart within a few seconds. RK4 with several substeps per rendered
frame keeps total mechanical energy (KE + PE) very nearly constant, so the
two pendulums' trajectories separate only because of the system's genuine
sensitivity to initial conditions (chaos), not integration error.
"""
from __future__ import annotations

import math

import pygame

from common import theme
from common.scene import Scene
from common.ui import Slider, draw_hud

# Fixed (non-slider) physical parameters -- abstract units, scaled to pixels
# separately for drawing.
M1 = 1.0
M2 = 1.0
L1 = 1.2
L2 = 1.2
PX_PER_LENGTH = 150.0  # pixels per unit of rod length

G_RANGE = (2.0, 20.0)
DEFAULT_G = 9.81
DELTA_THETA0_RANGE = (0.0001, 0.1)
DEFAULT_DELTA_THETA0 = 0.01
TIME_SCALE_RANGE = (0.1, 1.0)
DEFAULT_TIME_SCALE = 0.4

SUBSTEPS = 6  # RK4 substeps per rendered frame
TRAIL_FADE_ALPHA = 6  # alpha subtracted from the trail surface each frame

THETA1_0 = math.radians(120.0)
THETA2_0 = math.radians(-10.0)

COLOR_A = theme.CHALK_BLUE
COLOR_B = theme.CHALK_CORAL


def derivatives(state, g):
    """State = (theta1, theta2, omega1, omega2) -> its time derivative."""
    theta1, theta2, omega1, omega2 = state
    delta = theta1 - theta2

    denom = L1 * (2 * M1 + M2 - M2 * math.cos(2 * theta1 - 2 * theta2))
    theta1_dd = (
        -g * (2 * M1 + M2) * math.sin(theta1)
        - M2 * g * math.sin(theta1 - 2 * theta2)
        - 2 * math.sin(delta) * M2 * (omega2 ** 2 * L2 + omega1 ** 2 * L1 * math.cos(delta))
    ) / denom

    denom2 = L2 * (2 * M1 + M2 - M2 * math.cos(2 * theta1 - 2 * theta2))
    theta2_dd = (
        2 * math.sin(delta) * (
            omega1 ** 2 * L1 * (M1 + M2)
            + g * (M1 + M2) * math.cos(theta1)
            + omega2 ** 2 * L2 * M2 * math.cos(delta)
        )
    ) / denom2

    return (omega1, omega2, theta1_dd, theta2_dd)


def add_scaled(state, deriv, factor):
    return tuple(s + d * factor for s, d in zip(state, deriv))


def rk4_step(state, g, dt):
    k1 = derivatives(state, g)
    k2 = derivatives(add_scaled(state, k1, dt / 2), g)
    k3 = derivatives(add_scaled(state, k2, dt / 2), g)
    k4 = derivatives(add_scaled(state, k3, dt), g)
    return tuple(
        s + (dt / 6.0) * (a + 2 * b + 2 * c + d)
        for s, a, b, c, d in zip(state, k1, k2, k3, k4)
    )


def mechanical_energy(state, g):
    """KE + PE for one pendulum's state, using the fixed M1/M2/L1/L2 above."""
    theta1, theta2, omega1, omega2 = state
    ke = 0.5 * M1 * (L1 * omega1) ** 2 + 0.5 * M2 * (
        (L1 * omega1) ** 2 + (L2 * omega2) ** 2
        + 2 * L1 * L2 * omega1 * omega2 * math.cos(theta1 - theta2)
    )
    pe = -(M1 + M2) * g * L1 * math.cos(theta1) - M2 * g * L2 * math.cos(theta2)
    return ke + pe


class DoublePendulumScene(Scene):
    title = "Double Pendulum"
    category = "physics"
    formula = "double pendulum (Lagrangian, chaotic)"

    def reset(self) -> None:
        self.font = theme.mono_font(16)
        if not self.sliders:
            self.sliders = [
                Slider(20, 115, 230, *G_RANGE, DEFAULT_G, "g  gravity (m/s^2)", fmt="{:.2f}"),
                Slider(20, 157, 230, *DELTA_THETA0_RANGE, DEFAULT_DELTA_THETA0, "delta_theta0 (rad)", fmt="{:.4f}"),
                Slider(20, 199, 230, *TIME_SCALE_RANGE, DEFAULT_TIME_SCALE, "time_scale", fmt="{:.2f}"),
            ]

        delta0 = self.sliders[1].value
        self.state_a = (THETA1_0, THETA2_0, 0.0, 0.0)
        self.state_b = (THETA1_0 + delta0, THETA2_0, 0.0, 0.0)
        self.sim_time = 0.0

        self.trail = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.prev_bob2_a = None
        self.prev_bob2_b = None

    def _bob_positions(self, state, pivot):
        theta1, theta2, _, _ = state
        l1_px = L1 * PX_PER_LENGTH
        l2_px = L2 * PX_PER_LENGTH
        bob1 = (pivot[0] + l1_px * math.sin(theta1), pivot[1] + l1_px * math.cos(theta1))
        bob2 = (bob1[0] + l2_px * math.sin(theta2), bob1[1] + l2_px * math.cos(theta2))
        return bob1, bob2

    def update(self, dt: float) -> None:
        g = self.sliders[0].value
        time_scale = self.sliders[2].value

        dt_sub = (dt * time_scale) / SUBSTEPS
        for _ in range(SUBSTEPS):
            self.state_a = rk4_step(self.state_a, g, dt_sub)
            self.state_b = rk4_step(self.state_b, g, dt_sub)
        self.sim_time += dt * time_scale

    def draw(self, surface: "pygame.Surface") -> None:
        pivot = (self.width * 0.62, self.height * 0.30)

        bob1_a, bob2_a = self._bob_positions(self.state_a, pivot)
        bob1_b, bob2_b = self._bob_positions(self.state_b, pivot)

        # Fade the persistent trail surface toward transparent (subtracting a
        # small alpha from every pixel each frame), then draw this frame's
        # short trail segment on top -- same fading-trail technique used by
        # spiral_art_generator / lissajous, but on a per-pixel-alpha surface
        # so it can be composited over the freshly-drawn rods each frame
        # instead of owning the whole background.
        fade = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade.fill((0, 0, 0, TRAIL_FADE_ALPHA))
        self.trail.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        if self.prev_bob2_a is not None:
            pygame.draw.line(self.trail, COLOR_A, self.prev_bob2_a, bob2_a, 2)
        if self.prev_bob2_b is not None:
            pygame.draw.line(self.trail, COLOR_B, self.prev_bob2_b, bob2_b, 2)
        self.prev_bob2_a = bob2_a
        self.prev_bob2_b = bob2_b

        surface.blit(self.trail, (0, 0))

        for bob1, bob2, color in ((bob1_a, bob2_a, COLOR_A), (bob1_b, bob2_b, COLOR_B)):
            pygame.draw.line(surface, color, pivot, bob1, 2)
            pygame.draw.line(surface, color, bob1, bob2, 2)
            pygame.draw.circle(surface, color, (int(bob1[0]), int(bob1[1])), 8)
            pygame.draw.circle(surface, color, (int(bob2[0]), int(bob2[1])), 11)

        pygame.draw.circle(surface, theme.WOOD, (int(pivot[0]), int(pivot[1])), 4)
        self.draw_panel_backing(surface)

        delta0 = self.sliders[1].value
        hud_lines = [
            f"delta_theta0 = {delta0:.4f} rad ({math.degrees(delta0):.3f} deg)",
            f"t_sim = {self.sim_time:6.2f} s",
            "watch the paths diverge -- this is chaos",
        ]
        draw_hud(surface, self.font, hud_lines, (self.width * 0.55, self.height * 0.62))
