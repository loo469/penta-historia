from __future__ import annotations

from typing import Protocol

from src.domain.climate import Catastrophe, ClimateState, Myth, RegionSnapshot
from src.domain.model import WorldState


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

