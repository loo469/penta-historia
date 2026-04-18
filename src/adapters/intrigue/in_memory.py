from __future__ import annotations

import random
from collections.abc import Iterable
from typing import Any

from src.domain.model import Civilization, WorldState


class InMemoryIntrigueGateway:
    def __init__(
        self,
        world: WorldState,
        random_values: Iterable[float] | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self._world = world
        self._random_values = iter(random_values or [])
        self._rng = rng or random.Random()
        self.events: list[dict[str, Any]] = []

    def get_world(self) -> WorldState:
        return self._world

    def get_faction(self, faction_id: int) -> Civilization:
        return self._world.civilizations[faction_id]

    def now(self) -> int:
        return self._world.tick_count

    def random(self) -> float:
        try:
            return next(self._random_values)
        except StopIteration:
            return self._rng.random()

    def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        self.events.append({"event_name": event_name, "payload": payload})
