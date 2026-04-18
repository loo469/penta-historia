from __future__ import annotations

from src.application.ports import CouncilPort, SimulationRulesPort, WorldGeneratorPort
from src.domain.model import WorldState


class GameSessionService:
    def __init__(
        self,
        world_generator: WorldGeneratorPort,
        simulation_rules: SimulationRulesPort,
        council: CouncilPort,
    ) -> None:
        self.world_generator = world_generator
        self.simulation_rules = simulation_rules
        self.council = council

    def create_world(self, width: int = 28, height: int = 18, civ_count: int = 4) -> WorldState:
        world = self.world_generator.generate(width=width, height=height, civ_count=civ_count)
        world.suggestions = self.council.build_suggestions(world)
        return world

    def regenerate_world(self, world: WorldState | None = None) -> WorldState:
        if world is None:
            return self.create_world()
        return self.create_world(width=world.width, height=world.height, civ_count=len(world.civilizations))

    def advance_world(self, world: WorldState) -> None:
        self.simulation_rules.advance(world)
        world.suggestions = self.council.build_suggestions(world)

    def apply_player_choice(self, world: WorldState, suggestion_index: int) -> None:
        if 0 <= suggestion_index < len(world.suggestions):
            suggestion = world.suggestions[suggestion_index]
            self.council.apply_suggestion(world, suggestion.effect_key)
            world.suggestions = self.council.build_suggestions(world)

