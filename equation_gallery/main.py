"""Equation Gallery -- a menu-driven pygame app collecting 10 interactive
math/physics demos, each built on a real equation.

Controls:
  Menu:   number keys (1-5 = math, 6-9,0 = physics), or click a row
  Scene:  R resets the scene, Esc returns to the menu
  Esc at the menu, or closing the window, quits.
"""
from __future__ import annotations

import pygame

from .scenes.double_pendulum import DoublePendulumScene
from .scenes.euler_identity import EulerIdentityScene
from .scenes.fourier_epicycles import FourierEpicyclesScene
from .scenes.golden_spiral import GoldenSpiralScene
from .scenes.lissajous import LissajousScene
from .scenes.mandelbrot import MandelbrotScene
from .scenes.orbital_mechanics import OrbitalMechanicsScene
from .scenes.projectile_motion import ProjectileMotionScene
from .scenes.simple_pendulum import SimplePendulumScene
from .scenes.spring_mass import SpringMassScene

WIDTH, HEIGHT = 1000, 750
FPS = 60
BACKGROUND = (10, 10, 12)
HEADER_HEIGHT = 50

ALL_SCENES = [
    EulerIdentityScene,
    GoldenSpiralScene,
    LissajousScene,
    FourierEpicyclesScene,
    MandelbrotScene,
    SimplePendulumScene,
    SpringMassScene,
    ProjectileMotionScene,
    DoublePendulumScene,
    OrbitalMechanicsScene,
]

KEY_LABELS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
KEY_CODES = [
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
]


def build_menu_entries():
    math_scenes = [c for c in ALL_SCENES if c.category == "math"]
    physics_scenes = [c for c in ALL_SCENES if c.category == "physics"]
    entries = []
    for i, cls in enumerate(math_scenes):
        entries.append((KEY_LABELS[i], KEY_CODES[i], cls))
    for i, cls in enumerate(physics_scenes):
        entries.append((KEY_LABELS[5 + i], KEY_CODES[5 + i], cls))
    return entries


def draw_menu(surface, title_font, font, entries):
    title = title_font.render("Equation Gallery", True, (255, 255, 255))
    surface.blit(title, (30, 30))
    subtitle = font.render("pick a demo -- number key or click", True, (150, 220, 255))
    surface.blit(subtitle, (30, 70))

    row_rects = []
    columns = [
        ("MATH", 30, [e for e in entries if e[2].category == "math"]),
        ("PHYSICS", WIDTH // 2 + 20, [e for e in entries if e[2].category == "physics"]),
    ]
    for header, x, col_entries in columns:
        y = 120
        header_surface = font.render(header, True, (255, 220, 90))
        surface.blit(header_surface, (x, y))
        y += 36
        for label, _code, cls in col_entries:
            row_rect = pygame.Rect(x, y, WIDTH // 2 - 60, 34)
            hovered = row_rect.collidepoint(pygame.mouse.get_pos())
            bg_color = (35, 35, 42) if hovered else (22, 22, 27)
            pygame.draw.rect(surface, bg_color, row_rect, border_radius=6)
            row_text = font.render(f"[{label}]  {cls.title}", True, (230, 230, 230))
            surface.blit(row_text, (row_rect.x + 12, row_rect.y + 8))
            row_rects.append((row_rect, cls))
            y += 42
    return row_rects


def draw_header(surface, font, scene):
    bar = pygame.Surface((WIDTH, HEADER_HEIGHT))
    bar.set_alpha(230)
    bar.fill((20, 20, 24))
    surface.blit(bar, (0, 0))
    title_text = font.render(f"{scene.title}    {scene.formula}", True, (255, 255, 255))
    surface.blit(title_text, (20, 15))
    hint_text = font.render("[R] reset   [Esc] menu", True, (150, 220, 255))
    surface.blit(hint_text, (WIDTH - 220, 15))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Equation Gallery")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("menlo,consolas,monospace", 16)
    title_font = pygame.font.SysFont("menlo,consolas,monospace", 28, bold=True)

    menu_entries = build_menu_entries()
    menu_row_rects: list = []
    active_scene = None

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if active_scene is None:
                    running = False
                else:
                    active_scene = None
            elif event.type == pygame.KEYDOWN and active_scene is not None and event.key == pygame.K_r:
                active_scene.reset()
            elif event.type == pygame.KEYDOWN and active_scene is None:
                for label, code, cls in menu_entries:
                    if event.key == code:
                        active_scene = cls(WIDTH, HEIGHT)
                        break
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and active_scene is None
            ):
                for rect, cls in menu_row_rects:
                    if rect.collidepoint(event.pos):
                        active_scene = cls(WIDTH, HEIGHT)
                        break

            if active_scene is not None:
                active_scene.handle_event(event)

        screen.fill(BACKGROUND)
        if active_scene is None:
            menu_row_rects = draw_menu(screen, title_font, font, menu_entries)
        else:
            active_scene.update(dt)
            active_scene.draw(screen)
            draw_header(screen, font, active_scene)
            active_scene.draw_sliders(screen, font)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
