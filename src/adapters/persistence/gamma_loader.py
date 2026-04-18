from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.domain.gamma import DivergencePoint, HistoricalEvent

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency in local environments
    yaml = None


@dataclass(frozen=True)
class GammaCatalog:
    divergence_points: list[DivergencePoint] = field(default_factory=list)
    historical_events: list[HistoricalEvent] = field(default_factory=list)


class GammaContentLoader:
    def load_catalog(self, path: str | Path) -> GammaCatalog:
        source = Path(path)
        raw = self._read_file(source)
        return GammaCatalog(
            divergence_points=[self._build_divergence(item) for item in raw.get("divergence_points", [])],
            historical_events=[self._build_historical_event(item) for item in raw.get("historical_events", [])],
        )

    def _read_file(self, path: Path) -> dict[str, Any]:
        suffix = path.suffix.lower()
        content = path.read_text(encoding="utf-8")
        if suffix == ".json":
            return json.loads(content)
        if suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("PyYAML is required to load YAML gamma data")
            loaded = yaml.safe_load(content)
            if loaded is None:
                return {}
            if not isinstance(loaded, dict):
                raise ValueError("Gamma catalog must deserialize to a mapping")
            return loaded
        raise ValueError(f"unsupported gamma catalog format: {path.suffix}")

    def _build_divergence(self, data: dict[str, Any]) -> DivergencePoint:
        return DivergencePoint(
            key=data["key"],
            title=data["title"],
            description=data.get("description", ""),
            tick=int(data.get("tick", 0)),
            civ_id=data.get("civ_id"),
            tags=tuple(data.get("tags", [])),
            world_flags=tuple(data.get("world_flags", [])),
        )

    def _build_historical_event(self, data: dict[str, Any]) -> HistoricalEvent:
        divergence_data = data.get("divergence")
        divergence = self._build_divergence(divergence_data) if divergence_data else None
        return HistoricalEvent(
            event_id=data["event_id"],
            title=data["title"],
            description=data.get("description", ""),
            weight=int(data.get("weight", 1)),
            min_tick=int(data.get("min_tick", 0)),
            civ_id=data.get("civ_id"),
            required_flags=frozenset(data.get("required_flags", [])),
            blocked_flags=frozenset(data.get("blocked_flags", [])),
            culture_pressure=dict(data.get("culture_pressure", {})),
            research_grants=dict(data.get("research_grants", {})),
            divergence=divergence,
        )
