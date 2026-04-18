from __future__ import annotations

from src.core.types import WorldState


def tick_research(world: WorldState) -> None:
    for civ in world.civilizations.values():
        civ.knowledge += 0.12 + civ.industry * 0.01
        civ.culture += 0.08 + civ.stability * 0.01

