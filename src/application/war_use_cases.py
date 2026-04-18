from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from src.application.ports import BattleResolverPort, FactionStateRepository, MapRepository, WorldEventBus
from src.domain.war import (
    FactionTerritory,
    Front,
    Province,
    SupplyLevel,
    build_faction_territories,
    detect_fronts,
    expand_territory,
    resolve_border_pressure,
    stabilize_captured_province,
)


class DetectFronts:
    def __init__(
        self,
        map_repository: MapRepository,
        faction_state_repository: FactionStateRepository,
    ) -> None:
        self.map_repository = map_repository
        self.faction_state_repository = faction_state_repository

    def execute(self) -> list[Front]:
        provinces = self.map_repository.list_provinces()
        territories = build_faction_territories(provinces)
        self.faction_state_repository.save_faction_territories(territories)
        return detect_fronts(provinces, territories)


class ResolveBorderPressure:
    def __init__(
        self,
        map_repository: MapRepository,
        faction_state_repository: FactionStateRepository,
        battle_resolver: BattleResolverPort,
    ) -> None:
        self.map_repository = map_repository
        self.faction_state_repository = faction_state_repository
        self.battle_resolver = battle_resolver

    def execute(self) -> list[Front]:
        provinces = self.map_repository.list_provinces()
        territories = build_faction_territories(provinces)
        detected_fronts = detect_fronts(provinces, territories)

        pressure_by_faction: dict[int, list[float]] = defaultdict(list)
        resolved_fronts: list[Front] = []
        for front in detected_fronts:
            attacker_territory = territories[front.attacker]
            defender_territory = territories[front.defender]
            attacker_strength = attacker_territory.province_count * attacker_territory.supply_level.multiplier
            attacker_strength += attacker_territory.average_stability * 2.5
            defender_strength = defender_territory.province_count * defender_territory.supply_level.multiplier
            defender_strength += defender_territory.average_stability * 2.5
            advantage = self.battle_resolver.resolve_advantage(front, territories)
            pressure = resolve_border_pressure(front, attacker_strength, defender_strength, advantage)
            resolved_front = replace(front, pressure=pressure)
            resolved_fronts.append(resolved_front)
            pressure_by_faction[front.attacker].append(pressure)

        updated_territories: dict[int, FactionTerritory] = {}
        for faction_id, territory in territories.items():
            pressures = pressure_by_faction.get(faction_id, [])
            updated_territories[faction_id] = replace(
                territory,
                front_pressure=sum(pressures) / len(pressures) if pressures else 0.0,
            )

        self.faction_state_repository.save_faction_territories(updated_territories)
        return resolved_fronts


class ExpandTerritory:
    def __init__(
        self,
        map_repository: MapRepository,
        faction_state_repository: FactionStateRepository,
        battle_resolver: BattleResolverPort,
        event_bus: WorldEventBus,
    ) -> None:
        self.map_repository = map_repository
        self.faction_state_repository = faction_state_repository
        self.battle_resolver = battle_resolver
        self.event_bus = event_bus

    def execute(self, faction_id: int | None = None) -> Province | None:
        provinces = self.map_repository.list_provinces()
        territories = build_faction_territories(provinces)
        fronts = detect_fronts(provinces, territories)
        if faction_id is not None:
            fronts = [front for front in fronts if front.attacker == faction_id]
        if not fronts:
            self.faction_state_repository.save_faction_territories(territories)
            return None

        resolved_fronts: list[Front] = []
        for front in fronts:
            attacker_territory = territories[front.attacker]
            defender_territory = territories[front.defender]
            attacker_strength = attacker_territory.province_count * attacker_territory.supply_level.multiplier
            attacker_strength += attacker_territory.average_stability * 2.5
            defender_strength = defender_territory.province_count * defender_territory.supply_level.multiplier
            defender_strength += defender_territory.average_stability * 2.5
            advantage = self.battle_resolver.resolve_advantage(front, territories)
            resolved_fronts.append(
                replace(front, pressure=resolve_border_pressure(front, attacker_strength, defender_strength, advantage))
            )

        chosen_front = max(resolved_fronts, key=lambda front: (front.pressure, front.length, -front.defender))
        captured = expand_territory(chosen_front, provinces)
        if captured is None:
            self.faction_state_repository.save_faction_territories(territories)
            return None

        updated_provinces = [captured if province.coord == captured.coord else province for province in provinces]
        self.map_repository.save_provinces(updated_provinces)
        updated_territories = build_faction_territories(updated_provinces)
        self.faction_state_repository.save_faction_territories(updated_territories)
        self.event_bus.publish(
            "ProvinceCaptured",
            {
                "attacker": chosen_front.attacker,
                "defender": chosen_front.defender,
                "coord": captured.coord,
                "pressure": round(chosen_front.pressure, 3),
            },
        )
        return captured


class StabilizeCapturedProvince:
    def __init__(
        self,
        map_repository: MapRepository,
        faction_state_repository: FactionStateRepository,
        event_bus: WorldEventBus,
    ) -> None:
        self.map_repository = map_repository
        self.faction_state_repository = faction_state_repository
        self.event_bus = event_bus

    def execute(self) -> list[Province]:
        provinces = self.map_repository.list_provinces()
        territories = build_faction_territories(provinces)
        updated_provinces: list[Province] = []
        changed = False

        for province in provinces:
            territory = territories.get(province.owner) if province.owner is not None else None
            should_stabilize = province.owner is not None and (province.contested or province.turns_since_capture < 3)
            if territory is None or not should_stabilize:
                updated_provinces.append(province)
                continue

            stabilized = stabilize_captured_province(province, territory.supply_level)
            if stabilized != province:
                changed = True
                if province.contested and not stabilized.contested:
                    self.event_bus.publish(
                        "FrontStabilized",
                        {
                            "owner": stabilized.owner,
                            "coord": stabilized.coord,
                            "turns": stabilized.turns_since_capture,
                        },
                    )
            updated_provinces.append(stabilized)

        if changed:
            self.map_repository.save_provinces(updated_provinces)
            self.faction_state_repository.save_faction_territories(build_faction_territories(updated_provinces))
        else:
            self.faction_state_repository.save_faction_territories(territories)
        return updated_provinces
