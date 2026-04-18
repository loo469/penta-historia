from __future__ import annotations

from typing import Any

from src.core.types import WorldState
from src.domain.intrigue import niveau_alerte_pour_cellule



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

    lines.append("")
    lines.append("Intrigues:")
    if world.intrigue.recent_operations:
        for operation in world.intrigue.recent_operations[:3]:
            lines.append(f"- T{operation.tick} {operation.summary}")
    else:
        lines.append("- Aucune opération récente")

    for cellule in list(world.intrigue.cellules.values())[:3]:
        alert_level = niveau_alerte_pour_cellule(cellule).value.upper()
        lines.append(f"- {cellule.code}: {alert_level} (heat {cellule.heat:.1f})")

    lines.append("")
    lines.append("Civilisations:")
    for civ in world.civilizations.values():
        sabotage_pressure = world.intrigue.sabotage_pressure.get(civ.civ_id, 0.0)
        suffix = f" X{sabotage_pressure:.1f}" if sabotage_pressure > 0.0 else ""
        lines.append(
            f"{civ.name} F{civ.food:.1f} I{civ.industry:.1f} M{civ.military:.1f} S{civ.stability:.1f} K{civ.knowledge:.1f}{suffix}"
        )

    lines.append("")
    lines.append("Journal:")
    for entry in world.log[-6:]:
        lines.append(f"- {entry}")
    return lines



def draw_hud(screen: Any, world: WorldState, font: Any) -> None:
    left = world.width * 28 + 16
    y = 16

    for line in build_hud_lines(world):
        surface = font.render(line, True, (240, 240, 240))
        screen.blit(surface, (left, y))
        y += 22
