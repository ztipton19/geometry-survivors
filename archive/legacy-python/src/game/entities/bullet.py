from dataclasses import dataclass, field


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    ttl: float
    damage: float = 12.0
    prev_x: float = field(init=False)
    prev_y: float = field(init=False)

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def __post_init__(self) -> None:
        self.prev_x = self.x
        self.prev_y = self.y
