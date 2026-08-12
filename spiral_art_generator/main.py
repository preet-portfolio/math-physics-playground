"""Spiral Art Generator.

A Python/pygame recreation of David Panik's CodePen "Spiral Art Generator"
(https://codepen.io/davidpanik/pen/myMrLx), built on real rotational
kinematics: N chords through a center point rotate at a constant angular
velocity with a fixed phase offset between adjacent lines, and a fading
trail turns that rotation into visible spiral / moire patterns.

Controls:
  - Drag sliders: number of lines, line width, speed (omega), rotation (delta-phi)
  - R:   reset all sliders to defaults
  - Esc: quit (or just close the window)
"""
from __future__ import annotations

import pygame

from common.ui import Slider, draw_hud

from .spiral import (
    DEFAULT_LINE_WIDTH,
    DEFAULT_NUM_LINES,
    DEFAULT_ROTATION_DEG,
    DEFAULT_SPEED,
    LINE_WIDTH_RANGE,
    NUM_LINES_RANGE,
    ROTATION_RANGE_DEG,
    SPEED_RANGE,
    SpiralField,
)

WIDTH, HEIGHT = 900, 700
FPS = 60
BACKGROUND = (10, 10, 12)
LINE_COLOR = (255, 255, 255)
PANEL_HEIGHT = 220
TRAIL_ALPHA = 25  # lower = longer-lived trails (closer to 0 = never fades)


def make_sliders() -> dict[str, Slider]:
    x, width = 30, 260
    return {
        "num_lines": Slider(x, 50, width, *NUM_LINES_RANGE, DEFAULT_NUM_LINES, "Lines (N)", fmt="{:.0f}"),
        "line_width": Slider(x, 100, width, *LINE_WIDTH_RANGE, DEFAULT_LINE_WIDTH, "Width", fmt="{:.0f}"),
        "speed": Slider(x, 150, width, *SPEED_RANGE, DEFAULT_SPEED, "Speed  omega (rad/s)", fmt="{:.2f}"),
        "rotation": Slider(x, 200, width, *ROTATION_RANGE_DEG, DEFAULT_ROTATION_DEG, "Rotation  delta-phi (deg)", fmt="{:.1f}"),
    }


def reset_sliders(sliders: dict[str, Slider]) -> None:
    sliders["num_lines"].reset(DEFAULT_NUM_LINES)
    sliders["line_width"].reset(DEFAULT_LINE_WIDTH)
    sliders["speed"].reset(DEFAULT_SPEED)
    sliders["rotation"].reset(DEFAULT_ROTATION_DEG)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spiral Art Generator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("menlo,consolas,monospace", 16)

    field = SpiralField()
    sliders = make_sliders()

    fade_overlay = pygame.Surface((WIDTH, HEIGHT))
    fade_overlay.fill(BACKGROUND)
    fade_overlay.set_alpha(TRAIL_ALPHA)

    trail = pygame.Surface((WIDTH, HEIGHT))
    trail.fill(BACKGROUND)

    center = (WIDTH / 2, PANEL_HEIGHT + (HEIGHT - PANEL_HEIGHT) / 2)
    radius = max(WIDTH, HEIGHT)  # longer than the screen diagonal; clipped by the surface

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    reset_sliders(sliders)
            for slider in sliders.values():
                slider.handle_event(event)

        field.num_lines = int(sliders["num_lines"].value)
        field.line_width = int(sliders["line_width"].value)
        field.speed = sliders["speed"].value
        field.rotation_deg = sliders["rotation"].value
        field.update(dt)

        trail.blit(fade_overlay, (0, 0))
        field.draw(trail, center, radius, LINE_COLOR)
        screen.blit(trail, (0, 0))

        panel = pygame.Surface((WIDTH, PANEL_HEIGHT))
        panel.set_alpha(235)
        panel.fill((20, 20, 24))
        screen.blit(panel, (0, 0))

        for slider in sliders.values():
            slider.draw(screen, font)

        hud_lines = [
            f"omega  = {field.speed:6.2f} rad/s  ({field.speed_deg:6.1f} deg/s)",
            f"delta-phi = {field.rotation_deg:6.1f} deg   (360/N = {360.0 / field.num_lines:.1f} deg)",
            f"theta0(t) mod 360 = {field.theta0_deg:6.1f} deg",
            "",
            "[R] reset to defaults    [Esc] quit",
        ]
        draw_hud(screen, font, hud_lines, (330, 50))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
