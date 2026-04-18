from __future__ import annotations

from typing import Protocol

from src.domain.economy import ResourceType, TradeRoute
from src.domain.model import City, WorldState


class WorldGeneratorPort(Protocol):
    def generate(self, width: int = 28, height: int = 18, civ_count: int = 4) -> WorldState: ...


class SimulationRulesPort(Protocol):
    def advance(self, world: WorldState) -> None: ...


class CouncilPort(Protocol):
    def build_suggestions(self, world: WorldState) -> list: ...
    def apply_suggestion(self, world: WorldState, effect_key: str) -> None: ...


class CityRepository(Protocol):
    def list_all(self) -> list[City]: ...
    def get(self, city_name: str) -> City | None: ...
    def save(self, city: City) -> None: ...


class MarketRepository(Protocol):
    def get_price(self, city_name: str, resource: ResourceType) -> float: ...
    def set_price(self, city_name: str, resource: ResourceType, price: float) -> None: ...


class RouteRepository(Protocol):
    def list_all(self) -> list[TradeRoute]: ...


class ClockPort(Protocol):
    def now(self) -> int: ...


class EventBusPort(Protocol):
    def publish(self, event_name: str, payload: dict[str, object]) -> None: ...

