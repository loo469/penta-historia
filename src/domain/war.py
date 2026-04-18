from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from enum import Enum


Coordinate = tuple[int, int]


class SupplyLevel(str, Enum):
    CUT_OFF = "cut_off"
    STRAINED = "strained"
    STABLE = "stable"
    SECURED = "secured"

    @property
    def multiplier(self) -> float:
        return {
            SupplyLevel.CUT_OFF: 0.55,
            SupplyLevel.STRAINED: 0.8,
            SupplyLevel.STABLE: 1.0,
            SupplyLevel.SECURED: 1.2,
        }[self]

    @classmethod
    def from_ratio(cls, ratio: float) -> "SupplyLevel":
        if ratio < 0.55:
            return cls.CUT_OFF
        if ratio < 0.85:
            return cls.STRAINED
        if ratio < 1.1:
            return cls.STABLE
        return cls.SECURED


@dataclass(frozen=True, slots=True)
class Province:
    x: int
    y: int
    owner: int | None
    fertility: float
    stability: float = 1.0
    garrison: float = 1.0
    supply: float = 1.0
    contested: bool = False
    turns_since_capture: int = 5

    @property
    def coord(self) -> Coordinate:
        return (self.x, self.y)


@dataclass(frozen=True, slots=True)
class BorderSegment:
    attacker: int
    defender: int
    from_coord: Coordinate
    to_coord: Coordinate


@dataclass(frozen=True, slots=True)
class FactionTerritory:
    faction_id: int
    province_count: int
    supply_level: SupplyLevel
    average_stability: float
    front_pressure: float = 0.0
    captured_provinces: int = 0


@dataclass(frozen=True, slots=True)
class Front:
    attacker: int
    defender: int
    segments: tuple[BorderSegment, ...]
    pressure: float
    supply_level: SupplyLevel

    @property
    def length(self) -> int:
        return len(self.segments)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def build_faction_territories(provinces: list[Province]) -> dict[int, FactionTerritory]:
    grouped: dict[int, list[Province]] = defaultdict(list)
    for province in provinces:
        if province.owner is not None:
            grouped[province.owner].append(province)

    territories: dict[int, FactionTerritory] = {}
    for faction_id, faction_provinces in grouped.items():
        average_supply = sum(province.supply for province in faction_provinces) / len(faction_provinces)
        average_stability = sum(province.stability for province in faction_provinces) / len(faction_provinces)
        captured_count = sum(1 for province in faction_provinces if province.turns_since_capture < 3)
        territories[faction_id] = FactionTerritory(
            faction_id=faction_id,
            province_count=len(faction_provinces),
            supply_level=SupplyLevel.from_ratio(average_supply),
            average_stability=average_stability,
            captured_provinces=captured_count,
        )
    return territories


def detect_fronts(
    provinces: list[Province],
    territories: dict[int, FactionTerritory],
) -> list[Front]:
    province_map = {province.coord: province for province in provinces}
    grouped_segments: dict[tuple[int, int], list[BorderSegment]] = defaultdict(list)

    for province in provinces:
        if province.owner is None:
            continue
        for dx, dy in ((1, 0), (0, 1)):
            other = province_map.get((province.x + dx, province.y + dy))
            if other is None or other.owner is None or other.owner == province.owner:
                continue
            grouped_segments[(province.owner, other.owner)].append(
                BorderSegment(
                    attacker=province.owner,
                    defender=other.owner,
                    from_coord=province.coord,
                    to_coord=other.coord,
                )
            )
            grouped_segments[(other.owner, province.owner)].append(
                BorderSegment(
                    attacker=other.owner,
                    defender=province.owner,
                    from_coord=other.coord,
                    to_coord=province.coord,
                )
            )

    fronts: list[Front] = []
    for (attacker, defender), segments in grouped_segments.items():
        attacker_territory = territories.get(attacker)
        defender_territory = territories.get(defender)
        if attacker_territory is None or defender_territory is None:
            continue

        base_pressure = 0.48
        base_pressure += (attacker_territory.province_count - defender_territory.province_count) * 0.008
        base_pressure += (attacker_territory.supply_level.multiplier - defender_territory.supply_level.multiplier) * 0.18
        base_pressure += (attacker_territory.average_stability - defender_territory.average_stability) * 0.12
        base_pressure -= attacker_territory.captured_provinces * 0.04
        base_pressure += min(0.08, len(segments) * 0.01)

        fronts.append(
            Front(
                attacker=attacker,
                defender=defender,
                segments=tuple(segments),
                pressure=clamp(base_pressure),
                supply_level=attacker_territory.supply_level,
            )
        )

    fronts.sort(key=lambda front: (front.attacker, front.defender, -front.pressure))
    return fronts


def resolve_border_pressure(
    front: Front,
    attacker_strength: float,
    defender_strength: float,
    battle_advantage: float,
) -> float:
    delta = (attacker_strength - defender_strength) / max(8.0, attacker_strength + defender_strength)
    pressure = front.pressure
    pressure += delta * 0.4
    pressure += battle_advantage * 0.35
    pressure += (front.supply_level.multiplier - 1.0) * 0.2
    pressure += min(0.06, front.length * 0.008)
    return clamp(pressure)


def expand_territory(front: Front, provinces: list[Province]) -> Province | None:
    if front.pressure < 0.58:
        return None

    province_map = {province.coord: province for province in provinces}
    candidates: list[Province] = []
    seen: set[Coordinate] = set()
    for segment in front.segments:
        candidate = province_map.get(segment.to_coord)
        if candidate is None or candidate.owner != front.defender or candidate.coord in seen:
            continue
        seen.add(candidate.coord)
        candidates.append(candidate)

    if not candidates:
        return None

    target = min(
        candidates,
        key=lambda province: (
            province.stability + province.garrison * 0.55 + province.supply * 0.35 - province.fertility * 0.05,
            province.y,
            province.x,
        ),
    )
    return replace(
        target,
        owner=front.attacker,
        contested=True,
        stability=max(0.22, target.stability * 0.45),
        garrison=max(0.35, target.garrison * 0.6),
        supply=0.4,
        turns_since_capture=0,
    )


def stabilize_captured_province(province: Province, supply_level: SupplyLevel) -> Province:
    if province.owner is None:
        return province

    stability_gain = 0.09 * supply_level.multiplier
    supply_gain = 0.11 * supply_level.multiplier
    garrison_gain = 0.05 * supply_level.multiplier

    new_stability = clamp(province.stability + stability_gain)
    new_supply = clamp(province.supply + supply_gain)
    new_garrison = clamp(province.garrison + garrison_gain)
    new_turns = province.turns_since_capture + 1
    stabilized = new_turns >= 2 and new_stability >= 0.55 and new_supply >= 0.55

    return replace(
        province,
        stability=new_stability,
        supply=new_supply,
        garrison=new_garrison,
        contested=province.contested and not stabilized,
        turns_since_capture=new_turns,
    )
