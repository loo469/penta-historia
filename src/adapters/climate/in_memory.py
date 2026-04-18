from __future__ import annotations

from statistics import mean

from src.domain.climate import Catastrophe, CityClimateEffect, CitySnapshot, ClimateState, Myth, RegionSnapshot
from src.domain.model import WorldState


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


class InMemoryClimateRepository:
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def load(self) -> ClimateState:
        return self.world.climate

    def save(self, climate_state: ClimateState) -> None:
        self.world.climate = climate_state


class WorldStateReadAdapter:
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def get_world(self) -> WorldState:
        return self.world

    def get_region_snapshots(self) -> list[RegionSnapshot]:
        if self.world.height <= 0 or self.world.width <= 0:
            return []

        bands = {
            "north": {"lat": 0.18, "fertility": [], "cities": 0, "tension": []},
            "heartland": {"lat": 0.5, "fertility": [], "cities": 0, "tension": []},
            "south": {"lat": 0.82, "fertility": [], "cities": 0, "tension": []},
        }

        for y, row in enumerate(self.world.fertility):
            band_key = self._region_for_y(y)
            bands[band_key]["fertility"].extend(row)

        for city in self.world.cities:
            band_key = self._region_for_y(city.y)
            bands[band_key]["cities"] += 1
            civ = self.world.civilizations[city.civ_id]
            bands[band_key]["tension"].append(_clamp(1.0 - civ.stability / 20.0, 0.05, 0.95))

        snapshots: list[RegionSnapshot] = []
        global_tension = mean(_clamp(1.0 - civ.stability / 20.0, 0.05, 0.95) for civ in self.world.civilizations.values())
        for region_key, values in bands.items():
            fertility_values = values["fertility"]
            if not fertility_values:
                continue
            snapshots.append(
                RegionSnapshot(
                    region_key=region_key,
                    latitude=values["lat"],
                    average_fertility=mean(fertility_values),
                    city_count=values["cities"],
                    tension=mean(values["tension"]) if values["tension"] else global_tension,
                )
            )
        return snapshots

    def get_city_snapshots(self) -> list[CitySnapshot]:
        return [
            CitySnapshot(
                city_name=city.name,
                civ_id=city.civ_id,
                region_key=self._region_for_y(city.y),
                population=city.population,
                storage=city.storage,
                x=city.x,
                y=city.y,
            )
            for city in self.world.cities
        ]

    def _region_for_y(self, y: int) -> str:
        ratio = (y + 0.5) / max(1, self.world.height)
        if ratio < 1 / 3:
            return "north"
        if ratio < 2 / 3:
            return "heartland"
        return "south"


class WorldStateEventAdapter:
    def __init__(self, world: WorldState) -> None:
        self.world = world
        self.world_reader = WorldStateReadAdapter(world)

    def record_world_event(self, message: str) -> None:
        self.world.log.append(message)

    def apply_catastrophe(self, catastrophe: Catastrophe) -> None:
        affected_civs: set[int] = set()
        for city in self.world.cities:
            if self.world_reader._region_for_y(city.y) != catastrophe.region_key:
                continue
            affected_civs.add(city.civ_id)
            city.population = max(1.0, city.population * (1.0 - catastrophe.stability_impact * 0.08))
            city.storage = max(0.0, city.storage - catastrophe.fertility_impact * 1.5)

        for civ_id in affected_civs:
            civ = self.world.civilizations[civ_id]
            civ.food = max(0.0, civ.food - catastrophe.fertility_impact * 1.4)
            civ.stability = max(0.0, civ.stability - catastrophe.stability_impact * 1.1)

        self.record_world_event(catastrophe.description)


class WorldStateClimateEffectsAdapter:
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def apply_city_climate_effects(self, effects: list[CityClimateEffect]) -> None:
        if not effects:
            return

        cities_by_name = {city.name: city for city in self.world.cities}
        civ_stability_delta: dict[int, float] = {}
        migration_logs: list[str] = []

        for effect in effects:
            city = cities_by_name.get(effect.city_name)
            if city is None:
                continue
            city.climate_output_modifier = effect.output_modifier
            city.migration_pressure = effect.migration_pressure
            city.storage = max(0.0, city.storage + effect.storage_delta)
            city.population = max(1.0, city.population - effect.migrants_out)

            if effect.target_city_name is not None and effect.migrants_in > 0:
                target_city = cities_by_name.get(effect.target_city_name)
                if target_city is not None:
                    target_city.population += effect.migrants_in
                    migration_logs.append(
                        f"{effect.migrants_in:.1f} habitants quittent {city.name} vers {target_city.name} sous la pression du climat."
                    )

            civ_stability_delta[city.civ_id] = civ_stability_delta.get(city.civ_id, 0.0) + effect.stability_delta

        for civ_id, delta in civ_stability_delta.items():
            civ = self.world.civilizations[civ_id]
            civ.stability = _clamp(civ.stability + delta, 0.0, 20.0)

        for entry in migration_logs[:3]:
            self.world.log.append(entry)


class InMemoryMythLedger:
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def record(self, myth: Myth) -> None:
        self.world.log.append(f"Le mythe '{myth.title}' prend racine dans la mémoire du monde.")
