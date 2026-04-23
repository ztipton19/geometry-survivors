"""EMP pulse visual entity."""

from dataclasses import dataclass


@dataclass
class EmpPulse:
    x: float
    y: float
    radius: float
    ttl: float
