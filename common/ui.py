"""Reusable interactive widgets: a draggable slider and a HUD text block.

Generic (no scene-specific knowledge) so every project in this repo can
reuse them as-is.
"""
from __future__ import annotations

import pygame


class Slider:
    def __init__(self, x, y, width, min_value, max_value, value, label, fmt="{:.1f}"):
        self.rect = pygame.Rect(x, y, width, 6)
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

    def draw(self, surface, font, color=(230, 230, 230), track_color=(90, 90, 90)) -> None:
        pygame.draw.rect(surface, track_color, self.rect, border_radius=3)
        handle_x = self._handle_x()
        pygame.draw.circle(surface, color, (int(handle_x), self.rect.centery), self.handle_radius)
        text = f"{self.label}: {self.fmt.format(self.value)}"
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (self.rect.x, self.rect.y - 20))


def draw_hud(surface, font, lines, pos, color=(150, 220, 255)) -> None:
    x, y = pos
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y))
        y += text_surface.get_height() + 4
