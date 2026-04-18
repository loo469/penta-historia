from __future__ import annotations

import pygame

from src.core.types import WorldState


def draw_hud(screen: pygame.Surface, world: WorldState, font: pygame.font.Font) -> None:
    left = world.width * 28 + 16
    y = 16
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

    for line in lines:
        surface = font.render(line, True, (240, 240, 240))
        screen.blit(surface, (left, y))
        y += 22

