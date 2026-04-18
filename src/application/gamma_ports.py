from __future__ import annotations

from typing import Protocol

from src.domain.gamma import Culture, DivergencePoint, HistoricalEvent, ResearchState


class CultureRepository(Protocol):
    def get(self, civ_id: int) -> Culture: ...

    def save(self, culture: Culture) -> None: ...

    def list_divergences(self) -> list[DivergencePoint]: ...

    def add_divergence(self, divergence: DivergencePoint) -> None: ...

    def list_recorded_events(self) -> list[HistoricalEvent]: ...

    def record_event(self, event: HistoricalEvent) -> None: ...


class ResearchRepository(Protocol):
    def get(self, civ_id: int) -> ResearchState: ...

    def save(self, state: ResearchState) -> None: ...


class EventBus(Protocol):
    def publish(self, topic: str, payload: dict[str, object]) -> None: ...


class RandomProvider(Protocol):
    def choose_weighted(self, candidates: list[tuple[HistoricalEvent, int]]) -> HistoricalEvent | None: ...


class Clock(Protocol):
    def current_tick(self) -> int: ...
