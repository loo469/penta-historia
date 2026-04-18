from __future__ import annotations

import random

from src.core.types import WorldState


def tick_war(world: WorldState) -> None:
    for _ in range(4):
        x = random.randint(1, world.width - 2)
        y = random.randint(1, world.height - 2)
        owner = world.owners[y][x]
        if owner is None:
            continue

        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        nx, ny = random.choice(neighbors)
        other = world.owners[ny][nx]
        if other is None or other == owner:
            continue

        attacker = world.civilizations[owner]
        defender = world.civilizations[other]
        attack_power = attacker.military + attacker.industry * 0.2 + random.random() * 4
        defense_power = defender.military + defender.stability * 0.3 + random.random() * 4
        if attack_power > defense_power:
            world.owners[ny][nx] = owner
            attacker.influence += 0.3
            defender.stability = max(0.0, defender.stability - 0.1)

