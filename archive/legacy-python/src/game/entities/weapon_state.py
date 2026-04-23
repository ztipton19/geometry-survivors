from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WeaponState:
    name: str
    ammo_max: int
    ammo_current: int
    damage: float
    fire_rate: float
    gimbal_degrees: float
    mounting: str = "forward"
    cooldown_timer: float = 0.0
    side_sign: int = 1

    @property
    def is_empty(self) -> bool:
        return self.ammo_current <= 0

    def update(self, dt: float) -> None:
        self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

    def try_fire(self) -> bool:
        if self.is_empty or self.cooldown_timer > 0.0:
            return False
        self.ammo_current -= 1
        self.cooldown_timer = 1.0 / max(0.001, self.fire_rate)
        return True
