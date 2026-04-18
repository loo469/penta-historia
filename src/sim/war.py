from __future__ import annotations

from src.adapters.persistence.in_memory_war import (
    InMemoryFactionStateRepository,
    InMemoryMapRepository,
    WorldStateBattleResolver,
    WorldStateEventBus,
)
from src.application.war_use_cases import ExpandTerritory, ResolveBorderPressure, StabilizeCapturedProvince
from src.core.types import WorldState


def tick_war(world: WorldState) -> None:
    if not world.civilizations:
        return

    map_repository = InMemoryMapRepository(world)
    faction_state_repository = InMemoryFactionStateRepository(world, map_repository)
    battle_resolver = WorldStateBattleResolver(world)
    event_bus = WorldStateEventBus(world)

    ResolveBorderPressure(
        map_repository=map_repository,
        faction_state_repository=faction_state_repository,
        battle_resolver=battle_resolver,
    ).execute()
    ExpandTerritory(
        map_repository=map_repository,
        faction_state_repository=faction_state_repository,
        battle_resolver=battle_resolver,
        event_bus=event_bus,
    ).execute()
    StabilizeCapturedProvince(
        map_repository=map_repository,
        faction_state_repository=faction_state_repository,
        event_bus=event_bus,
    ).execute()
