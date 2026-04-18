from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CultureProfile:
    values: dict[str, float] = field(default_factory=lambda: {"militarisme": 0.5, "spiritualite": 0.5})
    traditions: list[str] = field(default_factory=list)
    stability_bonus: float = 0.0

    def evolve(self, pressure: dict[str, float]) -> None:
        for key, amount in pressure.items():
            self.values[key] = self.values.get(key, 0.0) + amount


@dataclass
class ResearchTree:
    unlocked: set[str] = field(default_factory=set)
    progress: dict[str, float] = field(default_factory=dict)

    def add_points(self, tech_id: str, amount: float) -> bool:
        current = self.progress.get(tech_id, 0.0) + amount
        self.progress[tech_id] = current
        if current >= 10.0:
            self.unlocked.add(tech_id)
            return True
        return False


@dataclass
class AltHistory:
    divergence_points: list[str] = field(default_factory=list)
    world_flags: set[str] = field(default_factory=set)

    def record_divergence(self, key: str) -> None:
        self.divergence_points.append(key)
        self.world_flags.add(key)


@dataclass
class NarrativeEvent:
    event_id: str
    description: str
    weight: int = 1

