"""Enemy spawning and scaling."""

from __future__ import annotations

import math
import random

from game import settings
from game.entities.enemy import Enemy
from game.settings import (
    ENEMY_BASE_SPEED,
    ENEMY_SPAWN_INTERVAL_MIN,
    ENEMY_SPAWN_INTERVAL_START,
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
            1: {"speed": 1.25, "hp": 0.7, "damage": 0.8, "xp": 0.7, "radius": 0.9},
            3: {"speed": 1.1, "hp": 0.9, "damage": 0.9, "xp": 0.9, "radius": 1.0},
            4: {"speed": 0.95, "hp": 1.1, "damage": 1.1, "xp": 1.1, "radius": 1.05},
            5: {"speed": 0.85, "hp": 1.4, "damage": 1.3, "xp": 1.4, "radius": 1.15},
            6: {"speed": 0.78, "hp": 1.7, "damage": 1.5, "xp": 1.7, "radius": 1.25},
            7: {"speed": 0.74, "hp": 1.9, "damage": 1.6, "xp": 1.9, "radius": 1.3},
            8: {"speed": 0.7, "hp": 2.1, "damage": 1.8, "xp": 2.2, "radius": 1.35},
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
            ENEMY_SPAWN_INTERVAL_START - elapsed * 0.0035,
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

        sides = self._choose_sides(elapsed)
        scaling = self.enemy_scaling.get(sides, self.enemy_scaling[4])

        base_speed = ENEMY_BASE_SPEED + min(180.0, elapsed * 2.0)
        base_hp = 24 + min(60, elapsed * 0.3)
        base_damage = 24.0 + min(12.0, elapsed * 0.02)

        speed = base_speed * scaling["speed"]
        hp = base_hp * scaling["hp"]
        damage = base_damage * scaling["damage"]
        xp_value = int(8 + base_hp * scaling["xp"] * 0.35)
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
        )

    def _choose_sides(self, elapsed: float) -> int:
        minutes = elapsed / 60.0
        for max_minutes, weights in self.enemy_weights:
            if minutes <= max_minutes:
                return self._weighted_choice(weights)
        return self._weighted_choice(self.enemy_weights[-1][1])

    def _weighted_choice(self, weights: list[tuple[int, float]]) -> int:
        total = sum(weight for _, weight in weights)
        roll = random.random() * total
        upto = 0.0
        for value, weight in weights:
            upto += weight
            if roll <= upto:
                return value
        return weights[-1][0]
