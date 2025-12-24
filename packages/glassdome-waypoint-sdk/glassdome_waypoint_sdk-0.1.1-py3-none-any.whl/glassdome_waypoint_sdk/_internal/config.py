from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WaypointConfig:
    base_url: str  # e.g. "https://waypoint.glassdome.dev"
    timeout_seconds: float = 60.0
