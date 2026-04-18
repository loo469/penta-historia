from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.domain.model import City


class ResourceType(str, Enum):
    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"


BASE_RESOURCE_PRICES: dict[ResourceType, float] = {
    ResourceType.FOOD: 1.0,
    ResourceType.WOOD: 1.4,
    ResourceType.STONE: 1.8,
}


@dataclass
class ResourceStock:
    resource: ResourceType
    amount: float = 0.0
    capacity: float = 20.0

    def add(self, quantity: float) -> float:
        moved = max(0.0, min(quantity, self.capacity - self.amount))
        self.amount += moved
        return moved

    def remove(self, quantity: float) -> float:
        moved = max(0.0, min(quantity, self.amount))
        self.amount -= moved
        return moved


@dataclass(frozen=True)
class ProductionRule:
    resource: ResourceType
    base_output: float
    fertility_factor: float = 0.0
    infrastructure_factor: float = 0.0
    population_factor: float = 0.0


@dataclass(frozen=True)
class TradeRoute:
    source_city: str
    target_city: str
    distance: int
    capacity: float = 4.0


@dataclass(frozen=True)
class LogisticsTransfer:
    source_city: str
    target_city: str
    resource: ResourceType
    amount: float
    distance: int


def default_resource_stocks() -> dict[ResourceType, ResourceStock]:
    return {
        ResourceType.FOOD: ResourceStock(resource=ResourceType.FOOD, amount=6.0, capacity=30.0),
        ResourceType.WOOD: ResourceStock(resource=ResourceType.WOOD, amount=3.0, capacity=20.0),
        ResourceType.STONE: ResourceStock(resource=ResourceType.STONE, amount=2.0, capacity=20.0),
    }


def default_production_rules() -> list[ProductionRule]:
    return [
        ProductionRule(
            resource=ResourceType.FOOD,
            base_output=1.2,
            fertility_factor=0.45,
            population_factor=0.015,
        ),
        ProductionRule(
            resource=ResourceType.WOOD,
            base_output=0.55,
            fertility_factor=0.15,
            infrastructure_factor=0.18,
        ),
        ProductionRule(
            resource=ResourceType.STONE,
            base_output=0.35,
            infrastructure_factor=0.32,
        ),
    ]


def get_stock(city: City, resource: ResourceType) -> ResourceStock:
    stock = city.stocks.get(resource)
    if stock is not None:
        return stock

    defaults = default_resource_stocks()
    template = defaults[resource]
    stock = ResourceStock(resource=resource, amount=0.0, capacity=template.capacity)
    city.stocks[resource] = stock
    return stock


def reserve_target(city: City, resource: ResourceType) -> float:
    if resource == ResourceType.FOOD:
        return max(4.0, city.population * 0.8)
    if resource == ResourceType.WOOD:
        return max(2.0, city.population * 0.2)
    return max(1.0, city.population * 0.12)


def total_stock_amount(city: City) -> float:
    return sum(stock.amount for stock in city.stocks.values())


def produce_resources(city: City, climate_modifier: float = 1.0) -> dict[ResourceType, float]:
    if not city.production_rules:
        city.production_rules = default_production_rules()

    produced: dict[ResourceType, float] = {}
    for rule in city.production_rules:
        stock = get_stock(city, rule.resource)
        multiplier = (
            1.0
            + city.fertility * rule.fertility_factor
            + city.infrastructure * rule.infrastructure_factor
            + city.population * rule.population_factor
        )
        amount = max(0.0, rule.base_output * climate_modifier * multiplier)
        stored = stock.add(amount)
        produced[rule.resource] = stored

    city.storage = total_stock_amount(city)
    return produced


def consume_needs(city: City) -> tuple[dict[ResourceType, float], float]:
    food_needed = max(0.6, city.population * 0.18)
    food_stock = get_stock(city, ResourceType.FOOD)
    consumed_food = food_stock.remove(food_needed)
    shortage = max(0.0, food_needed - consumed_food)

    if shortage > 0.0:
        shortage_ratio = shortage / food_needed
        city.population = max(1.0, city.population - 0.25 * shortage_ratio)
        city.infrastructure = max(0.5, city.infrastructure - 0.05 * shortage_ratio)
    else:
        city.population += 0.03 * max(0.5, city.fertility)

    city.storage = total_stock_amount(city)
    return {ResourceType.FOOD: consumed_food}, shortage


def compute_market_price(city: City, resource: ResourceType) -> float:
    stock = get_stock(city, resource)
    desired = reserve_target(city, resource)
    deficit_ratio = max(0.0, desired - stock.amount) / max(desired, 1.0)
    surplus_ratio = max(0.0, stock.amount - desired) / max(desired, 1.0)
    multiplier = 1.0 + deficit_ratio * 1.5 - min(0.35, surplus_ratio * 0.15)
    return round(max(0.4, BASE_RESOURCE_PRICES[resource] * multiplier), 2)


def plan_trade_transfer(source: City, target: City, route: TradeRoute) -> LogisticsTransfer | None:
    for resource in (ResourceType.FOOD, ResourceType.WOOD, ResourceType.STONE):
        source_stock = get_stock(source, resource)
        target_stock = get_stock(target, resource)
        source_surplus = max(0.0, source_stock.amount - reserve_target(source, resource))
        target_deficit = max(0.0, reserve_target(target, resource) - target_stock.amount)
        moved = min(source_surplus, target_deficit, route.capacity)
        if moved <= 0.0:
            continue

        shipped = source_stock.remove(moved)
        received = target_stock.add(shipped)
        if received < shipped:
            source_stock.add(shipped - received)
        if received <= 0.0:
            continue

        source.storage = total_stock_amount(source)
        target.storage = total_stock_amount(target)
        return LogisticsTransfer(
            source_city=source.name,
            target_city=target.name,
            resource=resource,
            amount=received,
            distance=route.distance,
        )

    return None
