from __future__ import annotations

from typing import Protocol

from src.domain.climate import Catastrophe, ClimateState, Myth, RegionSnapshot
from src.domain.model import WorldState
from src.domain.war import FactionTerritory, Front, Province


class WorldGeneratorPort(Protocol):
    def generate(self, width: int = 28, height: int = 18, civ_count: int = 4) -> WorldState: ...


class SimulationRulesPort(Protocol):
    def advance(self, world: WorldState) -> None: ...


class CouncilPort(Protocol):
    def build_suggestions(self, world: WorldState) -> list: ...
    def apply_suggestion(self, world: WorldState, effect_key: str) -> None: ...


class ClimateRepositoryPort(Protocol):
    def load(self) -> ClimateState: ...
    def save(self, climate_state: ClimateState) -> None: ...


class WorldReadPort(Protocol):
    def get_region_snapshots(self) -> list[RegionSnapshot]: ...


class WorldEventPort(Protocol):
    def record_world_event(self, message: str) -> None: ...
    def apply_catastrophe(self, catastrophe: Catastrophe) -> None: ...


class MythLedgerPort(Protocol):
    def record(self, myth: Myth) -> None: ...


class MapRepository(Protocol):
    def list_provinces(self) -> list[Province]: ...
    def save_provinces(self, provinces: list[Province]) -> None: ...


class FactionStateRepository(Protocol):
    def list_faction_territories(self) -> dict[int, FactionTerritory]: ...
    def save_faction_territories(self, territories: dict[int, FactionTerritory]) -> None: ...


class BattleResolverPort(Protocol):
    def resolve_advantage(self, front: Front, territories: dict[int, FactionTerritory]) -> float: ...


class WorldEventBus(Protocol):
    def publish(self, event_name: str, payload: dict[str, object]) -> None: ...

