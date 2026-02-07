from dataclasses import dataclass

from game.settings import PLAYER_MAX_HP


@dataclass
class Player:
    x: float
    y: float
    hp: float = PLAYER_MAX_HP

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)
