"""Enemy spawning for tactical multi-vector pressure."""

from __future__ import annotations

import math
import random

from game import settings
from game.entities.enemy import Enemy


class Spawner:
    def __init__(self) -> None:
        self.spawn_timer = 0.0
        self.max_enemies = 10
        self.sector_count = 8
        self.enemy_profiles: dict[str, dict[str, float | int | bool]] = {
            "scout": {
                "speed": 23.5,
                "hp": 22.0,
                "damage": 22.0,
                "sides": 3,
                "radius": 10.0,
                "is_boss": False,
                "behavior": "rush",
                "preferred_range": 180.0,
            },
            "fighter": {
                "speed": 18.5,
                "hp": 30.0,
                "damage": 24.0,
                "sides": 4,
                "radius": 12.0,
                "is_boss": False,
                "behavior": "skirmish",
                "preferred_range": 260.0,
            },
            "frigate": {
                "speed": 15.5,
                "hp": 44.0,
                "damage": 30.0,
                "sides": 5,
                "radius": 14.0,
                "is_boss": False,
                "behavior": "flank",
                "preferred_range": 320.0,
            },
            "heavy": {
                "speed": 12.5,
                "hp": 62.0,
                "damage": 36.0,
                "sides": 6,
                "radius": 16.0,
                "is_boss": False,
                "behavior": "siege",
                "preferred_range": 220.0,
            },
            "cruiser": {
                "speed": 10.2,
                "hp": 88.0,
                "damage": 44.0,
                "sides": 8,
                "radius": 20.0,
                "is_boss": True,
                "behavior": "siege",
                "preferred_range": 260.0,
            },
        }

    def reset(self) -> None:
        self.spawn_timer = 0.0

    def update(
        self,
        dt: float,
        elapsed: float,
        enemies: list[Enemy],
        player_pos: tuple[float, float],
    ) -> None:
        if len(enemies) >= self.max_enemies:
            return

        interval, active_sectors, profile_weights = self._get_schedule(elapsed)
        self.spawn_timer += dt
        while self.spawn_timer >= interval:
            self.spawn_timer -= interval
            if len(enemies) >= self.max_enemies:
                break
            enemies.append(
                self._spawn_enemy(player_pos, active_sectors, profile_weights)
            )

    def _spawn_enemy(
        self,
        player_pos: tuple[float, float],
        active_sectors: int,
        profile_weights: list[tuple[str, float]],
    ) -> Enemy:
        px, py = player_pos
        view_radius = max(settings.WIDTH, settings.HEIGHT) * 0.70
        margin = 180
        distance = view_radius + margin

        sector_size = math.tau / self.sector_count
        sector_indices = random.sample(range(self.sector_count), k=max(1, min(active_sectors, self.sector_count)))
        sector = random.choice(sector_indices)
        angle = sector * sector_size + random.uniform(0.0, sector_size)
        x = px + math.cos(angle) * distance
        y = py + math.sin(angle) * distance

        profile_name = self._weighted_choice(profile_weights)
        profile = self.enemy_profiles[profile_name]
        return Enemy(
            x=x,
            y=y,
            speed=float(profile["speed"]),
            hp=float(profile["hp"]),
            damage=float(profile["damage"]),
            sides=int(profile["sides"]),
            radius=float(profile["radius"]),
            is_boss=bool(profile["is_boss"]),
            behavior=str(profile.get("behavior", "rush")),
            preferred_range=float(profile.get("preferred_range", 240.0)),
        )

    def _weighted_choice(self, weights: list[tuple[str, float]]) -> str:
        total = sum(weight for _, weight in weights)
        roll = random.random() * total
        running = 0.0
        for value, weight in weights:
            running += weight
            if roll <= running:
                return value
        return weights[-1][0]

    def _get_schedule(self, elapsed: float) -> tuple[float, int, list[tuple[str, float]]]:
        minute = elapsed / 60.0
        if minute < 3.0:
            return 30.0, 1, [("scout", 0.7), ("fighter", 0.3)]
        if minute < 7.0:
            return 20.0, 2, [("scout", 0.45), ("fighter", 0.4), ("frigate", 0.15)]
        if minute < 12.0:
            return 15.0, 3, [("fighter", 0.45), ("frigate", 0.35), ("heavy", 0.2)]
        if minute < 15.0:
            return 9.0, self.sector_count, [("fighter", 0.22), ("frigate", 0.34), ("heavy", 0.32), ("cruiser", 0.12)]
        return 7.0, self.sector_count, [("frigate", 0.24), ("heavy", 0.46), ("cruiser", 0.30)]
