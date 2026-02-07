"""XP gem pickups that grant experience on collection."""

from dataclasses import dataclass

from game.settings import NEON_CYAN, NEON_GREEN


@dataclass
class XPGem:
    x: float
    y: float
    value: int
    lifetime: float = 30.0  # Despawn after 30 seconds
    magnet_range: float = 150.0  # Start magnetizing when this close

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)