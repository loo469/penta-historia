from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ClimateSystem:
    temperature: float = 0.5
    humidity: float = 0.5
    wind: float = 0.5
    biomes: dict[str, float] = field(default_factory=dict)

    def apply_season(self, season: str) -> None:
        if season == "Été":
            self.temperature += 0.1
        elif season == "Hiver":
            self.temperature -= 0.1


@dataclass
class SeasonCycle:
    current_season: str = "Printemps"
    day_in_year: int = 1

    def advance(self, days: int = 1) -> None:
        self.day_in_year += days


@dataclass
class CatastropheEvent:
    kind: str
    severity: float


class CatastropheEngine:
    def roll_event(self) -> CatastropheEvent | None:
        return None


@dataclass
class MythSystem:
    myths: list[str] = field(default_factory=list)

    def record_event(self, text: str) -> None:
        self.myths.append(text)
