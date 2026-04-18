from __future__ import annotations

import unittest

from src.adapters.climate.in_memory import (
    InMemoryClimateRepository,
    InMemoryMythLedger,
    WorldStateEventAdapter,
    WorldStateReadAdapter,
)
from src.application.climate_use_cases import (
    AdvanceSeasons,
    RegisterMythFromEvent,
    TriggerCatastrophe,
    UpdateRegionalClimate,
)
from src.sim.climate import tick_climate
from src.world.generator import generate_world


class ClimateHexagonTests(unittest.TestCase):
    def _make_dry_world(self):
        world = generate_world(width=12, height=12, civ_count=4)
        for y, row in enumerate(world.fertility):
            for x, _ in enumerate(row):
                row[x] = 0.18 if y < 4 else 0.28 if y < 8 else 0.22
        for civ in world.civilizations.values():
            civ.stability = 11.0
        return world

    def test_one_simulated_year_creates_region_profiles_catastrophe_and_myth(self) -> None:
        world = self._make_dry_world()
        climate_repository = InMemoryClimateRepository(world)
        world_reader = WorldStateReadAdapter(world)
        world_events = WorldStateEventAdapter(world)
        myth_ledger = InMemoryMythLedger(world)

        for _ in range(4):
            AdvanceSeasons(climate_repository, world_events).execute()
            UpdateRegionalClimate(climate_repository, world_reader, world_events).execute()
            catastrophe = TriggerCatastrophe(climate_repository, world_reader, world_events).execute(min_severity=0.25)
            if catastrophe is not None:
                RegisterMythFromEvent(climate_repository, myth_ledger, world_events).from_catastrophe(catastrophe)

        self.assertEqual(world.climate.year, 2)
        self.assertEqual(world.climate.season_name, "Printemps")
        self.assertTrue(world.climate.region_profiles)
        self.assertGreaterEqual(len(world.climate.active_catastrophes), 1)
        self.assertGreaterEqual(len(world.climate.myths), 1)
        self.assertTrue(any("sécheresse" in entry for entry in world.log))

    def test_tick_climate_uses_hexagonal_flow_and_updates_world_state(self) -> None:
        world = self._make_dry_world()

        tick_climate(world)

        self.assertEqual(world.climate.season_name, "Été")
        self.assertIn(world.climate.anomaly, {"dry", "storm", "frost", "omen", "stable"})
        self.assertTrue(world.climate.region_profiles)
        self.assertNotEqual(world.climate.fertility_modifier, 1.0)
        self.assertTrue(any("cycle" in entry.lower() or "climat" in entry.lower() for entry in world.log))


if __name__ == "__main__":
    unittest.main()
