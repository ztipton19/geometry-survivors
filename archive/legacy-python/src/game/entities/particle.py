from dataclasses import dataclass


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    ttl: float
    radius: float
    color: tuple[int, int, int]

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
