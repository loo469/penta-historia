from __future__ import annotations

import random

from src.core.types import WorldState



def compute_attack_power(world: WorldState, civ_id: int, roll: float) -> float:
    civ = world.civilizations[civ_id]
    disruption = world.intrigue.frontline_disruption.get(civ_id, 0.0)
    modifier = max(0.5, 1.0 - disruption * 0.16)
    return (civ.military + civ.industry * 0.2 + roll * 4) * modifier



def compute_defense_power(world: WorldState, civ_id: int, roll: float) -> float:
    civ = world.civilizations[civ_id]
    disruption = world.intrigue.frontline_disruption.get(civ_id, 0.0)
    modifier = max(0.55, 1.0 - disruption * 0.10)
    return (civ.military + civ.stability * 0.3 + roll * 4) * modifier



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
        attack_power = compute_attack_power(world, owner, random.random())
        defense_power = compute_defense_power(world, other, random.random())
        if attack_power > defense_power:
            world.owners[ny][nx] = owner
            attacker.influence += 0.3
            defender.stability = max(0.0, defender.stability - 0.1)
