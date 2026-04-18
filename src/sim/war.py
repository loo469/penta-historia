from __future__ import annotations

from src.adapters.persistence.in_memory_war import (
    InMemoryFactionStateRepository,
    InMemoryMapRepository,
    WorldStateBattleResolver,
    WorldStateEventBus,
)
from src.application.war_use_cases import ExpandTerritory, ResolveBorderPressure, StabilizeCapturedProvince
from src.core.types import WorldState
from src.domain.war import Front


def _build_front_snapshot(fronts: list[Front]) -> dict[str, dict[str, object]]:
    snapshot: dict[str, dict[str, object]] = {}
    for front in fronts:
        attacker, defender = sorted((front.attacker, front.defender))
        key = f"{attacker}:{defender}"
        entry = snapshot.setdefault(
            key,
            {
                "attacker": attacker,
                "defender": defender,
                "length": 0,
                "pressure": 0.0,
            },
        )
        entry["length"] = max(int(entry["length"]), front.length)
        entry["pressure"] = max(float(entry["pressure"]), front.pressure)
    return snapshot


def _sync_front_events(world: WorldState, event_bus: WorldStateEventBus, fronts: list[Front]) -> None:
    previous_snapshot = world.war_state.get("front_snapshot")
    previous = previous_snapshot if isinstance(previous_snapshot, dict) else {}
    current = _build_front_snapshot(fronts)

    previous_keys = set(previous)
    current_keys = set(current)

    for key in sorted(current_keys - previous_keys):
        event_bus.publish("FrontCreated", current[key])
    for key in sorted(previous_keys - current_keys):
        event_bus.publish("FrontCollapsed", previous[key])

    world.war_state["front_snapshot"] = current


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
    final_fronts = ResolveBorderPressure(
        map_repository=map_repository,
        faction_state_repository=faction_state_repository,
        battle_resolver=battle_resolver,
    ).execute()
    _sync_front_events(world, event_bus, final_fronts)
