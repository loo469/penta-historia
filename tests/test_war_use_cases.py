from __future__ import annotations

import unittest

from src.adapters.persistence.in_memory_war import (
    InMemoryFactionStateRepository,
    InMemoryMapRepository,
    WorldStateBattleResolver,
    WorldStateEventBus,
)
from src.application.war_use_cases import DetectFronts, ExpandTerritory, ResolveBorderPressure, StabilizeCapturedProvince
from src.domain.model import Civilization, ClimateState, WorldState


class WarUseCasesTests(unittest.TestCase):
    def _build_world(self) -> WorldState:
        return WorldState(
            width=4,
            height=3,
            owners=[
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            fertility=[
                [1.0, 1.0, 0.9, 0.9],
                [1.0, 1.0, 0.9, 0.9],
                [1.0, 1.0, 0.9, 0.9],
            ],
            civilizations={
                0: Civilization(civ_id=0, name="Aster", color=(220, 90, 90), military=18.0, industry=13.0, stability=12.0, food=11.0, influence=4.0),
                1: Civilization(civ_id=1, name="Boreal", color=(90, 170, 240), military=6.0, industry=7.0, stability=8.0, food=8.0, influence=1.0),
            },
            cities=[],
            climate=ClimateState(),
        )

    def test_detect_fronts_builds_bidirectional_border_lines(self) -> None:
        world = self._build_world()
        map_repository = InMemoryMapRepository(world)
        faction_state_repository = InMemoryFactionStateRepository(world, map_repository)

        fronts = DetectFronts(map_repository, faction_state_repository).execute()

        self.assertEqual({(front.attacker, front.defender) for front in fronts}, {(0, 1), (1, 0)})
        self.assertTrue(all(front.length == 3 for front in fronts))

    def test_resolve_border_pressure_prefers_stronger_faction(self) -> None:
        world = self._build_world()
        map_repository = InMemoryMapRepository(world)
        faction_state_repository = InMemoryFactionStateRepository(world, map_repository)
        battle_resolver = WorldStateBattleResolver(world)

        fronts = ResolveBorderPressure(map_repository, faction_state_repository, battle_resolver).execute()
        pressures = {(front.attacker, front.defender): front.pressure for front in fronts}

        self.assertGreater(pressures[(0, 1)], pressures[(1, 0)])
        self.assertGreater(pressures[(0, 1)], 0.58)

    def test_expand_and_stabilize_captured_province(self) -> None:
        world = self._build_world()
        map_repository = InMemoryMapRepository(world)
        faction_state_repository = InMemoryFactionStateRepository(world, map_repository)
        battle_resolver = WorldStateBattleResolver(world)
        event_bus = WorldStateEventBus(world)

        captured = ExpandTerritory(
            map_repository=map_repository,
            faction_state_repository=faction_state_repository,
            battle_resolver=battle_resolver,
            event_bus=event_bus,
        ).execute(faction_id=0)

        self.assertIsNotNone(captured)
        assert captured is not None
        self.assertEqual(captured.owner, 0)
        self.assertEqual(world.owners[captured.y][captured.x], 0)
        self.assertTrue(captured.contested)
        self.assertIn("prend une province", world.log[-1])

        stabilize = StabilizeCapturedProvince(
            map_repository=map_repository,
            faction_state_repository=faction_state_repository,
            event_bus=event_bus,
        )
        stabilize.execute()
        provinces_after_first_tick = {province.coord: province for province in map_repository.list_provinces()}
        self.assertTrue(provinces_after_first_tick[captured.coord].contested)

        stabilize.execute()
        provinces_after_second_tick = {province.coord: province for province in map_repository.list_provinces()}
        self.assertFalse(provinces_after_second_tick[captured.coord].contested)
        self.assertTrue(any("stabilise l'arrière" in entry for entry in world.log))


if __name__ == "__main__":
    unittest.main()
