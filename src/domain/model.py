from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.domain.climate import ClimateState
from src.domain.gamma import Culture, DivergencePoint, HistoricalEvent, ResearchState


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
    storage: float = 5.0


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
    cultures: dict[int, Culture] = field(default_factory=dict)
    research_states: dict[int, ResearchState] = field(default_factory=dict)
    divergence_points: list[DivergencePoint] = field(default_factory=list)
    historical_events: list[HistoricalEvent] = field(default_factory=list)
    emitted_events: list[dict[str, object]] = field(default_factory=list)
    suggestions: list[Suggestion] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    tick_count: int = 0

