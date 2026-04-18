from __future__ import annotations

from src.adapters.climate.in_memory import (
    InMemoryClimateRepository,
    InMemoryMythLedger,
    WorldStateEventAdapter,
    WorldStateReadAdapter,
)
from src.application.climate_use_cases import (
    AdvanceSeasons,
    RegisterMythFromEvent,
    TriggerCatastrophe,
    UpdateRegionalClimate,
)
from src.core.types import WorldState


def tick_climate(world: WorldState) -> None:
    climate_repository = InMemoryClimateRepository(world)
    world_reader = WorldStateReadAdapter(world)
    world_events = WorldStateEventAdapter(world)
    myth_ledger = InMemoryMythLedger(world)

    AdvanceSeasons(climate_repository, world_events).execute()
    UpdateRegionalClimate(climate_repository, world_reader, world_events).execute()
    catastrophe = TriggerCatastrophe(climate_repository, world_reader, world_events).execute()
    if catastrophe is not None:
        RegisterMythFromEvent(climate_repository, myth_ledger, world_events).from_catastrophe(catastrophe)
