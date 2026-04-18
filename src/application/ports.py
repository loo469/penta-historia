from __future__ import annotations

from typing import Protocol

from src.domain.model import WorldState


class WorldGeneratorPort(Protocol):
    def generate(self, width: int = 28, height: int = 18, civ_count: int = 4) -> WorldState: ...


class SimulationRulesPort(Protocol):
    def advance(self, world: WorldState) -> None: ...


class CouncilPort(Protocol):
    def build_suggestions(self, world: WorldState) -> list: ...
    def apply_suggestion(self, world: WorldState, effect_key: str) -> None: ...

