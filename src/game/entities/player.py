from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from game.settings import PLAYER_FUEL_START, PLAYER_MAX_HP, PLAYER_SPEED

if TYPE_CHECKING:
    import pymunk


@dataclass
class Player:
    x: float
    y: float
    hp: float = PLAYER_MAX_HP
    max_hp: float = PLAYER_MAX_HP
    fuel: float = PLAYER_FUEL_START
    max_fuel: float = PLAYER_FUEL_START
    fuel_rate: float = 1.0
    speed_value: float = PLAYER_SPEED
    throttle_level: float = 0.0
    boost_charge: float = 1.0
    boost_timer: float = 0.0
    boost_unlocked: bool = True
    hurdle_cooldown: float = 0.0
    hurdle_unlocked: bool = True
    tap_clock: float = 0.0
    last_left_tap: float = -10.0
    last_right_tap: float = -10.0
    left_was_down: bool = False
    right_was_down: bool = False
    enemies_killed: int = 0
    damage_dealt: int = 0
    body: pymunk.Body | None = None
    shape: pymunk.Shape | None = None

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def get_speed(self) -> float:
        return self.speed_value
