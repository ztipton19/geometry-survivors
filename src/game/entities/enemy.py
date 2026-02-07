from dataclasses import dataclass


@dataclass
class Enemy:
    x: float
    y: float
    speed: float
    hp: int

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
