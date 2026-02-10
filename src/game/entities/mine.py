from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Mine:
    x: float
    y: float
    ttl: float
    damage: float
    splash_radius: float
    trigger_radius: float
