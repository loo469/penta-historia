from __future__ import annotations

import random

from src.adapters.intrigue.in_memory import InMemoryIntrigueGateway
from src.application.intrigue_use_cases import CollecterRenseignement, DiffuserRumeur, LancerOperation, ResoudreSabotage
from src.core.types import WorldState
from src.domain.intrigue import Agent, Cellule


_rng = random.Random()



def _ensure_networks(world: WorldState) -> None:
    if world.intrigue.cellules:
        return

    for civ_id in world.civilizations:
        city = next((candidate for candidate in world.cities if candidate.civ_id == civ_id), None)
        if city is None:
            continue
        world.intrigue.cellules[f"delta-{civ_id}"] = Cellule(
            code=f"delta-{civ_id}",
            faction_id=civ_id,
            region=f"{city.name}:{city.x},{city.y}",
            agents=[
                Agent(code=f"delta-{civ_id}-a", faction_id=civ_id, stealth=1.0, cover=1.0, loyalty=1.0),
                Agent(code=f"delta-{civ_id}-b", faction_id=civ_id, stealth=1.2, cover=0.9, loyalty=0.95),
            ],
        )



def tick_intrigue(world: WorldState) -> None:
    civs = list(world.civilizations.values())
    if len(civs) < 2:
        return

    _ensure_networks(world)
    source = _rng.choice(civs)
    targets = [civ for civ in civs if civ.civ_id != source.civ_id]
    if not targets:
        return

    target = min(targets, key=lambda civ: civ.stability + civ.influence * 0.5 + _rng.random())
    cell_code = f"delta-{source.civ_id}"
    gateway = InMemoryIntrigueGateway(world=world, rng=_rng)
    launcher = LancerOperation(gateway, gateway, gateway, gateway, gateway)
    intel_use_case = CollecterRenseignement(launcher, gateway, gateway, gateway)
    rumor_use_case = DiffuserRumeur(launcher, gateway, gateway, gateway, gateway)
    sabotage_use_case = ResoudreSabotage(launcher, gateway, gateway)

    roll = _rng.random()
    if roll < 0.45:
        intel_use_case(
            cell_code,
            target_faction_id=target.civ_id,
            target_region=next((cell.region for cell in world.intrigue.cellules.values() if cell.faction_id == target.civ_id), f"civ-{target.civ_id}"),
            preparation=1.1,
            risk_base=0.16,
            intensity=0.9,
        )
    elif roll < 0.8:
        rumor_use_case(
            cell_code,
            target_faction_id=target.civ_id,
            message=f"Des rumeurs sapent la légitimité de {target.name}.",
            credibility=0.75,
            spread=0.7,
            preparation=1.0,
            risk_base=0.2,
            intensity=1.0,
        )
    else:
        sabotage_use_case(
            cell_code,
            target_faction_id=target.civ_id,
            target_region=next((cell.region for cell in world.intrigue.cellules.values() if cell.faction_id == target.civ_id), f"civ-{target.civ_id}"),
            preparation=1.2,
            risk_base=0.3,
            intensity=1.15,
        )
