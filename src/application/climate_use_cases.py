from __future__ import annotations

from statistics import mean

from src.application.ports import ClimateRepositoryPort, MythLedgerPort, WorldEventPort, WorldReadPort
from src.domain.climate import Catastrophe, ClimateState, Myth, RegionClimateProfile


SEASON_TEMPERATURE_SHIFT = {
    "Printemps": 0.02,
    "Été": 0.18,
    "Automne": -0.04,
    "Hiver": -0.22,
}

SEASON_FERTILITY_SHIFT = {
    "Printemps": 0.05,
    "Été": 0.1,
    "Automne": 0.0,
    "Hiver": -0.14,
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _derive_anomaly(season_name: str, avg_temp: float, avg_humidity: float, avg_wind: float, avg_tension: float) -> str:
    if season_name == "Été" and avg_temp > 0.69 and avg_humidity < 0.4:
        return "dry"
    if avg_humidity > 0.62 and avg_wind > 0.56:
        return "storm"
    if season_name == "Hiver" and avg_wind > 0.58:
        return "frost"
    if avg_tension > 0.62 and avg_temp > 0.64:
        return "omen"
    return "stable"


class AdvanceSeasons:
    def __init__(self, climate_repository: ClimateRepositoryPort, world_events: WorldEventPort | None = None) -> None:
        self.climate_repository = climate_repository
        self.world_events = world_events

    def execute(self, turns: int = 1) -> ClimateState:
        climate = self.climate_repository.load()
        previous_season = climate.season_name
        previous_year = climate.year
        climate.season_cycle.advance(turns=turns)
        self.climate_repository.save(climate)

        if self.world_events is not None and (climate.season_name != previous_season or climate.year != previous_year):
            self.world_events.record_world_event(
                f"Le cycle passe en {climate.season_name} de l'an {climate.year}."
            )
        return climate


class UpdateRegionalClimate:
    def __init__(
        self,
        climate_repository: ClimateRepositoryPort,
        world_reader: WorldReadPort,
        world_events: WorldEventPort | None = None,
    ) -> None:
        self.climate_repository = climate_repository
        self.world_reader = world_reader
        self.world_events = world_events

    def execute(self) -> ClimateState:
        climate = self.climate_repository.load()
        snapshots = self.world_reader.get_region_snapshots()
        if not snapshots:
            return climate

        raw_profiles: list[RegionClimateProfile] = []
        for snapshot in snapshots:
            latitude_distance = abs(snapshot.latitude - 0.5)
            temperature = 0.58 + SEASON_TEMPERATURE_SHIFT[climate.season_name] - latitude_distance * 0.24
            humidity = 0.22 + snapshot.average_fertility * 0.28 + snapshot.city_count * 0.02
            wind = 0.26 + latitude_distance * 0.44 + snapshot.tension * 0.2
            raw_profiles.append(
                RegionClimateProfile(
                    region_key=snapshot.region_key,
                    latitude=snapshot.latitude,
                    average_fertility=snapshot.average_fertility,
                    city_count=snapshot.city_count,
                    tension=snapshot.tension,
                    temperature=_clamp(temperature, 0.15, 1.0),
                    humidity=_clamp(humidity, 0.15, 1.0),
                    wind=_clamp(wind, 0.1, 1.0),
                )
            )

        avg_temp = mean(profile.temperature for profile in raw_profiles)
        avg_humidity = mean(profile.humidity for profile in raw_profiles)
        avg_wind = mean(profile.wind for profile in raw_profiles)
        avg_tension = mean(profile.tension for profile in raw_profiles)

        previous_anomaly = climate.anomaly
        climate.anomaly = _derive_anomaly(
            season_name=climate.season_name,
            avg_temp=avg_temp,
            avg_humidity=avg_humidity,
            avg_wind=avg_wind,
            avg_tension=avg_tension,
        )

        region_profiles: dict[str, RegionClimateProfile] = {}
        for profile in raw_profiles:
            temperature = profile.temperature
            humidity = profile.humidity
            wind = profile.wind
            fertility_modifier = 0.82 + SEASON_FERTILITY_SHIFT[climate.season_name]
            fertility_modifier += humidity * 0.22
            fertility_modifier -= max(0.0, temperature - 0.72) * 0.3
            fertility_modifier -= profile.tension * 0.08

            if climate.anomaly == "dry":
                humidity -= 0.14
                fertility_modifier *= 0.88
            elif climate.anomaly == "storm":
                humidity += 0.12
                wind += 0.12
                fertility_modifier *= 0.94
            elif climate.anomaly == "frost":
                temperature -= 0.14
                wind += 0.08
                fertility_modifier *= 0.86
            elif climate.anomaly == "omen":
                wind += 0.06
                fertility_modifier *= 0.97

            profile.temperature = _clamp(temperature, 0.1, 1.0)
            profile.humidity = _clamp(humidity, 0.1, 1.0)
            profile.wind = _clamp(wind, 0.1, 1.0)
            profile.fertility_modifier = _clamp(fertility_modifier, 0.55, 1.35)
            region_profiles[profile.region_key] = profile

        climate.region_profiles = region_profiles
        climate.global_temperature = mean(profile.temperature for profile in region_profiles.values())
        climate.global_humidity = mean(profile.humidity for profile in region_profiles.values())
        climate.global_wind = mean(profile.wind for profile in region_profiles.values())
        climate.fertility_modifier = mean(profile.fertility_modifier for profile in region_profiles.values())
        self.climate_repository.save(climate)

        if self.world_events is not None and climate.anomaly != previous_anomaly:
            self.world_events.record_world_event(f"Le climat bascule vers l'anomalie {climate.anomaly}.")
        return climate


class TriggerCatastrophe:
    def __init__(
        self,
        climate_repository: ClimateRepositoryPort,
        world_reader: WorldReadPort,
        world_events: WorldEventPort,
    ) -> None:
        self.climate_repository = climate_repository
        self.world_reader = world_reader
        self.world_events = world_events

    def execute(self, min_severity: float = 0.6) -> Catastrophe | None:
        climate = self.climate_repository.load()
        if not climate.region_profiles:
            return None

        catastrophe: Catastrophe | None = None
        for profile in climate.region_profiles.values():
            candidate = self._build_candidate(climate, profile)
            if candidate is None:
                continue
            if catastrophe is None or candidate.severity > catastrophe.severity:
                catastrophe = candidate

        if catastrophe is None or catastrophe.severity < min_severity:
            return None

        if any(
            existing.kind == catastrophe.kind
            and existing.region_key == catastrophe.region_key
            and existing.year == catastrophe.year
            and existing.season_name == catastrophe.season_name
            for existing in climate.active_catastrophes
        ):
            return None

        climate.remember_catastrophe(catastrophe)
        climate.fertility_modifier = _clamp(climate.fertility_modifier * (1.0 - catastrophe.fertility_impact * 0.12), 0.45, 1.35)
        self.climate_repository.save(climate)
        self.world_events.apply_catastrophe(catastrophe)
        return catastrophe

    def _build_candidate(self, climate: ClimateState, profile: RegionClimateProfile) -> Catastrophe | None:
        if climate.anomaly == "dry":
            severity = (0.7 - profile.humidity) + (profile.temperature - 0.68) + profile.tension * 0.25
            if severity <= 0:
                return None
            return Catastrophe(
                kind="sécheresse",
                region_key=profile.region_key,
                season_name=climate.season_name,
                year=climate.year,
                severity=round(severity, 2),
                fertility_impact=0.35,
                stability_impact=0.25,
                description=f"Une sécheresse frappe la région {profile.region_key}.",
            )

        if climate.anomaly == "storm":
            severity = (profile.humidity - 0.55) + (profile.wind - 0.45) + profile.tension * 0.2
            if severity <= 0:
                return None
            return Catastrophe(
                kind="crue",
                region_key=profile.region_key,
                season_name=climate.season_name,
                year=climate.year,
                severity=round(severity, 2),
                fertility_impact=0.25,
                stability_impact=0.2,
                description=f"Une crue ravage la région {profile.region_key}.",
            )

        if climate.anomaly == "frost":
            severity = (0.55 - profile.temperature) + (profile.wind - 0.4) + profile.tension * 0.18
            if severity <= 0:
                return None
            return Catastrophe(
                kind="gel meurtrier",
                region_key=profile.region_key,
                season_name=climate.season_name,
                year=climate.year,
                severity=round(severity, 2),
                fertility_impact=0.3,
                stability_impact=0.18,
                description=f"Un gel meurtrier mord la région {profile.region_key}.",
            )

        return None


class RegisterMythFromEvent:
    def __init__(
        self,
        climate_repository: ClimateRepositoryPort,
        myth_ledger: MythLedgerPort,
        world_events: WorldEventPort | None = None,
    ) -> None:
        self.climate_repository = climate_repository
        self.myth_ledger = myth_ledger
        self.world_events = world_events

    def from_catastrophe(self, catastrophe: Catastrophe) -> Myth:
        climate = self.climate_repository.load()
        title = {
            "sécheresse": "Le Soleil avare",
            "crue": "Les Eaux sans bride",
            "gel meurtrier": "Le Souffle blanc",
        }.get(catastrophe.kind, "Le Signe oublié")
        myth = Myth(
            title=title,
            description=f"Les chroniqueurs racontent {catastrophe.description.lower()}",
            source_event=catastrophe.description,
            season_name=climate.season_name,
            year=climate.year,
            intensity=catastrophe.severity,
            region_key=catastrophe.region_key,
        )
        climate.remember_myth(myth)
        self.climate_repository.save(climate)
        self.myth_ledger.record(myth)
        if self.world_events is not None:
            self.world_events.record_world_event(f"Le mythe '{myth.title}' se répand depuis {myth.region_key}.")
        return myth
