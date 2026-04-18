from __future__ import annotations

from src.core.types import WorldState



def tick_economy(world: WorldState) -> None:
    for city in world.cities:
        civ = world.civilizations[city.civ_id]
        tile_fertility = world.fertility[city.y][city.x]
        sabotage_pressure = world.intrigue.sabotage_pressure.get(city.civ_id, 0.0)
        pressure_penalty = max(0.45, 1.0 - sabotage_pressure * 0.18)
        growth = 0.05 * tile_fertility * world.climate.fertility_modifier * pressure_penalty
        city.population += growth
        city.storage += 0.2 * tile_fertility * pressure_penalty
        civ.food += 0.15 * tile_fertility * pressure_penalty
        civ.industry += (0.08 + city.population * 0.005) * pressure_penalty
        if sabotage_pressure > 0.0:
            civ.stability = max(0.0, min(20.0, civ.stability + 0.01 - sabotage_pressure * 0.04))
        else:
            civ.stability = max(0.0, min(20.0, civ.stability + 0.01))

    world.intrigue.decay_pressures()
