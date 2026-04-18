from __future__ import annotations

import unittest

from src.adapters.intrigue.in_memory import InMemoryIntrigueGateway
from src.application.intrigue_use_cases import CollecterRenseignement, DiffuserRumeur, LancerOperation, ResoudreSabotage
from src.domain.intrigue import Agent, Cellule, NiveauAlerte, OperationClandestine, TypeOperation, calculer_risque, lancer_operation
from src.world.generator import generate_world


class IntrigueUseCaseTests(unittest.TestCase):
    def _build_world_with_cell(self):
        world = generate_world(width=12, height=8, civ_count=3)
        world.civilizations[0].industry = 10.0
        world.civilizations[0].stability = 10.0
        world.civilizations[0].knowledge = 0.0
        world.civilizations[0].influence = 0.0
        world.civilizations[1].industry = 10.0
        world.civilizations[1].stability = 10.0
        world.civilizations[1].military = 10.0
        world.intrigue.cellules["delta-0"] = Cellule(
            code="delta-0",
            faction_id=0,
            region="Aster Prime:4,4",
            agents=[
                Agent(code="a0", faction_id=0, stealth=1.4, cover=1.2, loyalty=1.0),
                Agent(code="a1", faction_id=0, stealth=1.1, cover=1.0, loyalty=0.95),
            ],
        )
        return world

    def test_risk_increases_with_heat(self) -> None:
        low_heat = Cellule(code="cold", faction_id=0, region="north", agents=[Agent(code="a", faction_id=0)], heat=0.5)
        high_heat = Cellule(code="hot", faction_id=0, region="north", agents=[Agent(code="a", faction_id=0)], heat=6.0)
        operation = OperationClandestine(
            code="op-1",
            type_operation=TypeOperation.SABOTAGE,
            source_faction_id=0,
            target_faction_id=1,
            target_region="frontier",
            preparation=1.0,
            risk_base=0.3,
            intensity=1.0,
        )

        self.assertGreater(calculer_risque(high_heat, operation, target_security=5.0), calculer_risque(low_heat, operation, target_security=5.0))

    def test_detected_operation_can_expose_network(self) -> None:
        cell = Cellule(
            code="delta-0",
            faction_id=0,
            region="Aster Prime:4,4",
            agents=[Agent(code="a", faction_id=0, stealth=0.7, cover=0.6)],
            heat=5.2,
        )
        operation = OperationClandestine(
            code="sabotage-test",
            type_operation=TypeOperation.SABOTAGE,
            source_faction_id=0,
            target_faction_id=1,
            target_region="Boreal Prime:6,4",
            preparation=0.6,
            risk_base=0.45,
            intensity=1.2,
        )

        report = lancer_operation(
            cell,
            operation,
            target_security=7.0,
            success_roll=0.9,
            detection_roll=0.01,
        )

        self.assertTrue(report.detected)
        self.assertTrue(cell.exposed)
        self.assertEqual(report.alert_level, NiveauAlerte.EXPOSE)

    def test_resoudre_sabotage_reduces_target_resources_and_emits_events(self) -> None:
        world = self._build_world_with_cell()
        gateway = InMemoryIntrigueGateway(world, random_values=[0.05, 0.99])
        launcher = LancerOperation(gateway, gateway, gateway, gateway, gateway)
        sabotage = ResoudreSabotage(launcher, gateway, gateway)

        before_industry = world.civilizations[1].industry
        before_stability = world.civilizations[1].stability
        report = sabotage.execute("delta-0", target_faction_id=1, target_region="Boreal Prime:6,4", preparation=1.2, intensity=1.1)

        self.assertTrue(report.success)
        self.assertLess(world.civilizations[1].industry, before_industry)
        self.assertLess(world.civilizations[1].stability, before_stability)
        self.assertEqual(gateway.events[-1]["event_name"], "sabotage_resolu")

    def test_collecter_renseignement_and_diffuser_rumeur_update_world_state(self) -> None:
        world = self._build_world_with_cell()
        gateway = InMemoryIntrigueGateway(world, random_values=[0.05, 0.99, 0.05, 0.99])
        launcher = LancerOperation(gateway, gateway, gateway, gateway, gateway)
        intel = CollecterRenseignement(launcher, gateway, gateway, gateway)
        rumor = DiffuserRumeur(launcher, gateway, gateway, gateway, gateway)

        intel.execute("delta-0", target_faction_id=1, target_region="Boreal Prime:6,4", preparation=1.2)
        rumor.execute("delta-0", target_faction_id=1, message="La cour de Boreal vacille.", preparation=1.1)

        self.assertGreater(world.civilizations[0].knowledge, 0.0)
        self.assertGreater(world.intrigue.intel_points[0], 0.0)
        self.assertEqual(len(world.intrigue.rumeurs), 1)
        self.assertLess(world.civilizations[1].stability, 10.0)
        self.assertEqual(gateway.events[-1]["event_name"], "rumeur_diffusee")


if __name__ == "__main__":
    unittest.main()
