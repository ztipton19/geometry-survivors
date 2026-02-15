"""Combat systems for manual fire weapons and projectiles."""

from __future__ import annotations

import math
import random

from game.entities.bullet import Bullet
from game.entities.player import Player
from game.entities.weapon_state import WeaponState
from game.settings import BULLET_LIFETIME, BULLET_SPEED, PLAYER_RADIUS


def _wrap_angle(angle: float) -> float:
    while angle <= -math.pi:
        angle += math.tau
    while angle > math.pi:
        angle -= math.tau
    return angle


def _vector_to_ship_angle(dx: float, dy: float) -> float:
    # Convert world vector to ship-angle convention where angle=0 points up.
    return math.atan2(dx, -dy)


def _compute_mount_base_angle(
    player_angle: float,
    weapon: WeaponState,
    aim_world_pos: tuple[float, float] | None,
    player_pos: tuple[float, float],
) -> float:
    mounting = weapon.mounting.lower()
    if mounting == "rear":
        return player_angle + math.pi
    if mounting == "side":
        if aim_world_pos is not None:
            px, py = player_pos
            ax, ay = aim_world_pos
            to_aim_x = ax - px
            to_aim_y = ay - py
            if abs(to_aim_x) > 1e-4 or abs(to_aim_y) > 1e-4:
                right_x = math.cos(player_angle)
                right_y = math.sin(player_angle)
                dot = right_x * to_aim_x + right_y * to_aim_y
                weapon.side_sign = 1 if dot >= 0 else -1
        return player_angle + weapon.side_sign * (math.pi / 2)
    if mounting == "turret" and aim_world_pos is not None:
        px, py = player_pos
        ax, ay = aim_world_pos
        dx = ax - px
        dy = ay - py
        if abs(dx) > 1e-4 or abs(dy) > 1e-4:
            return _vector_to_ship_angle(dx, dy)
    return player_angle


def fire_weapon(
    player: Player,
    weapon: WeaponState,
    aim_world_pos: tuple[float, float] | None = None,
) -> Bullet | None:
    if player.body is None:
        return None
    if not weapon.try_fire():
        return None

    base_angle = _compute_mount_base_angle(
        float(player.body.angle),
        weapon,
        aim_world_pos,
        player.pos,
    )
    spread_radians = math.radians(weapon.gimbal_degrees)

    shot_angle = base_angle
    if aim_world_pos is not None:
        px, py = player.pos
        ax, ay = aim_world_pos
        aim_dx = ax - px
        aim_dy = ay - py
        if abs(aim_dx) > 1e-4 or abs(aim_dy) > 1e-4:
            aim_angle = _vector_to_ship_angle(aim_dx, aim_dy)
            delta = _wrap_angle(aim_angle - base_angle)
            delta = max(-spread_radians, min(spread_radians, delta))
            shot_angle = base_angle + delta
    else:
        shot_angle = base_angle + random.uniform(-spread_radians, spread_radians)

    forward_x = math.sin(shot_angle)
    forward_y = -math.cos(shot_angle)
    mounting = weapon.mounting.lower()
    side_offset = 0.0
    rear_offset = 0.0
    if mounting == "side":
        side_offset = 8.0 * weapon.side_sign
    elif mounting == "rear":
        rear_offset = -6.0
    spawn_distance = PLAYER_RADIUS + 8.0 + rear_offset
    px, py = player.pos
    right_x = math.cos(float(player.body.angle))
    right_y = math.sin(float(player.body.angle))
    bullet_x = px + forward_x * spawn_distance + right_x * side_offset
    bullet_y = py + forward_y * spawn_distance + right_y * side_offset
    bullet_vx = forward_x * BULLET_SPEED
    bullet_vy = forward_y * BULLET_SPEED
    return Bullet(
        bullet_x,
        bullet_y,
        bullet_vx,
        bullet_vy,
        BULLET_LIFETIME,
        damage=weapon.damage,
    )


def update_bullets(bullets: list[Bullet], dt: float) -> list[Bullet]:
    for bullet in bullets:
        bullet.prev_x = bullet.x
        bullet.prev_y = bullet.y
        bullet.x += bullet.vx * dt
        bullet.y += bullet.vy * dt
        bullet.ttl -= dt
    return bullets
