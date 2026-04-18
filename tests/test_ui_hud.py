from __future__ import annotations

import unittest

from src.domain.gamma import DivergencePoint, HistoricalEvent
from src.ui.hud import build_gamma_highlights, build_hud_lines
from src.world.generator import generate_world


class HudTests(unittest.TestCase):
    def test_build_gamma_highlights_keeps_recent_major_events_compact(self) -> None:
        world = generate_world()
        world.emitted_events.extend(
            [
                {"topic": "gamma.research.unlocked", "payload": {"civ_id": 0, "topic": "astronomie"}},
                {"topic": "gamma.divergence.registered", "payload": {"civ_id": 0, "title": "Renaissance d'Aster"}},
                {"topic": "gamma.historical_event.triggered", "payload": {"civ_id": 0, "title": "Syncrétisme civique"}},
                {"topic": "gamma.research.unlocked", "payload": {"civ_id": 1, "topic": "cartographie"}},
            ]
        )

        highlights = build_gamma_highlights(world)

        self.assertEqual(len(highlights), 3)
        self.assertEqual(highlights[-1], "Découverte: Boreal maîtrise cartographie")
        self.assertIn("Uchronie: Renaissance d'Aster", highlights)

    def test_build_hud_lines_surfaces_gamma_section_when_major_changes_exist(self) -> None:
        world = generate_world()
        world.divergence_points.append(
            DivergencePoint(
                key="age_of_curiosity",
                title="Âge de curiosité",
                description="Les académies prolifèrent.",
                tick=6,
                civ_id=0,
            )
        )
        world.historical_events.append(
            HistoricalEvent(
                event_id="gamma_renaissance_0",
                title="Renaissance savante",
                description="Le savoir devient public.",
                civ_id=0,
            )
        )
        world.emitted_events.append(
            {"topic": "gamma.divergence.registered", "payload": {"civ_id": 0, "title": "Âge de curiosité"}}
        )

        lines = build_hud_lines(world)

        self.assertIn("Percées Gamma:", lines)
        self.assertIn("- Uchronie: Âge de curiosité", lines)


if __name__ == "__main__":
    unittest.main()
