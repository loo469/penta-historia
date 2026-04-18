from __future__ import annotations

import random

from src.application.gamma_use_cases import build_default_culture, build_default_research_state
from src.core.types import City, Civilization, ClimateState, WorldState


CIV_NAMES = ["Aster", "Boreal", "Cyrene", "Doria"]
CIV_COLORS = [(220, 90, 90), (90, 170, 240), (120, 200, 120), (210, 170, 80)]


def generate_world(width: int = 28, height: int = 18, civ_count: int = 4) -> WorldState:
    owners: list[list[int | None]] = []
    fertility: list[list[float]] = []
    civilizations: dict[int, Civilization] = {}
    cities: list[City] = []

    for civ_id in range(civ_count):
        civilizations[civ_id] = Civilization(
            civ_id=civ_id,
            name=CIV_NAMES[civ_id % len(CIV_NAMES)],
            color=CIV_COLORS[civ_id % len(CIV_COLORS)],
            food=random.uniform(8, 14),
            industry=random.uniform(8, 14),
            military=random.uniform(8, 14),
            stability=random.uniform(8, 14),
        )

    seeds: list[tuple[int, int]] = []
    for civ_id in range(civ_count):
        x = random.randint(3, width - 4)
        y = random.randint(3, height - 4)
        seeds.append((x, y))
        cities.append(City(name=f"{civilizations[civ_id].name} Prime", civ_id=civ_id, x=x, y=y))

    for y in range(height):
        owner_row: list[int | None] = []
        fertility_row: list[float] = []
        for x in range(width):
            value = random.random()
            fertility_row.append(0.6 + random.random() * 0.8)
            if value < 0.08:
                owner_row.append(None)
                continue

            nearest = min(
                range(civ_count),
                key=lambda civ_id: abs(seeds[civ_id][0] - x) + abs(seeds[civ_id][1] - y),
            )
            owner_row.append(nearest)
        owners.append(owner_row)
        fertility.append(fertility_row)

    world = WorldState(
        width=width,
        height=height,
        owners=owners,
        fertility=fertility,
        civilizations=civilizations,
        cities=cities,
        climate=ClimateState(),
        cultures={civ_id: build_default_culture(civ_id) for civ_id in civilizations},
        research_states={civ_id: build_default_research_state(civ_id) for civ_id in civilizations},
    )
    world.log.append("Le monde a été généré.")
    return world

