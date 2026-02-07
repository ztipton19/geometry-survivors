from dataclasses import dataclass, field


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    ttl: float
    damage: float = 12.0

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
