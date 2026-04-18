from __future__ import annotations

import copy
import unittest

from src.adapters.intrigue.in_memory import InMemoryIntrigueGateway
from src.application.intrigue_use_cases import LancerOperation, ResoudreSabotage
from src.domain.intrigue import Agent, Cellule
from src.sim.economy import tick_economy
from src.sim.war import compute_attack_power
from src.ui.hud import build_hud_lines
from src.world.generator import generate_world


class IntrigueIntegrationTests(unittest.TestCase):
    def _build_world_with_network(self):
        world = generate_world(width=12, height=8, civ_count=3)
        world.civilizations[0].industry = 10.0
        world.civilizations[0].military = 10.0
        world.civilizations[0].stability = 10.0
        world.civilizations[1].industry = 10.0
        world.civilizations[1].military = 10.0
        world.civilizations[1].stability = 10.0
        world.intrigue.cellules["delta-0"] = Cellule(
            code="delta-0",
            faction_id=0,
            region="Aster Prime:4,4",
            agents=[
                Agent(code="a0", faction_id=0, stealth=1.4, cover=1.2),
                Agent(code="a1", faction_id=0, stealth=1.1, cover=1.0),
            ],
            heat=3.4,
        )
        return world

    def test_sabotage_pressure_reduces_economy_and_frontline_power(self) -> None:
        world = self._build_world_with_network()
        baseline = copy.deepcopy(world)
        gateway = InMemoryIntrigueGateway(world, random_values=[0.05, 0.99])
        sabotage = ResoudreSabotage(LancerOperation(gateway, gateway, gateway, gateway, gateway), gateway, gateway)

        sabotage.execute("delta-0", target_faction_id=1, target_region="Boreal Prime:6,4", preparation=1.2, intensity=1.1)
        base_attack = compute_attack_power(baseline, 1, 0.5)
        sabotaged_attack = compute_attack_power(world, 1, 0.5)

        tick_economy(baseline)
        tick_economy(world)

        self.assertLess(world.civilizations[1].industry, baseline.civilizations[1].industry)
        self.assertLess(sabotaged_attack, base_attack)
        self.assertGreater(world.intrigue.sabotage_pressure.get(1, 0.0), 0.0)

    def test_hud_lines_show_recent_intrigue_and_alert_level(self) -> None:
        world = self._build_world_with_network()
        gateway = InMemoryIntrigueGateway(world, random_values=[0.05, 0.99])
        sabotage = ResoudreSabotage(LancerOperation(gateway, gateway, gateway, gateway, gateway), gateway, gateway)

        sabotage.execute("delta-0", target_faction_id=1, target_region="Boreal Prime:6,4", preparation=1.2, intensity=1.1)
        lines = build_hud_lines(world)
        rendered = "\n".join(lines)

        self.assertIn("Intrigues:", rendered)
        self.assertIn("sabotage", rendered)
        self.assertIn("delta-0:", rendered)
        self.assertTrue(any(level in rendered for level in ("CALME", "SURVEILLANCE", "ALERTE", "EXPOSE")))


if __name__ == "__main__":
    unittest.main()
