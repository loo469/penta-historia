from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.domain.economy import ProductionRule, ResourceStock, ResourceType, TradeRoute


class AgentName(str, Enum):
    ALPHA = "Alpha"
    BETA = "Beta"
    GAMMA = "Gamma"
    DELTA = "Delta"
    EPSILON = "Epsilon"


@dataclass
class Civilization:
    civ_id: int
    name: str
    color: tuple[int, int, int]
    food: float = 10.0
    industry: float = 10.0
    knowledge: float = 0.0
    influence: float = 0.0
    stability: float = 10.0
    military: float = 10.0
    culture: float = 0.0


@dataclass
class City:
    name: str
    civ_id: int
    x: int
    y: int
    population: float = 10.0
    fertility: float = 1.0
    infrastructure: float = 1.0
    storage: float = 5.0
    stocks: dict[ResourceType, ResourceStock] = field(default_factory=dict)
    production_rules: list[ProductionRule] = field(default_factory=list)


@dataclass
class ClimateState:
    season_index: int = 0
    year: int = 1
    anomaly: str = "stable"
    fertility_modifier: float = 1.0

    @property
    def season_name(self) -> str:
        return ["Printemps", "Été", "Automne", "Hiver"][self.season_index % 4]


@dataclass
class Suggestion:
    agent: AgentName
    title: str
    description: str
    effect_key: str


@dataclass
class WorldState:
    width: int
    height: int
    owners: list[list[int | None]]
    fertility: list[list[float]]
    civilizations: dict[int, Civilization]
    cities: list[City]
    climate: ClimateState
    trade_routes: list[TradeRoute] = field(default_factory=list)
    market_prices: dict[str, dict[ResourceType, float]] = field(default_factory=dict)
    suggestions: list[Suggestion] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    tick_count: int = 0

