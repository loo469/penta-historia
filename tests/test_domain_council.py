from __future__ import annotations

import unittest

from src.domain.council import apply_suggestion, build_suggestions
from src.domain.gamma import DivergencePoint
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

    def test_gamma_suggestion_changes_when_major_discovery_exists(self) -> None:
        world = generate_world()
        world.research_states[0].unlocked.add("astronomie")

        gamma_suggestion = build_suggestions(world)[2]

        self.assertEqual(gamma_suggestion.effect_key, "gamma_institutionalize")
        self.assertIn("astronomie", gamma_suggestion.description)

    def test_gamma_suggestion_prioritizes_divergence_and_changes_effect(self) -> None:
        world = generate_world()
        world.divergence_points.append(
            DivergencePoint(
                key="age_of_curiosity",
                title="Âge de curiosité",
                description="Les académies prolifèrent.",
                tick=8,
                civ_id=1,
                world_flags=("age_of_curiosity",),
            )
        )
        before = world.civilizations[1].influence

        gamma_suggestion = build_suggestions(world)[2]
        apply_suggestion(world, gamma_suggestion.effect_key)

        self.assertEqual(gamma_suggestion.effect_key, "gamma_anchor_divergence")
        self.assertIn("Âge de curiosité", gamma_suggestion.description)
        self.assertGreater(world.civilizations[1].influence, before)
        self.assertIn("Gamma", world.log[-1])


if __name__ == "__main__":
    unittest.main()
