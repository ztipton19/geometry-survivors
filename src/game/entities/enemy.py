from dataclasses import dataclass


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

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
