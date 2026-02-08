from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymunk


@dataclass
class Enemy:
    x: float
    y: float
    speed: float
    hp: float
    damage: float
    xp_value: int
    sides: int = 1
    radius: float = 12.0
    is_boss: bool = False
    body: pymunk.Body | None = None
    shape: pymunk.Shape | None = None

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
