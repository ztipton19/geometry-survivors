"""Railgun slug projectile entity."""

from dataclasses import dataclass, field


@dataclass
class RailgunSlug:
    x: float
    y: float
    vx: float
    vy: float
    ttl: float
    damage: float
    prev_x: float = field(init=False)
    prev_y: float = field(init=False)
    hit_enemy_ids: set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.prev_x = self.x
        self.prev_y = self.y
