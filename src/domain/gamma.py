from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


DEFAULT_CULTURE_VALUES: dict[str, float] = {
    "knowledge": 0.5,
    "tradition": 0.5,
    "militarism": 0.5,
    "spirituality": 0.5,
}


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


@dataclass
class Culture:
    civ_id: int
    values: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_CULTURE_VALUES))
    traditions: list[str] = field(default_factory=list)
    stability_bonus: float = 0.0

    def evolve(self, pressure: Mapping[str, float]) -> dict[str, float]:
        applied: dict[str, float] = {}
        for key, delta in pressure.items():
            current = self.values.get(key, 0.5)
            updated = round(_clamp(current + delta), 3)
            self.values[key] = updated
            applied[key] = round(updated - current, 3)

        tradition = self.values.get("tradition", 0.5)
        knowledge = self.values.get("knowledge", 0.5)
        cohesion = (tradition + self.values.get("spirituality", 0.5)) / 2
        tension = max(0.0, knowledge - tradition)
        self.stability_bonus = round((cohesion - 0.5) * 0.4 - tension * 0.2, 3)
        return applied

    def adopt_tradition(self, tradition: str) -> bool:
        normalized = tradition.strip()
        if not normalized or normalized in self.traditions:
            return False
        self.traditions.append(normalized)
        return True


@dataclass
class ResearchState:
    civ_id: int
    progress: dict[str, float] = field(default_factory=dict)
    unlocked: set[str] = field(default_factory=set)
    focus: str | None = None

    def advance(self, topic: str, amount: float, unlock_cost: float = 10.0) -> bool:
        if amount < 0:
            raise ValueError("research amount cannot be negative")
        if unlock_cost <= 0:
            raise ValueError("unlock_cost must be positive")

        normalized_topic = topic.strip().lower()
        if not normalized_topic:
            raise ValueError("topic cannot be empty")

        already_unlocked = normalized_topic in self.unlocked
        current = self.progress.get(normalized_topic, 0.0) + amount
        self.progress[normalized_topic] = round(current, 3)
        if current >= unlock_cost:
            self.unlocked.add(normalized_topic)
            self.focus = normalized_topic
            return not already_unlocked
        return False


@dataclass(frozen=True)
class DivergencePoint:
    key: str
    title: str
    description: str
    tick: int
    civ_id: int | None = None
    tags: tuple[str, ...] = ()
    world_flags: tuple[str, ...] = ()

    def all_flags(self) -> set[str]:
        return {self.key, *self.world_flags}


@dataclass(frozen=True)
class HistoricalEvent:
    event_id: str
    title: str
    description: str
    weight: int = 1
    min_tick: int = 0
    civ_id: int | None = None
    required_flags: frozenset[str] = field(default_factory=frozenset)
    blocked_flags: frozenset[str] = field(default_factory=frozenset)
    culture_pressure: dict[str, float] = field(default_factory=dict)
    research_grants: dict[str, float] = field(default_factory=dict)
    divergence: DivergencePoint | None = None

    def is_eligible(self, current_tick: int, active_flags: set[str], seen_events: set[str], civ_id: int | None = None) -> bool:
        if self.event_id in seen_events:
            return False
        if current_tick < self.min_tick:
            return False
        if self.civ_id is not None and civ_id is not None and self.civ_id != civ_id:
            return False
        if not self.required_flags.issubset(active_flags):
            return False
        if self.blocked_flags.intersection(active_flags):
            return False
        return self.weight > 0
