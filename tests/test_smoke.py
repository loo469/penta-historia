from __future__ import annotations

import unittest

from src.domain.council import apply_suggestion, build_suggestions
from src.world.generator import generate_world


class SmokeTests(unittest.TestCase):
    def test_world_generation_has_expected_shape(self) -> None:
        world = generate_world(width=12, height=8, civ_count=4)

        self.assertEqual(world.width, 12)
        self.assertEqual(world.height, 8)
        self.assertEqual(len(world.owners), 8)
        self.assertEqual(len(world.owners[0]), 12)
        self.assertEqual(len(world.civilizations), 4)
        self.assertEqual(len(world.cities), 4)

    def test_council_generates_five_suggestions(self) -> None:
        world = generate_world()
        suggestions = build_suggestions(world)

        self.assertEqual(len(suggestions), 5)
        self.assertEqual(len({suggestion.agent.value for suggestion in suggestions}), 5)

    def test_applying_a_suggestion_updates_the_world_log(self) -> None:
        world = generate_world()
        world.suggestions = build_suggestions(world)

        apply_suggestion(world, world.suggestions[0].effect_key)

        self.assertTrue(world.log)
        self.assertIn("Alpha", world.log[-1])


if __name__ == "__main__":
    unittest.main()
