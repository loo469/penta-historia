from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.types import WorldState

if TYPE_CHECKING:
    import pygame


MAX_GAMMA_HIGHLIGHTS = 3


def build_gamma_highlights(world: WorldState, limit: int = MAX_GAMMA_HIGHLIGHTS) -> list[str]:
    highlights: list[str] = []
    seen: set[str] = set()

    for emitted in reversed(world.emitted_events):
        topic = str(emitted.get("topic", ""))
        payload = emitted.get("payload", {})
        formatted = _format_gamma_event(world, topic, payload if isinstance(payload, dict) else {})
        if formatted is None or formatted in seen:
            continue
        highlights.append(formatted)
        seen.add(formatted)
        if len(highlights) >= limit:
            break

    if not highlights:
        for divergence in reversed(world.divergence_points):
            formatted = f"Uchronie: {divergence.title}"
            if formatted in seen:
                continue
            highlights.append(formatted)
            seen.add(formatted)
            if len(highlights) >= limit:
                break

    if not highlights:
        for civ_id, research_state in sorted(world.research_states.items()):
            if not research_state.unlocked:
                continue
            topic = sorted(research_state.unlocked)[-1]
            civ_name = _civ_name(world, civ_id)
            highlights.append(f"Découverte: {civ_name} maîtrise {topic}")
            if len(highlights) >= limit:
                break

    return list(reversed(highlights))


def build_hud_lines(world: WorldState) -> list[str]:
    lines = [
        f"Année {world.climate.year}, {world.climate.season_name}",
        f"Anomalie: {world.climate.anomaly}",
        f"Tick: {world.tick_count}",
        "",
        "Conseil des cinq:",
    ]

    for index, suggestion in enumerate(world.suggestions, start=1):
        lines.append(f"{index}. {suggestion.agent.value}: {suggestion.title}")
        lines.append(f"   {suggestion.description}")

    gamma_highlights = build_gamma_highlights(world)
    if gamma_highlights:
        lines.append("")
        lines.append("Percées Gamma:")
        for highlight in gamma_highlights:
            lines.append(f"- {highlight}")

    lines.append("")
    lines.append("Civilisations:")
    for civ in world.civilizations.values():
        lines.append(
            f"{civ.name} F{civ.food:.1f} I{civ.industry:.1f} M{civ.military:.1f} S{civ.stability:.1f} K{civ.knowledge:.1f}"
        )

    lines.append("")
    lines.append("Journal:")
    for entry in world.log[-6:]:
        lines.append(f"- {entry}")

    return lines


def draw_hud(screen: "pygame.Surface", world: WorldState, font: "pygame.font.Font") -> None:
    left = world.width * 28 + 16
    y = 16

    for line in build_hud_lines(world):
        surface = font.render(line, True, (240, 240, 240))
        screen.blit(surface, (left, y))
        y += 22


def _format_gamma_event(world: WorldState, topic: str, payload: dict[str, object]) -> str | None:
    civ_name = _civ_name(world, payload.get("civ_id"))

    if topic == "gamma.research.unlocked":
        research_topic = str(payload.get("topic", "découverte")).replace("_", " ")
        return f"Découverte: {civ_name} maîtrise {research_topic}"
    if topic == "gamma.divergence.registered":
        title = str(payload.get("title", "bifurcation historique"))
        return f"Uchronie: {title}"
    if topic == "gamma.historical_event.triggered":
        title = str(payload.get("title", "événement historique"))
        return f"Événement: {title} ({civ_name})"
    return None


def _civ_name(world: WorldState, civ_id: object) -> str:
    if isinstance(civ_id, int) and civ_id in world.civilizations:
        return world.civilizations[civ_id].name
    return "Monde"
