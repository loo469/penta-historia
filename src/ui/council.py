from __future__ import annotations

from src.core.types import AgentName, Suggestion, WorldState


def build_suggestions(world: WorldState) -> list[Suggestion]:
    strongest = max(world.civilizations.values(), key=lambda civ: civ.military)
    richest = max(world.civilizations.values(), key=lambda civ: civ.industry)
    wisest = max(world.civilizations.values(), key=lambda civ: civ.knowledge)
    weakest = min(world.civilizations.values(), key=lambda civ: civ.stability)

    return [
        Suggestion(AgentName.ALPHA, "Pousser le front", f"Alpha veut étendre {strongest.name} sur les frontières voisines.", "alpha_expand"),
        Suggestion(AgentName.BETA, "Consolider les villes", f"Beta veut améliorer la logistique de {richest.name}.", "beta_build"),
        Suggestion(AgentName.GAMMA, "Déclencher une renaissance", f"Gamma veut accélérer la recherche de {wisest.name}.", "gamma_research"),
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
    elif effect_key == "delta_plot":
        weakest = min(world.civilizations.values(), key=lambda civ: civ.stability)
        weakest.stability = max(0.0, weakest.stability - 1.2)
        world.log.append(f"Delta a semé le désordre chez {weakest.name}.")
    elif effect_key == "epsilon_omen":
        world.climate.fertility_modifier *= 1.15
        world.climate.anomaly = "omen"
        world.log.append("Epsilon a lancé un augure qui courbe le destin du monde.")

