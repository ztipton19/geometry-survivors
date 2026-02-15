"""Pymunk-driven ship physics helpers."""

from __future__ import annotations

import math
from typing import Iterable

import pymunk

from game import settings
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
    FUEL_BURN_RATE,
    STRAFE_FUEL_MULT,
    BOOST_FUEL_MULT,
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


def apply_rotation(
    body: pymunk.Body,
    turn_direction: float,
    dt: float,
    rotation_speed: float,
    rotation_accel: float,
) -> None:
    if turn_direction == 0:
        return
    accel = math.radians(rotation_accel)
    max_spin = math.radians(rotation_speed)
    body.angular_velocity += accel * dt * turn_direction
    body.angular_velocity = max(-max_spin, min(max_spin, body.angular_velocity))


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
    # Preserve angular momentum so players must counter-thrust to stop spin.
    # Linear velocity is also left untouched for Newtonian movement.
    return


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
    fuel = float(getattr(player, "fuel", 0.0))
    fuel_rate = float(getattr(player, "fuel_rate", 1.0))
    has_fuel = fuel > 0.0
    drift_factor = float(getattr(player, "debug_drift_factor", DRIFT_FACTOR))
    if has_fuel:
        apply_rotation(
            body,
            rotate_direction,
            dt,
            float(getattr(player, "debug_rotation_speed", ROTATION_SPEED)),
            float(getattr(player, "debug_rotation_accel", ROTATION_ACCEL)),
        )
    body.angular_velocity *= max(0.0, min(1.0, drift_factor))
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

    thrust_power = float(getattr(player, "debug_thrust_power", THRUST_POWER))
    strafe_power = float(getattr(player, "debug_strafe_power", STRAFE_POWER))

    if has_fuel and throttle_level > 0:
        fuel_cost = FUEL_BURN_RATE * throttle_level * dt * fuel_rate
        if fuel >= fuel_cost:
            apply_thrust(body, thrust_power * speed_multiplier * throttle_level)
            fuel -= fuel_cost

    if has_fuel and strafe_direction != 0 and fuel > 0.0:
        fuel_cost = FUEL_BURN_RATE * STRAFE_FUEL_MULT * dt * fuel_rate
        if fuel >= fuel_cost:
            apply_strafe(body, strafe_power * speed_multiplier * strafe_direction)
            fuel -= fuel_cost

    boost_charge = float(getattr(player, "boost_charge", 0.0))
    boost_timer = float(getattr(player, "boost_timer", 0.0))
    boost_unlocked = bool(getattr(player, "boost_unlocked", False))
    if has_fuel and boost_unlocked and boost_pressed and boost_charge >= 1.0 and boost_timer <= 0.0:
        boost_timer = BOOST_DURATION
        boost_charge = 0.0
    if has_fuel and boost_timer > 0.0 and fuel > 0.0:
        fuel_cost = FUEL_BURN_RATE * BOOST_FUEL_MULT * dt * fuel_rate
        if fuel >= fuel_cost:
            apply_thrust(body, BOOST_FORCE * speed_multiplier)
            fuel -= fuel_cost
            boost_timer = max(0.0, boost_timer - dt)
        else:
            boost_timer = 0.0
    else:
        boost_charge = min(1.0, boost_charge + dt / BOOST_RECHARGE_TIME)
    fuel = max(0.0, fuel)
    setattr(player, "fuel", fuel)
    setattr(player, "boost_timer", boost_timer)
    setattr(player, "boost_charge", boost_charge)

    hurdle_unlocked = bool(getattr(player, "hurdle_unlocked", False))
    hurdle_cooldown = float(getattr(player, "hurdle_cooldown", 0.0))
    if hurdle_cooldown > 0.0:
        hurdle_cooldown = max(0.0, hurdle_cooldown - dt)
    elif has_fuel and hurdle_unlocked and hurdle_direction != 0.0:
        # Lateral hurdle (right is 1, 0)
        lateral = pymunk.Vec2d(1.0, 0.0).rotated(body.angle)
        body.velocity += lateral * (HURDLE_IMPULSE * hurdle_direction)
        hurdle_cooldown = HURDLE_COOLDOWN
    setattr(player, "hurdle_cooldown", hurdle_cooldown)


def update_enemy_ai(enemies: Iterable[object], player_pos: tuple[float, float], dt: float) -> None:
    """Behavior-driven movement for enemies."""
    px, py = player_pos
    for enemy in enemies:
        body = getattr(enemy, "body", None)
        if body is None:
            continue

        dx = px - body.position.x
        dy = py - body.position.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance <= 0.1:
            continue

        enemy_speed = float(getattr(enemy, "speed", ENEMY_BASE_SPEED))
        nx = dx / distance
        ny = dy / distance
        tangent_x = -ny
        tangent_y = nx
        behavior = str(getattr(enemy, "behavior", "rush"))
        preferred_range = float(getattr(enemy, "preferred_range", 240.0))
        ai_clock = float(getattr(enemy, "ai_clock", 0.0)) + dt
        setattr(enemy, "ai_clock", ai_clock)

        if behavior == "rush":
            vx = nx * enemy_speed
            vy = ny * enemy_speed
        elif behavior == "skirmish":
            orbit_sign = 1.0 if int(getattr(enemy, "sides", 4)) % 2 == 0 else -1.0
            radial = (distance - preferred_range) / max(1.0, preferred_range)
            vx = tangent_x * enemy_speed * orbit_sign + nx * enemy_speed * max(-0.55, min(0.55, radial))
            vy = tangent_y * enemy_speed * orbit_sign + ny * enemy_speed * max(-0.55, min(0.55, radial))
        elif behavior == "flank":
            wave = math.sin(ai_clock * 1.4 + int(getattr(enemy, "sides", 5)) * 0.3)
            flank_strength = 0.85
            inward_strength = 0.65 if distance > preferred_range else 0.2
            vx = tangent_x * enemy_speed * wave * flank_strength + nx * enemy_speed * inward_strength
            vy = tangent_y * enemy_speed * wave * flank_strength + ny * enemy_speed * inward_strength
        else:  # siege
            weave = math.sin(ai_clock * 0.8 + int(getattr(enemy, "sides", 6)) * 0.2) * 0.35
            vx = nx * enemy_speed * 0.92 + tangent_x * enemy_speed * weave
            vy = ny * enemy_speed * 0.92 + tangent_y * enemy_speed * weave

        velocity = pymunk.Vec2d(vx, vy)
        if velocity.length > enemy_speed:
            velocity = velocity.normalized() * enemy_speed
        body.velocity = velocity
        body.angle = math.atan2(body.velocity.y, body.velocity.x) + math.pi / 2


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
        max_speed = float(getattr(player, "debug_max_speed", settings.MAX_SPEED))
        clamp_speed(player_body, max_speed * speed_multiplier)
