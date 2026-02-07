from dataclasses import dataclass, field

from game.settings import PLAYER_MAX_HP


@dataclass
class Player:
    x: float
    y: float
    hp: float = PLAYER_MAX_HP
    xp: int = 0
    level: int = 1
    xp_to_next: int = 100
    # Upgrade tracking
    minigun_level: int = 0
    rockets_level: int = -1  # -1 = not unlocked
    laser_level: int = -1
    emp_level: int = -1
    health_level: int = 0
    shield_level: int = -1
    shield_hp: float = 0.0
    shield_max: float = 50.0
    # Stats
    max_hp: float = PLAYER_MAX_HP
    bullet_damage: float = 12.0
    fire_cooldown: float = 0.14  # Starting fire rate
    # Game stats
    enemies_killed: int = 0
    damage_dealt: int = 0
    upgrades_collected: int = 0

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if leveled up."""
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(100 * (1.3 ** (self.level - 1)))
            return True
        return False

    def get_max_hp(self) -> float:
        base = PLAYER_MAX_HP
        return base * (1.0 + 0.25 * self.health_level)

    def get_shield_max(self) -> float:
        base = 50.0
        return base * (1.0 + 0.25 * self.shield_level) if self.shield_level > 0 else 0.0

    def get_fire_cooldown(self) -> float:
        base = 0.14
        reduction = 0.01 * self.minigun_level
        return max(0.04, base - reduction)

    def get_bullet_damage(self) -> float:
        base = 12.0
        increase = 2.0 * self.minigun_level
        return base + increase
