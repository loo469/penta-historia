from __future__ import annotations

from src.domain.model import WorldState
from src.sim.climate import tick_climate
from src.sim.economy import tick_economy
from src.sim.intrigue import tick_intrigue
from src.sim.research import tick_research
from src.sim.war import tick_war


class DefaultSimulationRulesAdapter:
    def advance(self, world: WorldState) -> None:
        world.tick_count += 1
        tick_climate(world)
        tick_economy(world)
        tick_research(world)
        tick_intrigue(world)
        tick_war(world)

