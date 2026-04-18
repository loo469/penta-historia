from __future__ import annotations

from dataclasses import dataclass, field

from src.application.ports import CityRepository, ClockPort, EventBusPort, MarketRepository, RouteRepository
from src.domain.economy import LogisticsTransfer, ResourceType, compute_market_price, consume_needs, plan_trade_transfer, produce_resources


@dataclass
class EconomyUpdateReport:
    tick: int
    produced: dict[str, dict[ResourceType, float]] = field(default_factory=dict)
    consumed: dict[str, dict[ResourceType, float]] = field(default_factory=dict)
    shortages: dict[str, float] = field(default_factory=dict)
    transfers: list[LogisticsTransfer] = field(default_factory=list)
    prices: dict[str, dict[ResourceType, float]] = field(default_factory=dict)


class ProduceResources:
    def __init__(self, city_repository: CityRepository, event_bus: EventBusPort) -> None:
        self.city_repository = city_repository
        self.event_bus = event_bus

    def execute(self, climate_modifier: float = 1.0) -> dict[str, dict[ResourceType, float]]:
        produced_by_city: dict[str, dict[ResourceType, float]] = {}
        for city in self.city_repository.list_all():
            produced = produce_resources(city, climate_modifier=climate_modifier)
            self.city_repository.save(city)
            produced_by_city[city.name] = produced
            self.event_bus.publish(
                "resources_produced",
                {
                    "city": city.name,
                    "produced": {resource.value: amount for resource, amount in produced.items()},
                },
            )
        return produced_by_city


class ConsumeNeeds:
    def __init__(self, city_repository: CityRepository, event_bus: EventBusPort) -> None:
        self.city_repository = city_repository
        self.event_bus = event_bus

    def execute(self) -> tuple[dict[str, dict[ResourceType, float]], dict[str, float]]:
        consumed_by_city: dict[str, dict[ResourceType, float]] = {}
        shortages: dict[str, float] = {}
        for city in self.city_repository.list_all():
            consumed, shortage = consume_needs(city)
            self.city_repository.save(city)
            consumed_by_city[city.name] = consumed
            shortages[city.name] = shortage
            if shortage > 0.0:
                self.event_bus.publish(
                    "city_shortage",
                    {"city": city.name, "shortage": round(shortage, 2)},
                )
        return consumed_by_city, shortages


class PlanLogisticsFlows:
    def __init__(self, city_repository: CityRepository, route_repository: RouteRepository, event_bus: EventBusPort) -> None:
        self.city_repository = city_repository
        self.route_repository = route_repository
        self.event_bus = event_bus

    def execute(self) -> list[LogisticsTransfer]:
        transfers: list[LogisticsTransfer] = []
        for route in self.route_repository.list_all():
            source = self.city_repository.get(route.source_city)
            target = self.city_repository.get(route.target_city)
            if source is None or target is None:
                continue

            transfer = plan_trade_transfer(source, target, route)
            if transfer is None:
                continue

            self.city_repository.save(source)
            self.city_repository.save(target)
            transfers.append(transfer)
            self.event_bus.publish(
                "logistics_transfer_planned",
                {
                    "source": transfer.source_city,
                    "target": transfer.target_city,
                    "resource": transfer.resource.value,
                    "amount": round(transfer.amount, 2),
                },
            )
        return transfers


class UpdateCityEconomy:
    def __init__(
        self,
        city_repository: CityRepository,
        market_repository: MarketRepository,
        route_repository: RouteRepository,
        clock: ClockPort,
        event_bus: EventBusPort,
    ) -> None:
        self.city_repository = city_repository
        self.market_repository = market_repository
        self.route_repository = route_repository
        self.clock = clock
        self.event_bus = event_bus
        self.produce_resources = ProduceResources(city_repository=city_repository, event_bus=event_bus)
        self.consume_needs = ConsumeNeeds(city_repository=city_repository, event_bus=event_bus)
        self.plan_logistics_flows = PlanLogisticsFlows(
            city_repository=city_repository,
            route_repository=route_repository,
            event_bus=event_bus,
        )

    def execute(self, climate_modifier: float = 1.0) -> EconomyUpdateReport:
        report = EconomyUpdateReport(tick=self.clock.now())
        report.produced = self.produce_resources.execute(climate_modifier=climate_modifier)
        report.consumed, report.shortages = self.consume_needs.execute()
        report.transfers = self.plan_logistics_flows.execute()
        report.prices = self._refresh_prices()
        self.event_bus.publish(
            "city_economy_updated",
            {
                "tick": report.tick,
                "cities": len(report.prices),
                "transfers": len(report.transfers),
            },
        )
        return report

    def _refresh_prices(self) -> dict[str, dict[ResourceType, float]]:
        prices: dict[str, dict[ResourceType, float]] = {}
        for city in self.city_repository.list_all():
            city_prices: dict[ResourceType, float] = {}
            for resource in city.stocks:
                price = compute_market_price(city, resource)
                self.market_repository.set_price(city.name, resource, price)
                city_prices[resource] = price
            prices[city.name] = city_prices
        return prices
