from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Resource:
    name: str
    base_price: float
    weight: float = 1.0


@dataclass
class Stock:
    amount: float = 0.0
    capacity: float = 100.0

    def add(self, quantity: float) -> None:
        self.amount = min(self.capacity, self.amount + quantity)

    def remove(self, quantity: float) -> float:
        removed = min(self.amount, quantity)
        self.amount -= removed
        return removed


@dataclass
class Route:
    source: str
    target: str
    distance: float
    capacity: float
    cost_per_trip: float


@dataclass
class Convoy:
    route: Route
    cargo: dict[str, float] = field(default_factory=dict)
    speed: float = 1.0
    progress: float = 0.0

    def update(self, dt: float) -> None:
        self.progress = min(1.0, self.progress + self.speed * dt / max(1.0, self.route.distance))


class Market:
    def get_price(self, stock: Stock, resource: Resource) -> float:
        scarcity = 1.0 - min(1.0, stock.amount / max(1.0, stock.capacity))
        return resource.base_price * (1.0 + scarcity)
