from dataclasses import dataclass


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    ttl: float

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
