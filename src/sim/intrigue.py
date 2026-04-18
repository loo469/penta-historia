from __future__ import annotations

import random

from src.core.types import WorldState


def tick_intrigue(world: WorldState) -> None:
    civs = list(world.civilizations.values())
    if len(civs) < 2:
        return

    source = random.choice(civs)
    target = random.choice([c for c in civs if c.civ_id != source.civ_id])
    if random.random() < 0.15:
        target.stability = max(0.0, target.stability - 0.2)
        source.influence += 0.15

