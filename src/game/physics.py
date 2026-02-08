"""Pymunk-driven ship physics helpers."""

from __future__ import annotations

import math
from typing import Iterable

import pymunk

from game.settings import (
    DRIFT_FACTOR,
    FRICTION,
    MAX_SPEED,
    MIN_SPEED,
    REVERSE_POWER,
    ROTATION_ACCEL,
    ROTATION_SPEED,
    THRUST_POWER,
    PLAYER_SPEED,
)


def create_space() -> pymunk.Space:
    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    space.damping = FRICTION
    return space


def attach_body(space: pymunk.Space, entity: object, radius: float) -> None:
    if getattr(entity, "body", None) is not None:
        return
    mass = 1.0
    moment = pymunk.moment_for_circle(mass, 0.0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (getattr(entity, "x"), getattr(entity, "y"))
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.2
    shape.friction = 0.5
    space.add(body, shape)
    setattr(entity, "body", body)
    setattr(entity, "shape", shape)


def remove_body(space: pymunk.Space, entity: object) -> None:
    body = getattr(entity, "body", None)
    shape = getattr(entity, "shape", None)
    if body is None or shape is None:
        return
    space.remove(body, shape)
    setattr(entity, "body", None)
    setattr(entity, "shape", None)


def apply_rotation(body: pymunk.Body, turn_direction: float, dt: float) -> None:
    accel = math.radians(ROTATION_ACCEL)
    if turn_direction != 0:
        target = math.radians(ROTATION_SPEED) * turn_direction
        delta = target - body.angular_velocity
        max_change = accel * dt
        delta = max(-max_change, min(max_change, delta))
        body.angular_velocity += delta
    else:
        body.angular_velocity *= DRIFT_FACTOR


def apply_thrust(body: pymunk.Body, power: float) -> None:
    forward = pymunk.Vec2d(1.0, 0.0).rotated(body.angle)
    body.apply_force_at_world_point(forward * power, body.position)


def clamp_speed(body: pymunk.Body, max_speed: float, min_speed: float = MIN_SPEED) -> None:
    speed = body.velocity.length
    if speed == 0:
        return
    if speed > max_speed:
        body.velocity = body.velocity.normalized() * max_speed
    elif speed < min_speed:
        body.velocity = body.velocity.normalized() * min_speed


def apply_drift(body: pymunk.Body) -> None:
    body.velocity *= DRIFT_FACTOR
    body.angular_velocity *= DRIFT_FACTOR


def step_space(space: pymunk.Space, dt: float) -> None:
    space.step(dt)
    for body in space.bodies:
        if body.body_type == pymunk.Body.DYNAMIC:
            apply_drift(body)


def apply_player_controls(
    player: object,
    turn_direction: float,
    thrust: bool,
    reverse: bool,
    dt: float,
) -> None:
    body = getattr(player, "body", None)
    if body is None:
        return
    apply_rotation(body, turn_direction, dt)
    speed_multiplier = 1.0
    if hasattr(player, "get_speed"):
        speed_multiplier = float(player.get_speed()) / PLAYER_SPEED
    if thrust:
        apply_thrust(body, THRUST_POWER * speed_multiplier)
    elif reverse:
        apply_thrust(body, -REVERSE_POWER * speed_multiplier)


def update_enemy_ai(enemies: Iterable[object], player_pos: tuple[float, float], dt: float) -> None:
    px, py = player_pos
    for enemy in enemies:
        body = getattr(enemy, "body", None)
        if body is None:
            continue
        dx = px - body.position.x
        dy = py - body.position.y
        desired = math.atan2(dy, dx)
        angle_diff = (desired - body.angle + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_diff) > 0.05:
            turn_direction = 1.0 if angle_diff > 0 else -1.0
        else:
            turn_direction = 0.0
        apply_rotation(body, turn_direction, dt)
        apply_thrust(body, THRUST_POWER)


def sync_entity_positions(entities: Iterable[object]) -> None:
    for entity in entities:
        body = getattr(entity, "body", None)
        if body is None:
            continue
        setattr(entity, "x", float(body.position.x))
        setattr(entity, "y", float(body.position.y))


def clamp_entity_speeds(player: object, enemies: Iterable[object]) -> None:
    player_body = getattr(player, "body", None)
    if player_body is not None:
        speed_multiplier = float(player.get_speed()) / PLAYER_SPEED
        clamp_speed(player_body, MAX_SPEED * speed_multiplier)
    for enemy in enemies:
        body = getattr(enemy, "body", None)
        if body is None:
            continue
        clamp_speed(body, MAX_SPEED)
