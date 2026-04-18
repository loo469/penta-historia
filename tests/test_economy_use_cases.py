from __future__ import annotations

import unittest

from src.adapters.persistence.in_memory_economy import (
    FixedTickClock,
    InMemoryCityRepository,
    InMemoryEventBus,
    InMemoryMarketRepository,
    InMemoryRouteRepository,
)
from src.application.economy_use_cases import ConsumeNeeds, PlanLogisticsFlows, ProduceResources, UpdateCityEconomy
from src.domain.economy import ResourceType, TradeRoute, default_production_rules, default_resource_stocks
from src.domain.model import City


def build_city(name: str, food: float, population: float = 10.0, fertility: float = 1.0, infrastructure: float = 1.0) -> City:
    city = City(
        name=name,
        civ_id=0,
        x=0,
        y=0,
        population=population,
        fertility=fertility,
        infrastructure=infrastructure,
        stocks=default_resource_stocks(),
        production_rules=default_production_rules(),
    )
    city.stocks[ResourceType.FOOD].amount = food
    return city


class EconomyUseCaseTests(unittest.TestCase):
    def test_produce_resources_increases_city_stock(self) -> None:
        city = build_city(name="Aster", food=0.0, fertility=1.4, infrastructure=1.2)
        city_repository = InMemoryCityRepository([city])
        event_bus = InMemoryEventBus()

        produced = ProduceResources(city_repository=city_repository, event_bus=event_bus).execute(climate_modifier=1.1)

        self.assertGreater(produced[city.name][ResourceType.FOOD], 0.0)
        self.assertGreater(city.stocks[ResourceType.FOOD].amount, 0.0)
        self.assertTrue(event_bus.events)

    def test_consume_needs_creates_shortage_when_food_is_missing(self) -> None:
        city = build_city(name="Boreal", food=0.5, population=12.0)
        city_repository = InMemoryCityRepository([city])
        event_bus = InMemoryEventBus()

        _, shortages = ConsumeNeeds(city_repository=city_repository, event_bus=event_bus).execute()

        self.assertGreater(shortages[city.name], 0.0)
        self.assertLess(city.population, 12.0)

    def test_plan_logistics_flows_moves_food_to_a_city_in_need(self) -> None:
        source = build_city(name="Source", food=18.0)
        target = build_city(name="Target", food=0.0)
        city_repository = InMemoryCityRepository([source, target])
        route_repository = InMemoryRouteRepository(
            [TradeRoute(source_city="Source", target_city="Target", distance=3, capacity=4.0)]
        )
        event_bus = InMemoryEventBus()

        transfers = PlanLogisticsFlows(
            city_repository=city_repository,
            route_repository=route_repository,
            event_bus=event_bus,
        ).execute()

        self.assertEqual(len(transfers), 1)
        self.assertEqual(transfers[0].resource, ResourceType.FOOD)
        self.assertLess(source.stocks[ResourceType.FOOD].amount, 18.0)
        self.assertGreater(target.stocks[ResourceType.FOOD].amount, 0.0)

    def test_update_city_economy_raises_food_price_in_shortage_city(self) -> None:
        rich_city = build_city(name="Granary", food=14.0)
        starving_city = build_city(name="Hungerford", food=0.2)
        city_repository = InMemoryCityRepository([rich_city, starving_city])
        market_repository = InMemoryMarketRepository()
        route_repository = InMemoryRouteRepository([])
        clock = FixedTickClock(tick=7)
        event_bus = InMemoryEventBus()

        report = UpdateCityEconomy(
            city_repository=city_repository,
            market_repository=market_repository,
            route_repository=route_repository,
            clock=clock,
            event_bus=event_bus,
        ).execute()

        self.assertEqual(report.tick, 7)
        self.assertGreater(
            market_repository.get_price("Hungerford", ResourceType.FOOD),
            market_repository.get_price("Granary", ResourceType.FOOD),
        )


if __name__ == "__main__":
    unittest.main()
