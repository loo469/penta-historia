from __future__ import annotations

from src.domain.council import apply_suggestion, build_suggestions
from src.domain.model import Suggestion, WorldState


class DefaultCouncilAdapter:
    def build_suggestions(self, world: WorldState) -> list[Suggestion]:
        return build_suggestions(world)

    def apply_suggestion(self, world: WorldState, effect_key: str) -> None:
        apply_suggestion(world, effect_key)
