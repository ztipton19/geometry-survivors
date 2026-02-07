"""Progression and round timer."""

from __future__ import annotations

from game.settings import ROUND_SECONDS


def reset_timer() -> tuple[float, float]:
    return 0.0, float(ROUND_SECONDS)


def update_timer(elapsed: float, remaining: float, dt: float) -> tuple[float, float, bool]:
    elapsed += dt
    remaining -= dt
    if remaining <= 0:
        remaining = 0
        return elapsed, remaining, True
    return elapsed, remaining, False
