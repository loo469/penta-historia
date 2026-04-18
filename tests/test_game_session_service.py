from __future__ import annotations

import unittest

from src.adapters.council.default_council import DefaultCouncilAdapter
from src.adapters.generation.random_world_generator import RandomWorldGeneratorAdapter
from src.adapters.simulation.default_rules import DefaultSimulationRulesAdapter
from src.application.use_cases import GameSessionService


class GameSessionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = GameSessionService(
            world_generator=RandomWorldGeneratorAdapter(),
            simulation_rules=DefaultSimulationRulesAdapter(),
            council=DefaultCouncilAdapter(),
        )

    def test_create_world_populates_council_suggestions(self) -> None:
        world = self.service.create_world(width=12, height=8, civ_count=4)

        self.assertEqual(len(world.suggestions), 5)
        self.assertEqual(world.width, 12)
        self.assertEqual(world.height, 8)

    def test_advance_world_increments_tick_and_refreshes_suggestions(self) -> None:
        world = self.service.create_world()
        initial_tick = world.tick_count

        self.service.advance_world(world)

        self.assertEqual(world.tick_count, initial_tick + 1)
        self.assertEqual(len(world.suggestions), 5)

    def test_apply_player_choice_updates_world_log(self) -> None:
        world = self.service.create_world()

        self.service.apply_player_choice(world, 0)

        self.assertTrue(world.log)


if __name__ == "__main__":
    unittest.main()
