from __future__ import annotations

from src.domain.model import WorldState
from src.domain.war import FactionTerritory, Front, Province, clamp


class InMemoryMapRepository:
    def __init__(self, world: WorldState) -> None:
        self.world = world
        self._province_data()

    def _province_data(self) -> dict[tuple[int, int], dict[str, object]]:
        return self.world.war_state.setdefault("province_data", {})  # type: ignore[return-value]

    def list_provinces(self) -> list[Province]:
        province_data = self._province_data()
        provinces: list[Province] = []
        for y in range(self.world.height):
            for x in range(self.world.width):
                state = province_data.setdefault(
                    (x, y),
                    {
                        "stability": 1.0,
                        "garrison": 1.0,
                        "supply": 1.0,
                        "contested": False,
                        "turns_since_capture": 5,
                    },
                )
                provinces.append(
                    Province(
                        x=x,
                        y=y,
                        owner=self.world.owners[y][x],
                        fertility=self.world.fertility[y][x],
                        stability=float(state["stability"]),
                        garrison=float(state["garrison"]),
                        supply=float(state["supply"]),
                        contested=bool(state["contested"]),
                        turns_since_capture=int(state["turns_since_capture"]),
                    )
                )
        return provinces

    def save_provinces(self, provinces: list[Province]) -> None:
        province_data = self._province_data()
        for province in provinces:
            self.world.owners[province.y][province.x] = province.owner
            province_data[province.coord] = {
                "stability": province.stability,
                "garrison": province.garrison,
                "supply": province.supply,
                "contested": province.contested,
                "turns_since_capture": province.turns_since_capture,
            }


class InMemoryFactionStateRepository:
    def __init__(self, world: WorldState, map_repository: InMemoryMapRepository | None = None) -> None:
        self.world = world
        self.map_repository = map_repository or InMemoryMapRepository(world)

    def list_faction_territories(self) -> dict[int, FactionTerritory]:
        stored = self.world.war_state.get("faction_territories")
        if isinstance(stored, dict):
            return stored  # type: ignore[return-value]
        return {}

    def save_faction_territories(self, territories: dict[int, FactionTerritory]) -> None:
        self.world.war_state["faction_territories"] = territories


class WorldStateBattleResolver:
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def resolve_advantage(self, front: Front, territories: dict[int, FactionTerritory]) -> float:
        attacker = self.world.civilizations[front.attacker]
        defender = self.world.civilizations[front.defender]
        attacker_projection = attacker.military + attacker.industry * 0.25 + attacker.influence * 0.15
        defender_projection = defender.military + defender.stability * 0.3 + defender.food * 0.1
        attacker_projection += territories[front.attacker].front_pressure * 2.0
        defender_projection += territories[front.defender].average_stability * 1.5
        delta = (attacker_projection - defender_projection) / max(12.0, attacker_projection + defender_projection)
        return clamp(delta, -0.35, 0.35)


class WorldStateEventBus:
    def __init__(self, world: WorldState) -> None:
        self.world = world

    def publish(self, event_name: str, payload: dict[str, object]) -> None:
        if event_name == "ProvinceCaptured":
            attacker_id = int(payload["attacker"])
            defender_id = int(payload["defender"])
            x, y = payload["coord"]
            pressure = float(payload["pressure"])
            attacker_name = self.world.civilizations[attacker_id].name
            defender_name = self.world.civilizations[defender_id].name
            self.world.log.append(
                f"Le front s'ouvre en ({x}, {y}) : {attacker_name} prend une province à {defender_name} avec une pression de {pressure:.2f}."
            )
        elif event_name == "FrontStabilized":
            owner = int(payload["owner"])
            x, y = payload["coord"]
            owner_name = self.world.civilizations[owner].name
            self.world.log.append(
                f"{owner_name} stabilise l'arrière en ({x}, {y}) et sécurise sa nouvelle frontière."
            )
