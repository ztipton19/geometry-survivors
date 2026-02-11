"""Combat systems for bullets and auto-fire."""

from __future__ import annotations

import math
import random

from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.entities.rocket import Rocket
from game.settings import BULLET_LIFETIME, BULLET_SPEED, ROCKET_LIFETIME, ROCKET_SPEED
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


def fire_rocket_salvo(player: Player) -> list[Rocket]:
    px, py = player.pos
    angle = 0.0
    if player.body is not None:
        angle = float(player.body.angle)

    # Match player rendering orientation: angle 0 points ship "front" upward.
    forward_x = math.sin(angle)
    forward_y = -math.cos(angle)
    right_x = -forward_y
    right_y = forward_x

    stats = player.get_rocket_stats()
    rockets: list[Rocket] = []

    missiles_per_rack = max(1, int(stats["missiles_per_rack"]))
    rack_spacing = 7.0
    front_offset = 12.0
    spread_step = 0.09
    max_target_dist = 1000.0

    for rack_dir in (-1.0, 1.0):
        spawn_x = px + forward_x * front_offset + right_x * rack_spacing * rack_dir
        spawn_y = py + forward_y * front_offset + right_y * rack_spacing * rack_dir

        for missile_idx in range(missiles_per_rack):
            spread_index = missile_idx - (missiles_per_rack - 1) / 2
            spread_angle = angle + spread_index * spread_step
            nx = math.sin(spread_angle)
            ny = -math.cos(spread_angle)
            vx = nx * ROCKET_SPEED
            vy = ny * ROCKET_SPEED
            tx = spawn_x + nx * max_target_dist
            ty = spawn_y + ny * max_target_dist
            rockets.append(
                Rocket(
                    spawn_x,
                    spawn_y,
                    vx,
                    vy,
                    tx,
                    ty,
                    ROCKET_LIFETIME,
                    damage=stats["damage"],
                    splash_radius=stats["splash_radius"],
                )
            )

    return rockets


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
