from __future__ import annotations

from src.core.types import WorldState


def tick_economy(world: WorldState) -> None:
    for city in world.cities:
        civ = world.civilizations[city.civ_id]
        tile_fertility = world.fertility[city.y][city.x]
        growth = 0.05 * tile_fertility * world.climate.fertility_modifier
        city.population += growth
        city.storage += 0.2 * tile_fertility
        civ.food += 0.15 * tile_fertility
        civ.industry += 0.08 + city.population * 0.005
        civ.stability = max(0.0, min(20.0, civ.stability + 0.01))

