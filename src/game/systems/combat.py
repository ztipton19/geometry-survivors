"""Combat systems for bullets and auto-fire."""

from __future__ import annotations

import math
import random

from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.settings import BULLET_LIFETIME, BULLET_SPEED
from game.util import dist2, norm


def nearest_enemy(player: Player, enemies: list[Enemy]) -> Enemy | None:
    if not enemies:
        return None
    px, py = player.pos
    best = None
    best_d2 = float("inf")
    for enemy in enemies:
        d2 = dist2(px, py, enemy.x, enemy.y)
        if d2 < best_d2:
            best = enemy
            best_d2 = d2
    return best


def fire_minigun(player: Player, enemies: list[Enemy]) -> Bullet | None:
    target = nearest_enemy(player, enemies)
    if target is None:
        return None

    px, py = player.pos
    tx, ty = target.pos
    dx, dy = tx - px, ty - py
    nx, ny = norm(dx, dy)

    spread = 0.08
    ang = math.atan2(ny, nx) + random.uniform(-spread, spread)
    vx = math.cos(ang) * BULLET_SPEED
    vy = math.sin(ang) * BULLET_SPEED

    # Use player's bullet damage
    return Bullet(px, py, vx, vy, BULLET_LIFETIME, damage=player.get_bullet_damage())


def update_bullets(bullets: list[Bullet], dt: float) -> list[Bullet]:
    for bullet in bullets:
        bullet.prev_x = bullet.x
        bullet.prev_y = bullet.y
        bullet.x += bullet.vx * dt
        bullet.y += bullet.vy * dt
        bullet.ttl -= dt
    return bullets
