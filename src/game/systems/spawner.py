"""Enemy spawning and scaling."""

from __future__ import annotations

import math
import random

from game import settings
from game.entities.enemy import Enemy
from game.settings import (
    ENEMY_BASE_SPEED,
    ENEMY_DAMAGE_BASE,
    ENEMY_DAMAGE_MAX_BONUS,
    ENEMY_DAMAGE_PER_SEC,
    ENEMY_HP_BASE,
    ENEMY_HP_MAX_BONUS,
    ENEMY_HP_PER_SEC,
    ENEMY_SPAWN_INTERVAL_MIN,
    ENEMY_SPAWN_INTERVAL_DECAY,
    ENEMY_SPAWN_INTERVAL_START,
    ENEMY_SPEED_MAX_BONUS,
    ENEMY_SPEED_PER_SEC,
    ENEMY_XP_BASE,
    ENEMY_XP_PER_HP,
)


class Spawner:
    def __init__(self) -> None:
        self.spawn_interval = ENEMY_SPAWN_INTERVAL_START
        self.spawn_timer = 0.0
        self.enemy_weights = [
            (2.0, [(1, 0.7), (3, 0.3)]),
            (5.0, [(1, 0.45), (3, 0.35), (4, 0.2)]),
            (8.0, [(1, 0.3), (3, 0.35), (4, 0.25), (5, 0.1)]),
            (11.0, [(1, 0.2), (3, 0.3), (4, 0.25), (5, 0.15), (6, 0.1)]),
            (
                60.0,
                [
                    (1, 0.15),
                    (3, 0.25),
                    (4, 0.25),
                    (5, 0.18),
                    (6, 0.12),
                    (7, 0.03),
                    (8, 0.02),
                ],
            ),
        ]
        self.enemy_scaling = {
            1: {"speed": 1.28, "hp": 0.7, "damage": 0.8, "xp": 0.7, "radius": 0.9},
            3: {"speed": 1.12, "hp": 0.9, "damage": 0.9, "xp": 0.95, "radius": 1.0},
            4: {"speed": 0.98, "hp": 1.15, "damage": 1.1, "xp": 1.15, "radius": 1.05},
            5: {"speed": 0.88, "hp": 1.45, "damage": 1.3, "xp": 1.45, "radius": 1.15},
            6: {"speed": 0.8, "hp": 1.8, "damage": 1.55, "xp": 1.75, "radius": 1.25},
            7: {"speed": 0.74, "hp": 2.05, "damage": 1.7, "xp": 2.05, "radius": 1.32},
            8: {"speed": 0.7, "hp": 2.3, "damage": 1.9, "xp": 2.3, "radius": 1.4},
            "boss": {"speed": 0.68, "hp": 2.9, "damage": 2.4, "xp": 3.0, "radius": 1.6},
        }

    def reset(self) -> None:
        self.spawn_interval = ENEMY_SPAWN_INTERVAL_START
        self.spawn_timer = 0.0

    def update(
        self, dt: float, elapsed: float, enemies: list[Enemy], player_pos: tuple[float, float]
    ) -> None:
        self.spawn_timer += dt
        self.spawn_interval = max(
            ENEMY_SPAWN_INTERVAL_MIN,
            ENEMY_SPAWN_INTERVAL_START - elapsed * ENEMY_SPAWN_INTERVAL_DECAY,
        )
        while self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            enemies.append(self._spawn_enemy(elapsed, player_pos))

    def _spawn_enemy(self, elapsed: float, player_pos: tuple[float, float]) -> Enemy:
        px, py = player_pos
        view_radius = max(settings.WIDTH, settings.HEIGHT) * 0.65
        margin = 140
        distance = view_radius + margin
        angle = random.uniform(0, math.tau)
        x = px + math.cos(angle) * distance
        y = py + math.sin(angle) * distance

        sides, scaling, is_boss = self._choose_enemy_profile(elapsed)

        base_speed = ENEMY_BASE_SPEED + min(ENEMY_SPEED_MAX_BONUS, elapsed * ENEMY_SPEED_PER_SEC)
        base_hp = ENEMY_HP_BASE + min(ENEMY_HP_MAX_BONUS, elapsed * ENEMY_HP_PER_SEC)
        base_damage = ENEMY_DAMAGE_BASE + min(
            ENEMY_DAMAGE_MAX_BONUS, elapsed * ENEMY_DAMAGE_PER_SEC
        )

        speed = base_speed * scaling["speed"]
        hp = base_hp * scaling["hp"]
        damage = base_damage * scaling["damage"]
        xp_value = int(ENEMY_XP_BASE + base_hp * scaling["xp"] * ENEMY_XP_PER_HP)
        radius = 12.0 * scaling["radius"]

        return Enemy(
            x=x,
            y=y,
            speed=speed,
            hp=hp,
            damage=damage,
            xp_value=xp_value,
            sides=sides,
            radius=radius,
            is_boss=is_boss,
        )

    def _choose_enemy_profile(self, elapsed: float) -> tuple[int, dict[str, float], bool]:
        minutes = elapsed / 60.0
        if self._should_spawn_boss(minutes):
            return 8, self.enemy_scaling["boss"], True
        for max_minutes, weights in self.enemy_weights:
            if minutes <= max_minutes:
                sides = self._weighted_choice(weights)
                return sides, self.enemy_scaling.get(sides, self.enemy_scaling[4]), False
        sides = self._weighted_choice(self.enemy_weights[-1][1])
        return sides, self.enemy_scaling.get(sides, self.enemy_scaling[4]), False

    def _should_spawn_boss(self, minutes: float) -> bool:
        if minutes < 6.0:
            return False
        chance = min(0.12, 0.02 + (minutes - 6.0) * 0.01)
        return random.random() < chance

    def _weighted_choice(self, weights: list[tuple[int, float]]) -> int:
        total = sum(weight for _, weight in weights)
        roll = random.random() * total
        upto = 0.0
        for value, weight in weights:
            upto += weight
            if roll <= upto:
                return value
        return weights[-1][0]
