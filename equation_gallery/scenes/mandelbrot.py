"""The Mandelbrot set: z = z^2 + c, iterated per pixel, escape-time coloring.

Rendering the whole window per-pixel in pure Python is far too slow to feel
interactive, so the escape-time computation is vectorized with numpy
(compute_mandelbrot) and only re-run when the view actually changes (pan via
click-to-recenter, or the max_iter/zoom sliders) -- see the cache in draw().
"""
from __future__ import annotations

import numpy as np
import pygame

from common.scene import Scene
from common.ui import Slider, draw_hud

MAX_ITER_RANGE = (20, 300)
DEFAULT_MAX_ITER = 80
ZOOM_RANGE = (1, 200)
DEFAULT_ZOOM = 1
BASE_SPAN = 1.6  # half-width of the view at zoom = 1
DEFAULT_CX = -0.5
DEFAULT_CY = 0.0
RENDER_SCALE = 0.5  # compute at half resolution, then scale up, for speed


def compute_mandelbrot(width_px, height_px, cx, cy, span, max_iter):
    span_y = span * height_px / width_px
    x = np.linspace(cx - span, cx + span, width_px)
    y = np.linspace(cy - span_y, cy + span_y, height_px)
    X, Y = np.meshgrid(x, y)  # shape (height_px, width_px)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    iterations = np.zeros(C.shape, dtype=np.int32)
    mask = np.ones(C.shape, dtype=bool)
    for i in range(max_iter):
        Z[mask] = Z[mask] * Z[mask] + C[mask]
        escaped = (np.abs(Z) > 2) & mask
        iterations[escaped] = i
        mask &= ~escaped
        if not mask.any():
            break
    iterations[mask] = max_iter
    return iterations  # shape (height_px, width_px), int array


def _colorize(iterations, max_iter):
    inside = iterations >= max_iter
    t = iterations / max_iter
    r = (np.sin(t * 6.0 + 0.0) * 0.5 + 0.5) * 255
    g = (np.sin(t * 6.0 + 2.0) * 0.5 + 0.5) * 255
    b = (np.sin(t * 6.0 + 4.0) * 0.5 + 0.5) * 255
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    rgb[inside] = [5, 5, 10]
    return rgb


class MandelbrotScene(Scene):
    title = "Mandelbrot Set"
    category = "math"
    formula = "z = z^2 + c"

    def reset(self) -> None:
        self.cx = DEFAULT_CX
        self.cy = DEFAULT_CY
        self.font = pygame.font.SysFont("menlo,consolas,monospace", 16)
        self.sliders = [
            Slider(20, 65, 230, *MAX_ITER_RANGE, DEFAULT_MAX_ITER, "Detail  max_iter", fmt="{:.0f}"),
            Slider(20, 107, 230, *ZOOM_RANGE, DEFAULT_ZOOM, "Zoom", fmt="{:.0f}"),
        ]
        self._cache_key = None
        self._cache_surface = None

    def handle_event(self, event: "pygame.event.Event") -> None:
        for slider in self.sliders:
            slider.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.pos[1] > 160:
            zoom = self.sliders[1].value
            span = BASE_SPAN / zoom
            new_cx = self.cx + (event.pos[0] / self.width - 0.5) * 2 * span
            new_cy = self.cy + (event.pos[1] / self.height - 0.5) * 2 * span * (self.height / self.width)
            self.cx = new_cx
            self.cy = new_cy

    def update(self, dt: float) -> None:
        pass

    @property
    def max_iter(self) -> int:
        return int(round(self.sliders[0].value))

    @property
    def span(self) -> float:
        zoom = self.sliders[1].value
        return BASE_SPAN / zoom

    def draw(self, surface: "pygame.Surface") -> None:
        max_iter = self.max_iter
        span = self.span
        key = (self.cx, self.cy, span, max_iter)
        dragging = any(s.dragging for s in self.sliders)

        if key != self._cache_key and not dragging:
            render_w = max(1, int(self.width * RENDER_SCALE))
            render_h = max(1, int(self.height * RENDER_SCALE))
            iterations = compute_mandelbrot(render_w, render_h, self.cx, self.cy, span, max_iter)
            rgb = _colorize(iterations, max_iter)
            small_surface = pygame.surfarray.make_surface(rgb.transpose(1, 0, 2))
            self._cache_surface = pygame.transform.scale(small_surface, (self.width, self.height))
            self._cache_key = key

        if self._cache_surface is not None:
            surface.blit(self._cache_surface, (0, 0))

        hud_lines = [
            f"center = ({self.cx:+.5f}, {self.cy:+.5f})",
            f"span = {span:.5f}   max_iter = {max_iter}",
            "click the fractal to recenter",
        ]
        draw_hud(surface, self.font, hud_lines, (self.width * 0.55, 60))
