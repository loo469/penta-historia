from __future__ import annotations

from dataclasses import dataclass, field


SEASONS = ("Printemps", "Été", "Automne", "Hiver")


@dataclass
class SeasonCycle:
    season_index: int = 0
    year: int = 1
    turns_per_season: int = 1
    turn_in_season: int = 0

    @property
    def season_name(self) -> str:
        return SEASONS[self.season_index % len(SEASONS)]

    def advance(self, turns: int = 1) -> None:
        for _ in range(max(0, turns)):
            self.turn_in_season += 1
            if self.turn_in_season >= self.turns_per_season:
                self.turn_in_season = 0
                self.season_index = (self.season_index + 1) % len(SEASONS)
                if self.season_index == 0:
                    self.year += 1


@dataclass(frozen=True)
class RegionSnapshot:
    region_key: str
    latitude: float
    average_fertility: float
    city_count: int
    tension: float


@dataclass
class RegionClimateProfile:
    region_key: str
    latitude: float
    average_fertility: float
    city_count: int
    tension: float
    temperature: float = 0.5
    humidity: float = 0.5
    wind: float = 0.4
    fertility_modifier: float = 1.0


@dataclass(frozen=True)
class Catastrophe:
    kind: str
    region_key: str
    season_name: str
    year: int
    severity: float
    fertility_impact: float
    stability_impact: float
    description: str


@dataclass(frozen=True)
class Myth:
    title: str
    description: str
    source_event: str
    season_name: str
    year: int
    intensity: float
    region_key: str | None = None


@dataclass
class ClimateState:
    anomaly: str = "stable"
    fertility_modifier: float = 1.0
    season_cycle: SeasonCycle = field(default_factory=SeasonCycle)
    global_temperature: float = 0.5
    global_humidity: float = 0.5
    global_wind: float = 0.4
    region_profiles: dict[str, RegionClimateProfile] = field(default_factory=dict)
    active_catastrophes: list[Catastrophe] = field(default_factory=list)
    myths: list[Myth] = field(default_factory=list)

    @property
    def season_index(self) -> int:
        return self.season_cycle.season_index

    @season_index.setter
    def season_index(self, value: int) -> None:
        self.season_cycle.season_index = value

    @property
    def year(self) -> int:
        return self.season_cycle.year

    @year.setter
    def year(self, value: int) -> None:
        self.season_cycle.year = value

    @property
    def season_name(self) -> str:
        return self.season_cycle.season_name

    def remember_catastrophe(self, catastrophe: Catastrophe, limit: int = 8) -> None:
        self.active_catastrophes = [catastrophe, *self.active_catastrophes[: limit - 1]]

    def remember_myth(self, myth: Myth, limit: int = 12) -> None:
        self.myths = [myth, *self.myths[: limit - 1]]
