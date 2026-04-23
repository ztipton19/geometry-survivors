"""Laser beam visual entity."""

from dataclasses import dataclass


@dataclass
class LaserBeam:
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    ttl: float
