from __future__ import annotations

import random

from src.core.types import WorldState


def tick_climate(world: WorldState) -> None:
    world.climate.season_index = (world.climate.season_index + 1) % 4
    if world.climate.season_index == 0:
        world.climate.year += 1

    if world.climate.season_name == "Hiver":
        world.climate.fertility_modifier = 0.8
    elif world.climate.season_name == "Été":
        world.climate.fertility_modifier = 1.15
    else:
        world.climate.fertility_modifier = 1.0

    world.climate.anomaly = random.choice(["stable", "stable", "dry", "storm"])
    if world.climate.anomaly == "dry":
        world.climate.fertility_modifier *= 0.9
    elif world.climate.anomaly == "storm":
        world.climate.fertility_modifier *= 0.95

