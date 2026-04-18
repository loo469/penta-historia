from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.adapters.persistence.gamma_loader import GammaContentLoader, yaml


class GammaLoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = GammaContentLoader()

    def test_load_catalog_from_json(self) -> None:
        payload = {
            "divergence_points": [
                {
                    "key": "age_of_curiosity",
                    "title": "Âge de curiosité",
                    "description": "Les académies prolifèrent.",
                    "tick": 5,
                    "world_flags": ["renaissance"],
                }
            ],
            "historical_events": [
                {
                    "event_id": "gamma_renaissance",
                    "title": "Renaissance savante",
                    "description": "Le savoir circule plus vite.",
                    "weight": 3,
                    "min_tick": 4,
                    "required_flags": ["age_of_curiosity"],
                    "culture_pressure": {"knowledge": 0.12},
                    "research_grants": {"astronomie": 1.5},
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "gamma_catalog.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            catalog = self.loader.load_catalog(path)

        self.assertEqual(catalog.divergence_points[0].key, "age_of_curiosity")
        self.assertEqual(catalog.historical_events[0].event_id, "gamma_renaissance")
        self.assertEqual(catalog.historical_events[0].research_grants["astronomie"], 1.5)

    @unittest.skipIf(yaml is None, "PyYAML not installed")
    def test_load_catalog_from_yaml(self) -> None:
        payload = """
        divergence_points:
          - key: age_of_curiosity
            title: Âge de curiosité
            description: Les académies prolifèrent.
            tick: 5
        historical_events:
          - event_id: gamma_syncretism
            title: Syncrétisme civique
            description: Les traditions se recomposent.
            weight: 2
            min_tick: 6
            blocked_flags:
              - age_of_curiosity
        """

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "gamma_catalog.yaml"
            path.write_text(payload, encoding="utf-8")
            catalog = self.loader.load_catalog(path)

        self.assertEqual(catalog.historical_events[0].event_id, "gamma_syncretism")
        self.assertEqual(catalog.historical_events[0].blocked_flags, frozenset({"age_of_curiosity"}))


if __name__ == "__main__":
    unittest.main()
