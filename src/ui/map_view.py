from __future__ import annotations

import pygame

from src.core.types import WorldState


TILE = 28


def draw_map(screen: pygame.Surface, world: WorldState) -> None:
    for y in range(world.height):
        for x in range(world.width):
            owner = world.owners[y][x]
            rect = pygame.Rect(x * TILE, y * TILE, TILE - 1, TILE - 1)
            if owner is None:
                pygame.draw.rect(screen, (28, 42, 80), rect)
            else:
                color = world.civilizations[owner].color
                fertility = world.fertility[y][x]
                boosted = tuple(min(255, int(channel * fertility * 0.9)) for channel in color)
                pygame.draw.rect(screen, boosted, rect)

    for city in world.cities:
        cx = city.x * TILE + TILE // 2
        cy = city.y * TILE + TILE // 2
        pygame.draw.circle(screen, (245, 245, 245), (cx, cy), 5)

