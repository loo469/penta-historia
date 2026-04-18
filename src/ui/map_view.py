from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.adapters.persistence.in_memory_war import InMemoryMapRepository
from src.core.types import WorldState
from src.domain.war import build_faction_territories, detect_fronts

if TYPE_CHECKING:
    import pygame


TILE = 28


def build_war_overlay(world: WorldState) -> tuple[set[tuple[int, int]], set[tuple[tuple[int, int], tuple[int, int]]]]:
    provinces = InMemoryMapRepository(world).list_provinces()
    territories = build_faction_territories(provinces)
    fronts = detect_fronts(provinces, territories)

    contested = {province.coord for province in provinces if province.contested}
    borders: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for front in fronts:
        for segment in front.segments:
            borders.add(tuple(sorted((segment.from_coord, segment.to_coord))))
    return contested, borders


def _draw_front_segment(screen: Any, from_coord: tuple[int, int], to_coord: tuple[int, int]) -> None:
    import pygame

    x1, y1 = from_coord
    x2, y2 = to_coord
    if x1 != x2:
        x = max(x1, x2) * TILE
        y = min(y1, y2) * TILE
        start = (x, y + 4)
        end = (x, y + TILE - 4)
    else:
        x = min(x1, x2) * TILE
        y = max(y1, y2) * TILE
        start = (x + 4, y)
        end = (x + TILE - 4, y)

    pygame.draw.line(screen, (255, 170, 90), start, end, 3)
    pygame.draw.line(screen, (255, 240, 200), start, end, 1)


def draw_map(screen: Any, world: WorldState) -> None:
    import pygame

    contested, front_borders = build_war_overlay(world)

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
                if (x, y) in contested:
                    pygame.draw.rect(screen, (255, 226, 120), rect.inflate(-6, -6), 2)

    for from_coord, to_coord in front_borders:
        _draw_front_segment(screen, from_coord, to_coord)

    for city in world.cities:
        cx = city.x * TILE + TILE // 2
        cy = city.y * TILE + TILE // 2
        pygame.draw.circle(screen, (245, 245, 245), (cx, cy), 5)

