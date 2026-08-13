"""Equation Gallery -- a menu-driven pygame app collecting 10 interactive
math/physics demos, each built on a real equation.

Visual theme: Chalkboard Lecture Hall (see common/theme.py). A wooden-ledge
sidebar on the left lists all 10 demos; the rest of the window is a chalk
board where each demo opens with its formula handwritten across the top.

Layout: the sidebar is 240px; the remaining 1000x750 is a content area --
exactly the dimensions every scene in scenes/ is built and tested against --
reached via a pygame subsurface, so scene code never has to know a sidebar
exists.

Controls:
  Sidebar:  click a row, or press 1-5 (math) / 6-9,0 (physics), to switch
            demos instantly. Scene instances are cached, so switching back
            to a demo you've already visited resumes exactly where it was.
  In a scene:  drag the sliders to change parameters live -- the handle
               fills solid gold while held. R resets the current scene.
  Esc, or closing the window, quits.
"""
from __future__ import annotations

import pygame

from common import theme

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

SIDEBAR_WIDTH = 240
CONTENT_WIDTH, CONTENT_HEIGHT = 1000, 750
WIDTH = SIDEBAR_WIDTH + CONTENT_WIDTH
HEIGHT = CONTENT_HEIGHT
FPS = 60
HEADER_HEIGHT = 100  # room for the big handwritten formula + title caption

ROW_HEIGHT = 38
ROW_GAP = 6

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

CATEGORY_COLOR = {"math": theme.CHALK_GOLD, "physics": theme.CHALK_BLUE}


def build_menu_entries():
    math_scenes = [c for c in ALL_SCENES if c.category == "math"]
    physics_scenes = [c for c in ALL_SCENES if c.category == "physics"]
    entries = []
    for i, cls in enumerate(math_scenes):
        entries.append((KEY_LABELS[i], KEY_CODES[i], cls))
    for i, cls in enumerate(physics_scenes):
        entries.append((KEY_LABELS[5 + i], KEY_CODES[5 + i], cls))
    return entries


def draw_sidebar(surface, entries, active_cls):
    surface.fill(theme.BOARD_DARK)
    pygame.draw.line(surface, theme.WOOD, (SIDEBAR_WIDTH - 1, 0), (SIDEBAR_WIDTH - 1, HEIGHT), 3)

    title_font = theme.chalk_font(24, bold=True)
    surface.blit(title_font.render("Equation", True, theme.CHALK), (20, 22))
    surface.blit(title_font.render("Gallery", True, theme.CHALK), (20, 50))

    label_font = theme.chalk_font(14)
    header_font = theme.chalk_font(15, bold=True)
    mouse_pos = pygame.mouse.get_pos()

    row_rects = []  # (rect, scene_class), window-absolute (sidebar is at x offset 0)
    columns = [
        ("MATH", [e for e in entries if e[2].category == "math"]),
        ("PHYSICS", [e for e in entries if e[2].category == "physics"]),
    ]
    y = 104
    for header, col_entries in columns:
        accent = CATEGORY_COLOR[col_entries[0][2].category] if col_entries else theme.CHALK
        header_surface = header_font.render(header, True, accent)
        surface.blit(header_surface, (20, y))
        y += 28
        for label, _code, cls in col_entries:
            row_rect = pygame.Rect(14, y, SIDEBAR_WIDTH - 28, ROW_HEIGHT)
            is_active = cls is active_cls
            hovered = row_rect.collidepoint(mouse_pos)

            if is_active:
                fill = pygame.Surface(row_rect.size, pygame.SRCALPHA)
                fill.fill((*accent, 35))
                surface.blit(fill, row_rect.topleft)
                pygame.draw.rect(surface, accent, row_rect, width=2, border_radius=4)
            elif hovered:
                pygame.draw.rect(surface, theme.WOOD, row_rect, width=1, border_radius=4)
            else:
                pygame.draw.rect(surface, theme.WOOD, row_rect, width=1, border_radius=4)

            bullet_center = (row_rect.x + 16, row_rect.centery)
            if is_active:
                pygame.draw.circle(surface, accent, bullet_center, 5)
            else:
                pygame.draw.circle(surface, theme.CHALK, bullet_center, 5, 1)

            row_text = label_font.render(f"[{label}] {cls.title}", True, theme.CHALK)
            surface.blit(row_text, (row_rect.x + 30, row_rect.centery - row_text.get_height() // 2))

            row_rects.append((row_rect, cls))
            y += ROW_HEIGHT + ROW_GAP
        y += 14

    hint_font = theme.chalk_font(13)
    dim = tuple(int(c * 0.6) for c in theme.CHALK)
    surface.blit(hint_font.render("R: reset demo", True, dim), (20, HEIGHT - 58))
    surface.blit(hint_font.render("Esc: quit", True, dim), (20, HEIGHT - 34))

    return row_rects


def draw_header(surface, scene):
    # A raised "placard" for the formula, opaque enough to stay legible over
    # busy scene content (Mandelbrot fills the whole canvas, for instance).
    backing = pygame.Surface((CONTENT_WIDTH, HEADER_HEIGHT), pygame.SRCALPHA)
    backing.fill((*theme.BOARD_DARK, 215))
    surface.blit(backing, (0, 0))

    formula_font, formula_surface = theme.fit_display_text(
        scene.formula, max_width=CONTENT_WIDTH - 40, max_size=34, min_size=18,
    )
    surface.blit(formula_surface, (30, 14))

    caption_font = theme.chalk_font(15)
    accent = CATEGORY_COLOR[scene.category]
    caption = caption_font.render(scene.title.upper(), True, accent)
    surface.blit(caption, (30, 14 + formula_surface.get_height() + 6))

    pygame.draw.line(surface, theme.WOOD, (30, HEADER_HEIGHT - 8),
                      (CONTENT_WIDTH - 30, HEADER_HEIGHT - 8), 1)


def translate_event(event, dx, dy):
    """Return a copy of a mouse event with `.pos` shifted by (-dx, -dy), so
    scenes (which only ever see their own 1000x750 content area) get
    content-local coordinates instead of window-absolute ones."""
    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
        new_dict = dict(event.dict)
        x, y = new_dict["pos"]
        new_dict["pos"] = (x - dx, y - dy)
        return pygame.event.Event(event.type, new_dict)
    return event


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Equation Gallery")
    clock = pygame.time.Clock()

    sidebar_surface = screen.subsurface((0, 0, SIDEBAR_WIDTH, HEIGHT))
    content_surface = screen.subsurface((SIDEBAR_WIDTH, 0, CONTENT_WIDTH, CONTENT_HEIGHT))
    dust = theme.chalk_texture(CONTENT_WIDTH, CONTENT_HEIGHT)

    menu_entries = build_menu_entries()
    scene_cache: dict = {}

    def get_scene(cls):
        if cls not in scene_cache:
            scene_cache[cls] = cls(CONTENT_WIDTH, CONTENT_HEIGHT)
        return scene_cache[cls]

    active_scene = get_scene(ALL_SCENES[0])
    sidebar_row_rects: list = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                active_scene.reset()
            elif event.type == pygame.KEYDOWN:
                for label, code, cls in menu_entries:
                    if event.key == code:
                        active_scene = get_scene(cls)
                        break
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if event.pos[0] < SIDEBAR_WIDTH:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for rect, cls in sidebar_row_rects:
                            if rect.collidepoint(event.pos):
                                active_scene = get_scene(cls)
                                break
                else:
                    translated = translate_event(event, SIDEBAR_WIDTH, 0)
                    active_scene.handle_event(translated)

        content_surface.fill(theme.BOARD)
        content_surface.blit(dust, (0, 0))
        active_scene.update(dt)
        active_scene.draw(content_surface)
        draw_header(content_surface, active_scene)
        active_scene.draw_sliders(content_surface)

        sidebar_row_rects = draw_sidebar(sidebar_surface, menu_entries, type(active_scene))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
