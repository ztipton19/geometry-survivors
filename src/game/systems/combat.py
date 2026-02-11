"""Combat systems for bullets and auto-fire."""

from __future__ import annotations

import math
import random

from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.entities.railgun import RailgunSlug
from game.entities.rocket import Rocket
from game.settings import (
    BULLET_LIFETIME,
    BULLET_SPEED,
    RAILGUN_LIFETIME,
    RAILGUN_SPEED,
    ROCKET_LIFETIME,
    ROCKET_SPEED,
)
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


def fire_rocket(player: Player, target_pos: tuple[float, float]) -> Rocket:
    px, py = player.pos
    tx, ty = target_pos
    dx, dy = tx - px, ty - py
    nx, ny = norm(dx, dy)
    vx = nx * ROCKET_SPEED
    vy = ny * ROCKET_SPEED
    stats = player.get_rocket_stats()
    return Rocket(
        px,
        py,
        vx,
        vy,
        tx,
        ty,
        ROCKET_LIFETIME,
        damage=stats["damage"],
        splash_radius=stats["splash_radius"],
    )


def fire_railgun(player: Player) -> RailgunSlug:
    px, py = player.pos
    angle = 0.0
    if player.body is not None:
        angle = float(player.body.angle)

    # Player ship is authored facing up; transform by body angle.
    nx = math.sin(angle)
    ny = -math.cos(angle)
    vx = nx * RAILGUN_SPEED
    vy = ny * RAILGUN_SPEED
    stats = player.get_railgun_stats()
    return RailgunSlug(px, py, vx, vy, RAILGUN_LIFETIME, damage=stats["damage"])


def update_bullets(bullets: list[Bullet], dt: float) -> list[Bullet]:
    for bullet in bullets:
        bullet.prev_x = bullet.x
        bullet.prev_y = bullet.y
        bullet.x += bullet.vx * dt
        bullet.y += bullet.vy * dt
        bullet.ttl -= dt
    return bullets


def update_rockets(rockets: list[Rocket], dt: float) -> list[Rocket]:
    for rocket in rockets:
        rocket.prev_x = rocket.x
        rocket.prev_y = rocket.y
        rocket.x += rocket.vx * dt
        rocket.y += rocket.vy * dt
        rocket.ttl -= dt
    return rockets


def update_railgun_shots(shots: list[RailgunSlug], dt: float) -> list[RailgunSlug]:
    for shot in shots:
        shot.prev_x = shot.x
        shot.prev_y = shot.y
        shot.x += shot.vx * dt
        shot.y += shot.vy * dt
        shot.ttl -= dt
    return shots
