from dataclasses import dataclass


@dataclass
class Pickup:
    x: float
    y: float
    kind: str

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
