from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Territory:
    x: int
    y: int
    owner: int | None
    stability: float = 1.0
    garrison: float = 1.0
    supply: float = 1.0


@dataclass
class Front:
    attacker: int
    defender: int
    x: int
    y: int
    pressure: float = 0.0
    supply_ratio: float = 1.0


def find_fronts(owners: list[list[int | None]]) -> list[Front]:
    fronts: list[Front] = []
    height = len(owners)
    width = len(owners[0]) if height else 0
    for y in range(height):
        for x in range(width):
            owner = owners[y][x]
            if owner is None:
                continue
            for nx, ny in ((x + 1, y), (x, y + 1)):
                if nx >= width or ny >= height:
                    continue
                other = owners[ny][nx]
                if other is not None and other != owner:
                    fronts.append(Front(attacker=owner, defender=other, x=x, y=y, pressure=0.5))
    return fronts


def stabilize_rear(territory: Territory) -> None:
    territory.stability = min(2.0, territory.stability + 0.05)
    territory.supply = min(2.0, territory.supply + 0.03)
