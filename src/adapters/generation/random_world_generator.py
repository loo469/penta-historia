from __future__ import annotations

from src.domain.model import WorldState
from src.world.generator import generate_world


class RandomWorldGeneratorAdapter:
    def generate(self, width: int = 28, height: int = 18, civ_count: int = 4) -> WorldState:
        return generate_world(width=width, height=height, civ_count=civ_count)

