from __future__ import annotations

from src.adapters.persistence.in_memory_gamma import (
    PythonRandomProvider,
    WorldLogEventBus,
    WorldStateCultureRepository,
    WorldStateResearchRepository,
    WorldTickClock,
)
from src.application.gamma_use_cases import AdvanceResearch, EvolveCulture, RegisterDivergence, TriggerHistoricalEvent
from src.domain.gamma import DivergencePoint, HistoricalEvent
from src.core.types import WorldState


def _build_dynamic_events(world: WorldState, civ_id: int) -> list[HistoricalEvent]:
    civilization = world.civilizations[civ_id]
    return [
        HistoricalEvent(
            event_id=f"gamma_renaissance_{civ_id}",
            title="Renaissance savante",
            description=f"{civilization.name} convertit son savoir en renouveau culturel.",
            weight=3,
            min_tick=4,
            civ_id=civ_id,
            culture_pressure={"knowledge": 0.08, "tradition": -0.03},
            research_grants={"astronomie": 1.6},
            divergence=DivergencePoint(
                key=f"renaissance_{civ_id}",
                title=f"Renaissance de {civilization.name}",
                description=f"{civilization.name} entre dans une ère de curiosité publique.",
                tick=world.tick_count,
                civ_id=civ_id,
                tags=("renaissance", civilization.name.lower()),
                world_flags=("age_of_curiosity",),
            ),
        ),
        HistoricalEvent(
            event_id=f"gamma_syncretism_{civ_id}",
            title="Syncrétisme civique",
            description=f"{civilization.name} fusionne anciennes traditions et nouvelles idées.",
            weight=2,
            min_tick=6,
            civ_id=civ_id,
            culture_pressure={"tradition": 0.07, "spirituality": 0.05},
            research_grants={"institutions": 1.2},
            blocked_flags=frozenset({f"renaissance_{civ_id}"}),
        ),
    ]


def tick_research(world: WorldState) -> None:
    culture_repository = WorldStateCultureRepository(world)
    research_repository = WorldStateResearchRepository(world)
    event_bus = WorldLogEventBus(world)
    random_provider = PythonRandomProvider(seed=world.tick_count)
    clock = WorldTickClock(world)

    advance_research = AdvanceResearch(research_repository, event_bus)
    evolve_culture = EvolveCulture(culture_repository, event_bus)
    register_divergence = RegisterDivergence(culture_repository, event_bus)
    trigger_historical_event = TriggerHistoricalEvent(
        culture_repository=culture_repository,
        research_repository=research_repository,
        event_bus=event_bus,
        random_provider=random_provider,
        clock=clock,
    )

    for civ in world.civilizations.values():
        research_points = round(0.12 + civ.industry * 0.01, 3)
        culture_points = round(0.08 + civ.stability * 0.01, 3)
        research_result = advance_research.execute(civ.civ_id, "philosophie", research_points)
        culture_result = evolve_culture.execute(
            civ.civ_id,
            {
                "knowledge": round(0.01 + civ.industry * 0.001, 3),
                "tradition": round(0.004 + civ.stability * 0.0005, 3),
            },
            tradition="chroniques orales" if world.tick_count == 1 else None,
        )

        civ.knowledge += research_points
        civ.culture += culture_points + culture_result.stability_bonus
        civ.stability = max(0.0, civ.stability + culture_result.stability_bonus * 0.5)

        if research_result.unlocked:
            divergence = DivergencePoint(
                key=f"research_{civ.civ_id}_{research_result.topic}",
                title=f"{civ.name} maîtrise {research_result.topic}",
                description=f"{civ.name} transforme {research_result.topic} en doctrine d'État.",
                tick=world.tick_count,
                civ_id=civ.civ_id,
                tags=("research", research_result.topic),
                world_flags=(f"tech_{research_result.topic}",),
            )
            if register_divergence.execute(divergence):
                world.log.append(f"Gamma: {divergence.title}.")

        if world.tick_count % 4 == 0:
            event = trigger_historical_event.execute(_build_dynamic_events(world, civ.civ_id), civ_id=civ.civ_id)
            if event is not None:
                world.log.append(f"Gamma: {event.title} chez {civ.name}.")
