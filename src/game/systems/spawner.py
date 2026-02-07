"""Enemy spawning and scaling."""

from __future__ import annotations

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

    def update(self, dt: float, elapsed: float, enemies: list[Enemy]) -> None:
        self.spawn_timer += dt
        self.spawn_interval = max(
            ENEMY_SPAWN_INTERVAL_MIN,
            ENEMY_SPAWN_INTERVAL_START - elapsed * 0.0035,
        )
        while self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            enemies.append(self._spawn_enemy(elapsed))

    def _spawn_enemy(self, elapsed: float) -> Enemy:
        edge = random.choice(["L", "R", "T", "B"])
        margin = 40
        if edge == "L":
            x = -margin
            y = random.uniform(0, HEIGHT)
        elif edge == "R":
            x = WIDTH + margin
            y = random.uniform(0, HEIGHT)
        elif edge == "T":
            x = random.uniform(0, WIDTH)
            y = -margin
        else:
            x = random.uniform(0, WIDTH)
            y = HEIGHT + margin

        speed = ENEMY_BASE_SPEED + min(180.0, elapsed * 2.0)
        hp = 26 + int(min(40, elapsed * 0.25))
        return Enemy(x, y, speed, hp)
