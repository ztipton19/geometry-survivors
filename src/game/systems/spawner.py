"""Enemy spawning and scaling."""

from __future__ import annotations

import math
import random

from game.entities.enemy import Enemy
from game.settings import (
    ENEMY_BASE_SPEED,
    ENEMY_SPAWN_INTERVAL_MIN,
    ENEMY_SPAWN_INTERVAL_START,
    HEIGHT,
    WIDTH,
)


class Spawner:
    def __init__(self) -> None:
        self.spawn_interval = ENEMY_SPAWN_INTERVAL_START
        self.spawn_timer = 0.0

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
        view_radius = max(WIDTH, HEIGHT) * 0.65
        margin = 140
        distance = view_radius + margin
        angle = random.uniform(0, math.tau)
        x = px + math.cos(angle) * distance
        y = py + math.sin(angle) * distance

        speed = ENEMY_BASE_SPEED + min(180.0, elapsed * 2.0)
        hp = 26 + int(min(40, elapsed * 0.25))
        return Enemy(x, y, speed, hp)
