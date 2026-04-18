from __future__ import annotations

import unittest

from src.domain.council import apply_suggestion, build_suggestions
from src.world.generator import generate_world


class DomainCouncilTests(unittest.TestCase):
    def test_domain_council_builds_distinct_agent_suggestions(self) -> None:
        world = generate_world()

        suggestions = build_suggestions(world)

        self.assertEqual(len(suggestions), 5)
        self.assertEqual([suggestion.agent.value for suggestion in suggestions], ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

    def test_domain_council_application_changes_world_state(self) -> None:
        world = generate_world()
        before = sum(civ.military for civ in world.civilizations.values())

        apply_suggestion(world, "alpha_expand")

        after = sum(civ.military for civ in world.civilizations.values())
        self.assertGreater(after, before)
        self.assertIn("Alpha", world.log[-1])


if __name__ == "__main__":
    unittest.main()
