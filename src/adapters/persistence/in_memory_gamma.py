from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.application.gamma_ports import Clock, CultureRepository, EventBus, RandomProvider, ResearchRepository
from src.application.gamma_use_cases import build_default_culture, build_default_research_state
from src.domain.gamma import Culture, DivergencePoint, HistoricalEvent, ResearchState
from src.domain.model import WorldState


class WorldStateCultureRepository(CultureRepository):
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def get(self, civ_id: int) -> Culture:
        if civ_id not in self.world.cultures:
            self.world.cultures[civ_id] = build_default_culture(civ_id)
        return self.world.cultures[civ_id]

    def save(self, culture: Culture) -> None:
        self.world.cultures[culture.civ_id] = culture

    def list_divergences(self) -> list[DivergencePoint]:
        return list(self.world.divergence_points)

    def add_divergence(self, divergence: DivergencePoint) -> None:
        self.world.divergence_points.append(divergence)

    def list_recorded_events(self) -> list[HistoricalEvent]:
        return list(self.world.historical_events)

    def record_event(self, event: HistoricalEvent) -> None:
        self.world.historical_events.append(event)


class WorldStateResearchRepository(ResearchRepository):
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def get(self, civ_id: int) -> ResearchState:
        if civ_id not in self.world.research_states:
            self.world.research_states[civ_id] = build_default_research_state(civ_id)
        return self.world.research_states[civ_id]

    def save(self, state: ResearchState) -> None:
        self.world.research_states[state.civ_id] = state


class WorldLogEventBus(EventBus):
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def publish(self, topic: str, payload: dict[str, object]) -> None:
        self.world.emitted_events.append({"topic": topic, "payload": payload})


class PythonRandomProvider(RandomProvider):
    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)

    def choose_weighted(self, candidates: list[tuple[HistoricalEvent, int]]) -> HistoricalEvent | None:
        if not candidates:
            return None
        items = [candidate for candidate, _ in candidates]
        weights = [weight for _, weight in candidates]
        return self._random.choices(items, weights=weights, k=1)[0]


class WorldTickClock(Clock):
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def current_tick(self) -> int:
        return self.world.tick_count


@dataclass
class RecordedEventBus(EventBus):
    events: list[tuple[str, dict[str, object]]] = field(default_factory=list)

    def publish(self, topic: str, payload: dict[str, object]) -> None:
        self.events.append((topic, payload))
