from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NiveauAlerte(str, Enum):
    CALME = "calme"
    SURVEILLANCE = "surveillance"
    ALERTE = "alerte"
    EXPOSE = "expose"


class TypeOperation(str, Enum):
    SABOTAGE = "sabotage"
    RENSEIGNEMENT = "renseignement"
    INTRIGUE = "intrigue"


@dataclass
class Agent:
    code: str
    faction_id: int
    stealth: float = 1.0
    cover: float = 1.0
    loyalty: float = 1.0


@dataclass
class Cellule:
    code: str
    faction_id: int
    region: str
    agents: list[Agent] = field(default_factory=list)
    heat: float = 0.0
    exposed: bool = False
    intel_level: float = 0.0

    @property
    def stealth_moyenne(self) -> float:
        if not self.agents:
            return 0.0
        return sum(agent.stealth for agent in self.agents) / len(self.agents)

    @property
    def couverture_moyenne(self) -> float:
        if not self.agents:
            return 0.0
        return sum(agent.cover for agent in self.agents) / len(self.agents)


@dataclass
class OperationClandestine:
    code: str
    type_operation: TypeOperation
    source_faction_id: int
    target_faction_id: int
    target_region: str
    preparation: float = 1.0
    risk_base: float = 0.2
    intensity: float = 1.0


@dataclass
class Rumeur:
    message: str
    source_faction_id: int
    target_faction_id: int
    credibility: float = 0.5
    spread: float = 0.5
    created_at_tick: int = 0


@dataclass
class OperationResume:
    tick: int
    type_operation: TypeOperation
    source_faction_id: int
    target_faction_id: int
    target_region: str
    success: bool
    detected: bool
    alert_level: NiveauAlerte
    summary: str


@dataclass
class IntrigueState:
    cellules: dict[str, Cellule] = field(default_factory=dict)
    rumeurs: list[Rumeur] = field(default_factory=list)
    intel_points: dict[int, float] = field(default_factory=dict)
    recent_operations: list[OperationResume] = field(default_factory=list)
    sabotage_pressure: dict[int, float] = field(default_factory=dict)
    frontline_disruption: dict[int, float] = field(default_factory=dict)

    def record_operation(self, resume: OperationResume, limit: int = 6) -> None:
        self.recent_operations = [resume, *self.recent_operations[: limit - 1]]

    def apply_sabotage_pressure(self, faction_id: int, economic_pressure: float, war_disruption: float) -> None:
        self.sabotage_pressure[faction_id] = self.sabotage_pressure.get(faction_id, 0.0) + economic_pressure
        self.frontline_disruption[faction_id] = self.frontline_disruption.get(faction_id, 0.0) + war_disruption

    def decay_pressures(self, decay_ratio: float = 0.18) -> None:
        self.sabotage_pressure = {
            faction_id: value * (1.0 - decay_ratio)
            for faction_id, value in self.sabotage_pressure.items()
            if value * (1.0 - decay_ratio) > 0.05
        }
        self.frontline_disruption = {
            faction_id: value * (1.0 - decay_ratio)
            for faction_id, value in self.frontline_disruption.items()
            if value * (1.0 - decay_ratio) > 0.05
        }


@dataclass
class RapportOperation:
    operation: OperationClandestine
    success: bool
    detected: bool
    risk: float
    success_chance: float
    effect_strength: float
    alert_level: NiveauAlerte


@dataclass
class SabotageImpact:
    industry_loss: float
    stability_loss: float
    economic_pressure: float
    war_disruption: float


@dataclass
class IntelImpact:
    intel_gain: float
    knowledge_gain: float
    influence_gain: float


@dataclass
class RumorImpact:
    stability_loss: float
    influence_shift: float



def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))



def niveau_alerte_pour_cellule(cellule: Cellule) -> NiveauAlerte:
    if cellule.exposed or cellule.heat >= 8.0:
        return NiveauAlerte.EXPOSE
    if cellule.heat >= 5.0:
        return NiveauAlerte.ALERTE
    if cellule.heat >= 2.5:
        return NiveauAlerte.SURVEILLANCE
    return NiveauAlerte.CALME



def calculer_risque(cellule: Cellule, operation: OperationClandestine, target_security: float) -> float:
    exposure_penalty = 0.2 if cellule.exposed else 0.0
    risk = (
        operation.risk_base
        + cellule.heat * 0.08
        + target_security * 0.03
        + exposure_penalty
        - cellule.couverture_moyenne * 0.10
        - cellule.stealth_moyenne * 0.06
        - operation.preparation * 0.04
    )
    return _clamp(risk, 0.05, 0.95)



def calculer_chance_succes(cellule: Cellule, operation: OperationClandestine, target_security: float) -> float:
    penalty = 0.12 if cellule.exposed else 0.0
    success = (
        0.38
        + cellule.stealth_moyenne * 0.12
        + cellule.couverture_moyenne * 0.06
        + operation.preparation * 0.08
        + operation.intensity * 0.04
        - target_security * 0.025
        - cellule.heat * 0.04
        - penalty
    )
    return _clamp(success, 0.05, 0.95)



def lancer_operation(
    cellule: Cellule,
    operation: OperationClandestine,
    *,
    target_security: float,
    success_roll: float,
    detection_roll: float,
) -> RapportOperation:
    risk = calculer_risque(cellule, operation, target_security)
    success_chance = calculer_chance_succes(cellule, operation, target_security)
    success = success_roll <= success_chance
    detected = detection_roll <= risk

    base_heat = 0.35 + operation.risk_base * 1.4 + operation.intensity * 0.35
    if detected:
        cellule.heat += base_heat + 1.8
    else:
        cellule.heat = max(0.0, cellule.heat + base_heat - cellule.couverture_moyenne * 0.45)

    cellule.intel_level = _clamp(cellule.intel_level + (0.6 if success else 0.2), 0.0, 10.0)
    cellule.exposed = cellule.exposed or cellule.heat >= 8.0 or (detected and cellule.heat >= 6.0)

    effect_strength = operation.intensity * (1.0 if success else 0.25)
    return RapportOperation(
        operation=operation,
        success=success,
        detected=detected,
        risk=risk,
        success_chance=success_chance,
        effect_strength=effect_strength,
        alert_level=niveau_alerte_pour_cellule(cellule),
    )



def resoudre_sabotage(report: RapportOperation) -> SabotageImpact:
    if report.success:
        effect_strength = report.effect_strength
        return SabotageImpact(
            industry_loss=0.9 * effect_strength,
            stability_loss=0.55 * effect_strength,
            economic_pressure=0.8 * effect_strength,
            war_disruption=0.6 * effect_strength,
        )
    effect_strength = report.effect_strength
    return SabotageImpact(
        industry_loss=0.2 * effect_strength,
        stability_loss=0.1 * effect_strength,
        economic_pressure=0.16 * effect_strength,
        war_disruption=0.08 * effect_strength,
    )



def collecter_renseignement(report: RapportOperation) -> IntelImpact:
    if report.success:
        return IntelImpact(
            intel_gain=1.4 * report.effect_strength,
            knowledge_gain=0.8 * report.effect_strength,
            influence_gain=0.35 * report.effect_strength,
        )
    return IntelImpact(intel_gain=0.35 * report.effect_strength, knowledge_gain=0.2 * report.effect_strength, influence_gain=0.05 * report.effect_strength)



def diffuser_rumeur(report: RapportOperation, rumor: Rumeur) -> RumorImpact:
    potency = report.effect_strength * rumor.credibility * rumor.spread
    if report.success:
        return RumorImpact(stability_loss=0.85 * potency, influence_shift=0.4 * potency)
    return RumorImpact(stability_loss=0.2 * potency, influence_shift=0.1 * potency)
