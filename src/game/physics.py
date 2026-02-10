"""Pymunk-driven ship physics helpers."""

from __future__ import annotations

import math
from typing import Iterable

import pymunk

from game.settings import (
    BOOST_DURATION,
    BOOST_FORCE,
    BOOST_RECHARGE_TIME,
    DRIFT_FACTOR,
    FRICTION,
    HURDLE_COOLDOWN,
    HURDLE_IMPULSE,
    MAX_SPEED,
    MIN_SPEED,
    ENEMY_BASE_SPEED,
    ROTATION_ACCEL,
    ROTATION_SPEED,
    STRAFE_POWER,
    THROTTLE_STEP_PER_SEC,
    THRUST_POWER,
    PLAYER_SPEED,
)


def create_space() -> pymunk.Space:
    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    space.damping = 1.0  # No damping - true Newtonian physics
    return space


def attach_body(space: pymunk.Space, entity: object, radius: float) -> None:
    if getattr(entity, "body", None) is not None:
        return
    mass = 1.0
    moment = pymunk.moment_for_circle(mass, 0.0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (getattr(entity, "x"), getattr(entity, "y"))
    body.velocity = (0.0, 0.0)
    body.angular_velocity = 0.0
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
    # Ship points up (0, -1) at angle=0, rotated by body.angle
    forward = pymunk.Vec2d(0.0, -1.0).rotated(body.angle)
    body.apply_force_at_world_point(forward * power, body.position)


def apply_strafe(body: pymunk.Body, power: float) -> None:
    # Lateral is perpendicular to forward (right is 1, 0)
    lateral = pymunk.Vec2d(1.0, 0.0).rotated(body.angle)
    body.apply_force_at_world_point(lateral * power, body.position)


def clamp_speed(body: pymunk.Body, max_speed: float, min_speed: float = MIN_SPEED) -> None:
    speed = body.velocity.length
    if speed == 0:
        return
    if speed > max_speed:
        body.velocity = body.velocity.normalized() * max_speed
    elif speed < min_speed:
        body.velocity = body.velocity.normalized() * min_speed


def apply_drift(body: pymunk.Body) -> None:
    # Only dampen angular velocity for controllable rotation
    # Linear velocity is unaffected - true Newtonian space physics
    body.angular_velocity *= DRIFT_FACTOR


def step_space(space: pymunk.Space, dt: float) -> None:
    space.step(dt)
    for body in space.bodies:
        if body.body_type == pymunk.Body.DYNAMIC:
            apply_drift(body)


def apply_player_controls(
    player: object,
    rotate_direction: float,
    strafe_direction: float,
    throttle_increment: bool,
    throttle_decrement: bool,
    max_thrust: bool,
    cut_engines: bool,
    boost_pressed: bool,
    hurdle_direction: float,
    dt: float,
) -> None:
    body = getattr(player, "body", None)
    if body is None:
        return
    apply_rotation(body, rotate_direction, dt)
    speed_multiplier = 1.0
    if hasattr(player, "get_speed"):
        speed_multiplier = float(player.get_speed()) / PLAYER_SPEED

    throttle_level = float(getattr(player, "throttle_level", 0.0))

    # Instant overrides
    if max_thrust:
        throttle_level = 1.0
    elif cut_engines:
        throttle_level = 0.0
    # Incremental adjustments
    elif throttle_increment:
        throttle_level = min(1.0, throttle_level + THROTTLE_STEP_PER_SEC * dt)
    elif throttle_decrement:
        throttle_level = max(0.0, throttle_level - THROTTLE_STEP_PER_SEC * dt)

    setattr(player, "throttle_level", throttle_level)

    if throttle_level > 0:
        apply_thrust(body, THRUST_POWER * speed_multiplier * throttle_level)

    if strafe_direction != 0:
        apply_strafe(body, STRAFE_POWER * speed_multiplier * strafe_direction)

    boost_charge = float(getattr(player, "boost_charge", 0.0))
    boost_timer = float(getattr(player, "boost_timer", 0.0))
    boost_unlocked = bool(getattr(player, "boost_unlocked", False))
    if boost_unlocked and boost_pressed and boost_charge >= 1.0 and boost_timer <= 0.0:
        boost_timer = BOOST_DURATION
        boost_charge = 0.0
    if boost_timer > 0.0:
        apply_thrust(body, BOOST_FORCE * speed_multiplier)
        boost_timer = max(0.0, boost_timer - dt)
    else:
        boost_charge = min(1.0, boost_charge + dt / BOOST_RECHARGE_TIME)
    setattr(player, "boost_timer", boost_timer)
    setattr(player, "boost_charge", boost_charge)

    hurdle_unlocked = bool(getattr(player, "hurdle_unlocked", False))
    hurdle_cooldown = float(getattr(player, "hurdle_cooldown", 0.0))
    if hurdle_cooldown > 0.0:
        hurdle_cooldown = max(0.0, hurdle_cooldown - dt)
    elif hurdle_unlocked and hurdle_direction != 0.0:
        # Lateral hurdle (right is 1, 0)
        lateral = pymunk.Vec2d(1.0, 0.0).rotated(body.angle)
        body.velocity += lateral * (HURDLE_IMPULSE * hurdle_direction)
        hurdle_cooldown = HURDLE_COOLDOWN
    setattr(player, "hurdle_cooldown", hurdle_cooldown)


def update_enemy_ai(enemies: Iterable[object], player_pos: tuple[float, float], dt: float) -> None:
    """Simple homing behavior - enemies move directly toward player at constant speed."""
    px, py = player_pos
    for enemy in enemies:
        body = getattr(enemy, "body", None)
        if body is None:
            continue

        # Calculate direction to player
        dx = px - body.position.x
        dy = py - body.position.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0.1:  # Avoid division by zero
            # Normalize direction and set velocity directly
            enemy_speed = getattr(enemy, "speed", ENEMY_BASE_SPEED)
            vx = (dx / distance) * enemy_speed
            vy = (dy / distance) * enemy_speed
            body.velocity = pymunk.Vec2d(vx, vy)

            # Rotate enemy to face movement direction (visual only)
            body.angle = math.atan2(dy, dx) + math.pi / 2  # +90° because ship points up


def sync_entity_positions(entities: Iterable[object]) -> None:
    for entity in entities:
        body = getattr(entity, "body", None)
        if body is None:
            continue
        setattr(entity, "x", float(body.position.x))
        setattr(entity, "y", float(body.position.y))


def clamp_entity_speeds(player: object, enemies: Iterable[object]) -> None:
    """Clamp player speed - enemies use direct velocity setting so don't need clamping."""
    player_body = getattr(player, "body", None)
    if player_body is not None:
        speed_multiplier = float(player.get_speed()) / PLAYER_SPEED
        clamp_speed(player_body, MAX_SPEED * speed_multiplier)
