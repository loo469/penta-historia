from __future__ import annotations

from dataclasses import asdict

from src.application.delta_ports import ClockPort, EventBusPort, FactionReadPort, RandomPort, WorldReadPort
from src.domain.intrigue import (
    OperationClandestine,
    RapportOperation,
    Rumeur,
    TypeOperation,
    collecter_renseignement,
    diffuser_rumeur,
    lancer_operation,
    resoudre_sabotage,
)


class LancerOperation:
    def __init__(
        self,
        world_reader: WorldReadPort,
        faction_reader: FactionReadPort,
        clock: ClockPort,
        random_port: RandomPort,
        event_bus: EventBusPort,
    ) -> None:
        self.world_reader = world_reader
        self.faction_reader = faction_reader
        self.clock = clock
        self.random_port = random_port
        self.event_bus = event_bus

    def execute(self, cell_code: str, operation: OperationClandestine) -> RapportOperation:
        world = self.world_reader.get_world()
        cellule = world.intrigue.cellules[cell_code]
        target = self.faction_reader.get_faction(operation.target_faction_id)
        target_security = target.stability * 0.35 + target.military * 0.15
        report = lancer_operation(
            cellule,
            operation,
            target_security=target_security,
            success_roll=self.random_port.random(),
            detection_roll=self.random_port.random(),
        )
        world.log.append(
            f"Delta a lancé {operation.type_operation.value} contre {target.name} depuis {cellule.region}."
        )
        self.event_bus.publish(
            "operation_clandestine_lancee",
            {
                "tick": self.clock.now(),
                "cell_code": cell_code,
                "operation_code": operation.code,
                "type_operation": operation.type_operation.value,
                "target_faction_id": operation.target_faction_id,
                "success": report.success,
                "detected": report.detected,
                "alert_level": report.alert_level.value,
            },
        )
        return report

    __call__ = execute


class ResoudreSabotage:
    def __init__(self, launcher: LancerOperation, faction_reader: FactionReadPort, event_bus: EventBusPort) -> None:
        self.launcher = launcher
        self.faction_reader = faction_reader
        self.event_bus = event_bus

    def execute(
        self,
        cell_code: str,
        *,
        target_faction_id: int,
        target_region: str,
        preparation: float = 1.0,
        risk_base: float = 0.3,
        intensity: float = 1.0,
    ) -> RapportOperation:
        operation = OperationClandestine(
            code=f"sabotage-{cell_code}-{target_faction_id}",
            type_operation=TypeOperation.SABOTAGE,
            source_faction_id=self.launcher.world_reader.get_world().intrigue.cellules[cell_code].faction_id,
            target_faction_id=target_faction_id,
            target_region=target_region,
            preparation=preparation,
            risk_base=risk_base,
            intensity=intensity,
        )
        report = self.launcher.execute(cell_code, operation)
        impact = resoudre_sabotage(report)
        target = self.faction_reader.get_faction(target_faction_id)
        target.industry = max(0.0, target.industry - impact.industry_loss)
        target.stability = max(0.0, target.stability - impact.stability_loss)
        self.event_bus.publish(
            "sabotage_resolu",
            {
                "target_faction_id": target_faction_id,
                **asdict(impact),
                "success": report.success,
                "detected": report.detected,
            },
        )
        return report

    __call__ = execute


class DiffuserRumeur:
    def __init__(
        self,
        launcher: LancerOperation,
        world_reader: WorldReadPort,
        faction_reader: FactionReadPort,
        clock: ClockPort,
        event_bus: EventBusPort,
    ) -> None:
        self.launcher = launcher
        self.world_reader = world_reader
        self.faction_reader = faction_reader
        self.clock = clock
        self.event_bus = event_bus

    def execute(
        self,
        cell_code: str,
        *,
        target_faction_id: int,
        message: str,
        credibility: float = 0.7,
        spread: float = 0.7,
        preparation: float = 1.0,
        risk_base: float = 0.2,
        intensity: float = 1.0,
    ) -> RapportOperation:
        operation = OperationClandestine(
            code=f"rumeur-{cell_code}-{target_faction_id}",
            type_operation=TypeOperation.INTRIGUE,
            source_faction_id=self.world_reader.get_world().intrigue.cellules[cell_code].faction_id,
            target_faction_id=target_faction_id,
            target_region=self.world_reader.get_world().intrigue.cellules[cell_code].region,
            preparation=preparation,
            risk_base=risk_base,
            intensity=intensity,
        )
        report = self.launcher.execute(cell_code, operation)
        rumor = Rumeur(
            message=message,
            source_faction_id=operation.source_faction_id,
            target_faction_id=target_faction_id,
            credibility=credibility,
            spread=spread,
            created_at_tick=self.clock.now(),
        )
        impact = diffuser_rumeur(report, rumor)
        world = self.world_reader.get_world()
        world.intrigue.rumeurs.append(rumor)
        target = self.faction_reader.get_faction(target_faction_id)
        target.stability = max(0.0, target.stability - impact.stability_loss)
        target.influence = max(0.0, target.influence - impact.influence_shift)
        self.event_bus.publish(
            "rumeur_diffusee",
            {
                "target_faction_id": target_faction_id,
                "message": message,
                **asdict(impact),
                "success": report.success,
            },
        )
        return report

    __call__ = execute


class CollecterRenseignement:
    def __init__(
        self,
        launcher: LancerOperation,
        world_reader: WorldReadPort,
        faction_reader: FactionReadPort,
        event_bus: EventBusPort,
    ) -> None:
        self.launcher = launcher
        self.world_reader = world_reader
        self.faction_reader = faction_reader
        self.event_bus = event_bus

    def execute(
        self,
        cell_code: str,
        *,
        target_faction_id: int,
        target_region: str,
        preparation: float = 1.0,
        risk_base: float = 0.18,
        intensity: float = 1.0,
    ) -> RapportOperation:
        source_faction_id = self.world_reader.get_world().intrigue.cellules[cell_code].faction_id
        operation = OperationClandestine(
            code=f"intel-{cell_code}-{target_faction_id}",
            type_operation=TypeOperation.RENSEIGNEMENT,
            source_faction_id=source_faction_id,
            target_faction_id=target_faction_id,
            target_region=target_region,
            preparation=preparation,
            risk_base=risk_base,
            intensity=intensity,
        )
        report = self.launcher.execute(cell_code, operation)
        impact = collecter_renseignement(report)
        world = self.world_reader.get_world()
        source = self.faction_reader.get_faction(source_faction_id)
        source.knowledge += impact.knowledge_gain
        source.influence += impact.influence_gain
        world.intrigue.intel_points[source_faction_id] = world.intrigue.intel_points.get(source_faction_id, 0.0) + impact.intel_gain
        self.event_bus.publish(
            "renseignement_collecte",
            {
                "source_faction_id": source_faction_id,
                **asdict(impact),
                "success": report.success,
                "detected": report.detected,
            },
        )
        return report

    __call__ = execute
