"""Math helpers used across the game."""

import math


def clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def vec_len(x: float, y: float) -> float:
    return math.hypot(x, y)


def norm(x: float, y: float) -> tuple[float, float]:
    length = vec_len(x, y)
    if length == 0:
        return 0.0, 0.0
    return x / length, y / length


def dist2(ax: float, ay: float, bx: float, by: float) -> float:
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy
