from __future__ import annotations

from src.domain.economy import BASE_RESOURCE_PRICES, ResourceType, TradeRoute
from src.domain.model import City


class InMemoryCityRepository:
    def __init__(self, cities: list[City]) -> None:
        self._cities = {city.name: city for city in cities}

    def list_all(self) -> list[City]:
        return list(self._cities.values())

    def get(self, city_name: str) -> City | None:
        return self._cities.get(city_name)

    def save(self, city: City) -> None:
        self._cities[city.name] = city


class InMemoryMarketRepository:
    def __init__(self, prices: dict[str, dict[ResourceType, float]] | None = None) -> None:
        self._prices = prices if prices is not None else {}

    def get_price(self, city_name: str, resource: ResourceType) -> float:
        return self._prices.get(city_name, {}).get(resource, BASE_RESOURCE_PRICES[resource])

    def set_price(self, city_name: str, resource: ResourceType, price: float) -> None:
        self._prices.setdefault(city_name, {})[resource] = price


class InMemoryRouteRepository:
    def __init__(self, routes: list[TradeRoute]) -> None:
        self._routes = routes

    def list_all(self) -> list[TradeRoute]:
        return list(self._routes)


class FixedTickClock:
    def __init__(self, tick: int = 0) -> None:
        self._tick = tick

    def now(self) -> int:
        return self._tick


class InMemoryEventBus:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def publish(self, event_name: str, payload: dict[str, object]) -> None:
        self.events.append({"event_name": event_name, "payload": payload})
