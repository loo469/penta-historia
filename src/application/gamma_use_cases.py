from __future__ import annotations

from dataclasses import dataclass

from src.application.gamma_ports import Clock, CultureRepository, EventBus, RandomProvider, ResearchRepository
from src.domain.gamma import Culture, DivergencePoint, HistoricalEvent, ResearchState


@dataclass(frozen=True)
class ResearchAdvanceResult:
    civ_id: int
    topic: str
    total_progress: float
    unlocked: bool


@dataclass(frozen=True)
class CultureEvolutionResult:
    civ_id: int
    applied_pressure: dict[str, float]
    traditions: tuple[str, ...]
    stability_bonus: float


class AdvanceResearch:
    def __init__(self, research_repository: ResearchRepository, event_bus: EventBus) -> None:
        self.research_repository = research_repository
        self.event_bus = event_bus

    def execute(self, civ_id: int, topic: str, points: float, unlock_cost: float = 10.0) -> ResearchAdvanceResult:
        state = self.research_repository.get(civ_id)
        unlocked = state.advance(topic, points, unlock_cost=unlock_cost)
        self.research_repository.save(state)

        normalized_topic = topic.strip().lower()
        total_progress = state.progress[normalized_topic]
        self.event_bus.publish(
            "gamma.research.advanced",
            {
                "civ_id": civ_id,
                "topic": normalized_topic,
                "points": round(points, 3),
                "total_progress": total_progress,
                "unlocked": unlocked,
            },
        )
        if unlocked:
            self.event_bus.publish(
                "gamma.research.unlocked",
                {
                    "civ_id": civ_id,
                    "topic": normalized_topic,
                    "unlock_cost": unlock_cost,
                },
            )

        return ResearchAdvanceResult(civ_id=civ_id, topic=normalized_topic, total_progress=total_progress, unlocked=unlocked)


class EvolveCulture:
    def __init__(self, culture_repository: CultureRepository, event_bus: EventBus) -> None:
        self.culture_repository = culture_repository
        self.event_bus = event_bus

    def execute(self, civ_id: int, pressure: dict[str, float], tradition: str | None = None) -> CultureEvolutionResult:
        culture = self.culture_repository.get(civ_id)
        applied = culture.evolve(pressure)
        if tradition is not None:
            culture.adopt_tradition(tradition)
        self.culture_repository.save(culture)

        self.event_bus.publish(
            "gamma.culture.evolved",
            {
                "civ_id": civ_id,
                "pressure": dict(pressure),
                "applied": applied,
                "stability_bonus": culture.stability_bonus,
                "traditions": list(culture.traditions),
            },
        )
        return CultureEvolutionResult(
            civ_id=civ_id,
            applied_pressure=applied,
            traditions=tuple(culture.traditions),
            stability_bonus=culture.stability_bonus,
        )


class RegisterDivergence:
    def __init__(self, culture_repository: CultureRepository, event_bus: EventBus) -> None:
        self.culture_repository = culture_repository
        self.event_bus = event_bus

    def execute(self, divergence: DivergencePoint) -> bool:
        known_keys = {item.key for item in self.culture_repository.list_divergences()}
        if divergence.key in known_keys:
            return False

        self.culture_repository.add_divergence(divergence)
        self.event_bus.publish(
            "gamma.divergence.registered",
            {
                "key": divergence.key,
                "title": divergence.title,
                "civ_id": divergence.civ_id,
                "tick": divergence.tick,
                "flags": sorted(divergence.all_flags()),
            },
        )
        return True


class TriggerHistoricalEvent:
    def __init__(
        self,
        culture_repository: CultureRepository,
        research_repository: ResearchRepository,
        event_bus: EventBus,
        random_provider: RandomProvider,
        clock: Clock,
    ) -> None:
        self.culture_repository = culture_repository
        self.research_repository = research_repository
        self.event_bus = event_bus
        self.random_provider = random_provider
        self.clock = clock
        self.advance_research = AdvanceResearch(research_repository, event_bus)
        self.evolve_culture = EvolveCulture(culture_repository, event_bus)
        self.register_divergence = RegisterDivergence(culture_repository, event_bus)

    def execute(self, candidates: list[HistoricalEvent], civ_id: int | None = None) -> HistoricalEvent | None:
        active_flags: set[str] = set()
        for divergence in self.culture_repository.list_divergences():
            active_flags.update(divergence.all_flags())

        seen_events = {event.event_id for event in self.culture_repository.list_recorded_events()}
        current_tick = self.clock.current_tick()
        eligible = [
            event
            for event in candidates
            if event.is_eligible(current_tick=current_tick, active_flags=active_flags, seen_events=seen_events, civ_id=civ_id)
        ]
        selected = self.random_provider.choose_weighted([(event, event.weight) for event in eligible])
        if selected is None:
            return None

        self.culture_repository.record_event(selected)

        target_civ_id = selected.civ_id if selected.civ_id is not None else civ_id
        if target_civ_id is not None and selected.culture_pressure:
            self.evolve_culture.execute(target_civ_id, dict(selected.culture_pressure))
        if target_civ_id is not None:
            for topic, amount in selected.research_grants.items():
                self.advance_research.execute(target_civ_id, topic, amount)
        if selected.divergence is not None:
            self.register_divergence.execute(selected.divergence)

        self.event_bus.publish(
            "gamma.historical_event.triggered",
            {
                "event_id": selected.event_id,
                "title": selected.title,
                "civ_id": target_civ_id,
                "tick": current_tick,
            },
        )
        return selected


def build_default_culture(civ_id: int) -> Culture:
    return Culture(civ_id=civ_id)


def build_default_research_state(civ_id: int) -> ResearchState:
    return ResearchState(civ_id=civ_id)
