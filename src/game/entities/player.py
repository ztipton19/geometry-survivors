from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from game.settings import PLAYER_MAX_HP, PLAYER_SPEED, XP_BASE, XP_GROWTH, XP_LINEAR_BONUS
from game.upgrades import UPGRADES

if TYPE_CHECKING:
    import pymunk


@dataclass
class Player:
    x: float
    y: float
    hp: float = PLAYER_MAX_HP
    xp: int = 0
    level: int = 1
    xp_to_next: int = XP_BASE
    # Upgrade tracking
    minigun_level: int = 0
    rockets_level: int = -1  # -1 = not unlocked
    laser_level: int = -1
    emp_level: int = -1
    health_level: int = 0
    shield_level: int = 0
    shield_hp: float = 0.0
    shield_max: float = 50.0
    shield_regen_delay: float = 0.0
    tractor_level: int = 0
    speed_level: int = 0
    # Stats
    max_hp: float = PLAYER_MAX_HP
    bullet_damage: float = 10.0
    fire_cooldown: float = 0.4  # Starting fire rate
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
    # Game stats
    enemies_killed: int = 0
    damage_dealt: int = 0
    upgrades_collected: int = 0
    body: pymunk.Body | None = None
    shape: pymunk.Shape | None = None

    def __post_init__(self) -> None:
        if self.shield_level >= 0:
            self.shield_max = self.get_shield_max()
            self.shield_hp = self.shield_max

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if leveled up."""
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(XP_BASE * (XP_GROWTH ** (self.level - 1)) + XP_LINEAR_BONUS * (self.level - 1))
            return True
        return False

    def get_max_hp(self) -> float:
        base = PLAYER_MAX_HP
        return base * (1.0 + 0.25 * self.health_level)

    def get_shield_max(self) -> float:
        if self.shield_level < 0:
            return 0.0
        values = UPGRADES["shield"].values[self.shield_level]
        return float(values["shield_max"])

    def get_shield_regen_rate(self) -> float:
        if self.shield_level < 0:
            return 0.0
        values = UPGRADES["shield"].values[self.shield_level]
        return float(values["regen_rate"])

    def get_shield_regen_delay(self) -> float:
        if self.shield_level < 0:
            return 0.0
        values = UPGRADES["shield"].values[self.shield_level]
        return float(values["regen_delay"])

    def get_speed(self) -> float:
        values = UPGRADES["speed"].values[self.speed_level]
        return float(values.get("speed", PLAYER_SPEED))

    def get_fire_cooldown(self) -> float:
        values = UPGRADES["minigun"].values[self.minigun_level]
        return float(values["fire_cooldown"])

    def get_bullet_damage(self) -> float:
        values = UPGRADES["minigun"].values[self.minigun_level]
        return float(values["bullet_damage"])

    def get_rocket_stats(self) -> dict[str, float]:
        values = UPGRADES["rockets"].values[self.rockets_level]
        return {
            "damage": float(values["damage"]),
            "splash_radius": float(values["splash_radius"]),
            "fire_cooldown": float(values["fire_cooldown"]),
        }

    def get_laser_stats(self) -> dict[str, float]:
        values = UPGRADES["laser"].values[self.laser_level]
        return {
            "damage": float(values["damage"]),
            "fire_cooldown": float(values["fire_cooldown"]),
        }

    def get_emp_stats(self) -> dict[str, float]:
        values = UPGRADES["emp"].values[self.emp_level]
        return {
            "damage": float(values["damage"]),
            "radius": float(values["radius"]),
        }

    def get_tractor_range(self) -> float:
        values = UPGRADES["tractor"].values[self.tractor_level]
        return float(values["pickup_radius"])
