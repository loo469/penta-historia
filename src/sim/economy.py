from __future__ import annotations

from src.adapters.persistence.in_memory_economy import (
    FixedTickClock,
    InMemoryCityRepository,
    InMemoryEventBus,
    InMemoryMarketRepository,
    InMemoryRouteRepository,
)
from src.application.economy_use_cases import UpdateCityEconomy
from src.core.types import WorldState
from src.domain.economy import ResourceType


def tick_economy(world: WorldState) -> None:
    city_repository = InMemoryCityRepository(world.cities)
    market_repository = InMemoryMarketRepository(world.market_prices)
    route_repository = InMemoryRouteRepository(world.trade_routes)
    event_bus = InMemoryEventBus()
    clock = FixedTickClock(tick=world.tick_count)

    report = UpdateCityEconomy(
        city_repository=city_repository,
        market_repository=market_repository,
        route_repository=route_repository,
        clock=clock,
        event_bus=event_bus,
    ).execute(climate_modifier=world.climate.fertility_modifier)

    cities_by_civ: dict[int, list] = {}
    for city in world.cities:
        cities_by_civ.setdefault(city.civ_id, []).append(city)

    for civ_id, civ in world.civilizations.items():
        civ_cities = cities_by_civ.get(civ_id, [])
        if not civ_cities:
            continue

        total_food_stock = sum(city.stocks[ResourceType.FOOD].amount for city in civ_cities)
        total_materials = sum(
            city.stocks[ResourceType.WOOD].amount + city.stocks[ResourceType.STONE].amount for city in civ_cities
        )
        average_shortage = sum(report.shortages.get(city.name, 0.0) for city in civ_cities) / len(civ_cities)

        civ.food = max(0.0, civ.food * 0.97 + total_food_stock * 0.09)
        civ.industry = max(0.0, civ.industry * 0.97 + total_materials * 0.06)
        civ.stability = max(0.0, min(20.0, civ.stability + 0.03 - average_shortage * 0.5))
