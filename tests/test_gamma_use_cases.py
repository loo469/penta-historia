from __future__ import annotations

import unittest

from src.adapters.persistence.in_memory_gamma import RecordedEventBus
from src.application.gamma_ports import Clock, CultureRepository, RandomProvider, ResearchRepository
from src.application.gamma_use_cases import AdvanceResearch, EvolveCulture, RegisterDivergence, TriggerHistoricalEvent
from src.domain.gamma import Culture, DivergencePoint, HistoricalEvent, ResearchState


class InMemoryCultureRepository(CultureRepository):
    def __init__(self) -> None:
        self.cultures = {1: Culture(civ_id=1)}
        self.divergences: list[DivergencePoint] = []
        self.events: list[HistoricalEvent] = []

    def get(self, civ_id: int) -> Culture:
        return self.cultures.setdefault(civ_id, Culture(civ_id=civ_id))

    def save(self, culture: Culture) -> None:
        self.cultures[culture.civ_id] = culture

    def list_divergences(self) -> list[DivergencePoint]:
        return list(self.divergences)

    def add_divergence(self, divergence: DivergencePoint) -> None:
        self.divergences.append(divergence)

    def list_recorded_events(self) -> list[HistoricalEvent]:
        return list(self.events)

    def record_event(self, event: HistoricalEvent) -> None:
        self.events.append(event)


class InMemoryResearchRepository(ResearchRepository):
    def __init__(self) -> None:
        self.states = {1: ResearchState(civ_id=1)}

    def get(self, civ_id: int) -> ResearchState:
        return self.states.setdefault(civ_id, ResearchState(civ_id=civ_id))

    def save(self, state: ResearchState) -> None:
        self.states[state.civ_id] = state


class FixedClock(Clock):
    def __init__(self, tick: int) -> None:
        self.tick = tick

    def current_tick(self) -> int:
        return self.tick


class FirstCandidateRandom(RandomProvider):
    def choose_weighted(self, candidates: list[tuple[HistoricalEvent, int]]) -> HistoricalEvent | None:
        if not candidates:
            return None
        return candidates[0][0]


class GammaUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.culture_repository = InMemoryCultureRepository()
        self.research_repository = InMemoryResearchRepository()
        self.event_bus = RecordedEventBus()

    def test_advance_research_unlocks_topic_and_emits_events(self) -> None:
        result = AdvanceResearch(self.research_repository, self.event_bus).execute(1, "Astronomie", 10.0)

        self.assertTrue(result.unlocked)
        self.assertIn("astronomie", self.research_repository.get(1).unlocked)
        self.assertEqual(self.event_bus.events[0][0], "gamma.research.advanced")
        self.assertEqual(self.event_bus.events[1][0], "gamma.research.unlocked")

    def test_evolve_culture_updates_values_and_traditions(self) -> None:
        result = EvolveCulture(self.culture_repository, self.event_bus).execute(
            1,
            {"knowledge": 0.25, "tradition": -0.1},
            tradition="Fêtes des archives",
        )

        culture = self.culture_repository.get(1)
        self.assertAlmostEqual(culture.values["knowledge"], 0.75)
        self.assertIn("Fêtes des archives", culture.traditions)
        self.assertEqual(result.traditions, tuple(culture.traditions))

    def test_register_divergence_ignores_duplicate_keys(self) -> None:
        use_case = RegisterDivergence(self.culture_repository, self.event_bus)
        divergence = DivergencePoint(
            key="age_of_glass",
            title="Âge de verre",
            description="Les savants standardisent les observatoires.",
            tick=7,
            civ_id=1,
        )

        self.assertTrue(use_case.execute(divergence))
        self.assertFalse(use_case.execute(divergence))
        self.assertEqual(len(self.culture_repository.divergences), 1)

    def test_trigger_historical_event_records_effects_and_divergence(self) -> None:
        use_case = TriggerHistoricalEvent(
            culture_repository=self.culture_repository,
            research_repository=self.research_repository,
            event_bus=self.event_bus,
            random_provider=FirstCandidateRandom(),
            clock=FixedClock(8),
        )
        event = HistoricalEvent(
            event_id="gamma_renaissance_1",
            title="Renaissance savante",
            description="Une génération de chroniqueurs transforme la recherche.",
            weight=2,
            min_tick=4,
            civ_id=1,
            culture_pressure={"knowledge": 0.1},
            research_grants={"astronomie": 10.0},
            divergence=DivergencePoint(
                key="renaissance_1",
                title="Renaissance d'Aster",
                description="Le savoir devient public.",
                tick=8,
                civ_id=1,
                world_flags=("age_of_curiosity",),
            ),
        )

        selected = use_case.execute([event], civ_id=1)

        self.assertIsNotNone(selected)
        self.assertEqual(self.culture_repository.events[0].event_id, "gamma_renaissance_1")
        self.assertIn("astronomie", self.research_repository.get(1).unlocked)
        self.assertEqual(self.culture_repository.divergences[0].key, "renaissance_1")
        self.assertEqual(self.event_bus.events[-1][0], "gamma.historical_event.triggered")


if __name__ == "__main__":
    unittest.main()
