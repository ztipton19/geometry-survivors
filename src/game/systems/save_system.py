"""Simple JSON save/load for meta progression."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SAVE_PATH = Path(__file__).resolve().parent.parent / "data" / "save_data.json"


def default_save_data() -> dict[str, Any]:
    return {
        "meta": {
            "total_runs": 0,
            "total_data_gb": 0.0,
            "best_time_seconds": 0.0,
            "total_kills": 0,
            "total_fuel_burned": 0.0,
            "total_ammo_spent": 0,
        },
        "unlocks": {
            "modules": [
                "pdc_array",
                "railgun_mk1",
                "light_armor",
                "standard_fuel_tank",
            ]
        },
    }


def load_save_data() -> dict[str, Any]:
    if not SAVE_PATH.exists():
        data = default_save_data()
        save_data(data)
        return data
    try:
        with SAVE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = default_save_data()
        save_data(data)
    return data


def save_data(data: dict[str, Any]) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SAVE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
