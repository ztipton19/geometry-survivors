"""Minimal camera placeholder."""

from dataclasses import dataclass


@dataclass
class Camera:
    x: float = 0.0
    y: float = 0.0

    def apply(self, position: tuple[float, float]) -> tuple[int, int]:
        return int(position[0] - self.x), int(position[1] - self.y)
