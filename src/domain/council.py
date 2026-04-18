from __future__ import annotations

from src.domain.gamma import ResearchState
from src.domain.model import AgentName, Civilization, Suggestion, WorldState


def build_suggestions(world: WorldState) -> list[Suggestion]:
    strongest = max(world.civilizations.values(), key=lambda civ: civ.military)
    richest = max(world.civilizations.values(), key=lambda civ: civ.industry)
    wisest = max(world.civilizations.values(), key=lambda civ: civ.knowledge)
    weakest = min(world.civilizations.values(), key=lambda civ: civ.stability)

    return [
        Suggestion(AgentName.ALPHA, "Pousser le front", f"Alpha veut étendre {strongest.name} sur les frontières voisines.", "alpha_expand"),
        Suggestion(AgentName.BETA, "Consolider les villes", f"Beta veut améliorer la logistique de {richest.name}.", "beta_build"),
        _build_gamma_suggestion(world, wisest),
        Suggestion(AgentName.DELTA, "Lancer des intrigues", f"Delta cible la stabilité de {weakest.name} par sabotage discret.", "delta_plot"),
        Suggestion(AgentName.EPSILON, "Invoquer un augure", "Epsilon modifie le climat du cycle suivant et crée une opportunité mondiale.", "epsilon_omen"),
    ]


def apply_suggestion(world: WorldState, effect_key: str) -> None:
    if effect_key == "alpha_expand":
        for civ in world.civilizations.values():
            civ.military += 0.6
        world.log.append("Alpha a ordonné une poussée générale des fronts.")
    elif effect_key == "beta_build":
        for civ in world.civilizations.values():
            civ.industry += 0.8
            civ.food += 0.4
        world.log.append("Beta a renforcé les infrastructures et les flux.")
    elif effect_key == "gamma_research":
        for civ in world.civilizations.values():
            civ.knowledge += 1.2
            civ.culture += 0.6
        world.log.append("Gamma a déclenché une vague d'innovation.")
    elif effect_key == "gamma_institutionalize":
        target = _resolve_gamma_target(world)
        target.knowledge += 0.9
        target.culture += 1.1
        target.influence += 0.8
        target.stability += 0.4
        world.log.append(f"Gamma a transformé une découverte majeure en institutions chez {target.name}.")
    elif effect_key == "gamma_shape_culture":
        target = _resolve_gamma_target(world)
        target.culture += 1.2
        target.stability += 0.8
        target.influence += 0.3
        world.log.append(f"Gamma a canalisé un basculement culturel chez {target.name}.")
    elif effect_key == "gamma_anchor_divergence":
        target = _resolve_gamma_target(world)
        target.culture += 1.0
        target.stability += 0.9
        target.influence += 1.0
        world.log.append(f"Gamma a ancré une bifurcation historique au profit de {target.name}.")
    elif effect_key == "delta_plot":
        weakest = min(world.civilizations.values(), key=lambda civ: civ.stability)
        weakest.stability = max(0.0, weakest.stability - 1.2)
        world.log.append(f"Delta a semé le désordre chez {weakest.name}.")
    elif effect_key == "epsilon_omen":
        world.climate.fertility_modifier *= 1.15
        world.climate.anomaly = "omen"
        world.log.append("Epsilon a lancé un augure qui courbe le destin du monde.")


def _build_gamma_suggestion(world: WorldState, default_target: Civilization) -> Suggestion:
    latest_divergence = world.divergence_points[-1] if world.divergence_points else None
    latest_event = world.historical_events[-1] if world.historical_events else None
    leading_research = _leading_research(world)

    if latest_divergence is not None:
        target_name = _civ_name(world, latest_divergence.civ_id, default_target.name)
        return Suggestion(
            AgentName.GAMMA,
            "Ancrer une bifurcation majeure",
            f"Gamma veut transformer {latest_divergence.title} en avantage durable pour {target_name}.",
            "gamma_anchor_divergence",
        )

    if latest_event is not None and (latest_event.culture_pressure or latest_event.divergence is not None):
        target_name = _civ_name(world, latest_event.civ_id, default_target.name)
        return Suggestion(
            AgentName.GAMMA,
            "Canaliser un basculement culturel",
            f"Gamma veut exploiter {latest_event.title} pour réorienter durablement {target_name}.",
            "gamma_shape_culture",
        )

    if leading_research is not None and leading_research[1].unlocked:
        civ_id, research_state = leading_research
        topic = sorted(research_state.unlocked)[-1]
        target_name = _civ_name(world, civ_id, default_target.name)
        return Suggestion(
            AgentName.GAMMA,
            "Diffuser une découverte majeure",
            f"Gamma veut convertir {topic} en institutions, prestige et influence pour {target_name}.",
            "gamma_institutionalize",
        )

    return Suggestion(
        AgentName.GAMMA,
        "Déclencher une renaissance",
        f"Gamma veut accélérer la recherche de {default_target.name}.",
        "gamma_research",
    )


def _leading_research(world: WorldState) -> tuple[int, ResearchState] | None:
    if not world.research_states:
        return None
    return max(
        world.research_states.items(),
        key=lambda item: (len(item[1].unlocked), round(sum(item[1].progress.values()), 3), item[0]),
    )


def _resolve_gamma_target(world: WorldState) -> Civilization:
    if world.divergence_points and world.divergence_points[-1].civ_id in world.civilizations:
        return world.civilizations[world.divergence_points[-1].civ_id]
    if world.historical_events and world.historical_events[-1].civ_id in world.civilizations:
        return world.civilizations[world.historical_events[-1].civ_id]
    leading_research = _leading_research(world)
    if leading_research is not None:
        civ_id, _ = leading_research
        return world.civilizations[civ_id]
    return max(world.civilizations.values(), key=lambda civ: civ.knowledge)


def _civ_name(world: WorldState, civ_id: int | None, default: str) -> str:
    if civ_id is None:
        return default
    civilization = world.civilizations.get(civ_id)
    if civilization is None:
        return default
    return civilization.name
