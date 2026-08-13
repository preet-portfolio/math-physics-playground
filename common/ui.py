"""Reusable interactive widgets: a draggable slider and a HUD text block.

Generic (no scene-specific knowledge) so every project in this repo can
reuse them as-is. Styled from common.theme (Chalkboard Lecture Hall).
"""
from __future__ import annotations

import pygame

from . import theme

GROOVE_COLOR = (132, 138, 129)  # CHALK worn down toward BOARD -- a muted sage line
TICK_COUNT = 5  # includes both ends


class Slider:
    def __init__(self, x, y, width, min_value, max_value, value, label, fmt="{:.1f}"):
        self.rect = pygame.Rect(x, y, width, 4)
        self.handle_radius = 8
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.label = label
        self.fmt = fmt
        self.dragging = False

    def reset(self, value) -> None:
        self.value = value

    def _handle_x(self) -> float:
        t = (self.value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.x + t * self.rect.width

    def _set_from_pixel_x(self, pixel_x: float) -> bool:
        t = (pixel_x - self.rect.x) / self.rect.width
        t = max(0.0, min(1.0, t))
        new_value = self.min_value + t * (self.max_value - self.min_value)
        if new_value != self.value:
            self.value = new_value
            return True
        return False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hit_rect = self.rect.inflate(0, self.handle_radius * 2)
            if hit_rect.collidepoint(event.pos):
                self.dragging = True
                return self._set_from_pixel_x(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            return self._set_from_pixel_x(event.pos[0])
        return False

    def draw(self, surface, font=None) -> None:
        # `font` is accepted-but-unused for backward compatibility with
        # callers (e.g. spiral_art_generator) written before this widget
        # switched to sourcing its own fonts from common.theme.
        # Groove with tick marks, like a chalk-drawn ruler.
        pygame.draw.line(surface, GROOVE_COLOR, (self.rect.x, self.rect.centery),
                          (self.rect.right, self.rect.centery), 2)
        for i in range(TICK_COUNT):
            tick_x = self.rect.x + self.rect.width * i / (TICK_COUNT - 1)
            pygame.draw.line(surface, GROOVE_COLOR, (tick_x, self.rect.centery - 4),
                              (tick_x, self.rect.centery + 4), 1)

        handle_x = int(self._handle_x())
        handle_y = self.rect.centery
        if self.dragging:
            pygame.draw.circle(surface, theme.CHALK_GOLD, (handle_x, handle_y), self.handle_radius)
        else:
            pygame.draw.circle(surface, theme.CHALK, (handle_x, handle_y), self.handle_radius, 2)

        caption_font = theme.chalk_font(13)
        value_font = theme.mono_font(14, bold=True)
        caption = caption_font.render(f"{self.label}", True, theme.CHALK)
        value_text = value_font.render(f" {self.fmt.format(self.value)}", True, theme.CHALK_GOLD)
        surface.blit(caption, (self.rect.x, self.rect.y - 22))
        surface.blit(value_text, (self.rect.x + caption.get_width(), self.rect.y - 21))


def draw_hud(surface, font, lines, pos, color=None) -> None:
    if color is None:
        color = theme.CHALK_BLUE
    x, y = pos
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y))
        y += text_surface.get_height() + 4
