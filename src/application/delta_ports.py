from __future__ import annotations

from typing import Any, Protocol

from src.domain.model import Civilization, WorldState


class WorldReadPort(Protocol):
    def get_world(self) -> WorldState: ...


class FactionReadPort(Protocol):
    def get_faction(self, faction_id: int) -> Civilization: ...


class ClockPort(Protocol):
    def now(self) -> int: ...


class RandomPort(Protocol):
    def random(self) -> float: ...


class EventBusPort(Protocol):
    def publish(self, event_name: str, payload: dict[str, Any]) -> None: ...
