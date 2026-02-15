"""Data-driven ship fitting and module unlock helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from game.settings import PLAYER_SPEED

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODULES_PATH = DATA_DIR / "modules.json"
SHIPS_PATH = DATA_DIR / "ships.json"


def _read_json(path: Path, root_key: str) -> dict[str, dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    value = payload.get(root_key)
    if not isinstance(value, dict):
        return {}
    return value


def load_modules() -> dict[str, dict[str, Any]]:
    return _read_json(MODULES_PATH, "modules")


def load_ships() -> dict[str, dict[str, Any]]:
    return _read_json(SHIPS_PATH, "ships")


def get_unlocked_module_ids(save_data: dict[str, Any]) -> set[str]:
    unlocks = save_data.get("unlocks", {})
    module_ids = unlocks.get("modules", [])
    if not isinstance(module_ids, list):
        return set()
    return {str(module_id) for module_id in module_ids}


def module_fits_slot(module: dict[str, Any], slot: dict[str, Any]) -> bool:
    if module.get("type") != slot.get("type"):
        return False
    slot_size = str(slot.get("slot_size", "S"))
    module_size = str(module.get("slot_size", "S"))
    order = {"S": 1, "M": 2, "L": 3}
    return order.get(module_size, 1) <= order.get(slot_size, 1)


def compatible_modules_for_slot(
    modules: dict[str, dict[str, Any]],
    unlocked_module_ids: set[str],
    slot: dict[str, Any],
) -> list[str]:
    result: list[str] = []
    for module_id, module in modules.items():
        if module_id not in unlocked_module_ids:
            continue
        if module_fits_slot(module, slot):
            result.append(module_id)
    result.sort(key=lambda module_id: str(modules[module_id].get("name", module_id)))
    return result


def default_equipment_for_ship(
    ship: dict[str, Any],
    modules: dict[str, dict[str, Any]],
    unlocked_module_ids: set[str],
) -> dict[str, str]:
    equipment: dict[str, str] = {}
    for slot in ship.get("slots", []):
        if not isinstance(slot, dict):
            continue
        slot_id = str(slot.get("id", ""))
        if not slot_id:
            continue
        default_module = str(slot.get("default_module", ""))
        if default_module in unlocked_module_ids and default_module in modules:
            equipment[slot_id] = default_module
            continue
        compatible = compatible_modules_for_slot(modules, unlocked_module_ids, slot)
        if compatible:
            equipment[slot_id] = compatible[0]
    return equipment


def sanitize_equipment(
    equipment: dict[str, str],
    ship: dict[str, Any],
    modules: dict[str, dict[str, Any]],
    unlocked_module_ids: set[str],
) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    for slot in ship.get("slots", []):
        if not isinstance(slot, dict):
            continue
        slot_id = str(slot.get("id", ""))
        if not slot_id:
            continue
        candidate = equipment.get(slot_id)
        if candidate in modules and candidate in unlocked_module_ids:
            if module_fits_slot(modules[candidate], slot):
                cleaned[slot_id] = candidate
                continue
        compatible = compatible_modules_for_slot(modules, unlocked_module_ids, slot)
        if compatible:
            cleaned[slot_id] = compatible[0]
    return cleaned


def calculate_ship_stats(
    ship: dict[str, Any],
    modules: dict[str, dict[str, Any]],
    equipment: dict[str, str],
) -> dict[str, float | int]:
    base_mass = float(ship.get("base_mass", 1500.0))
    mass_limit = float(ship.get("mass_limit", base_mass * 2.0))
    base_hull = float(ship.get("base_hull", 100.0))
    base_fuel = float(ship.get("base_fuel", 340.0))
    base_speed = float(ship.get("base_speed", PLAYER_SPEED))

    hull_bonus = 0.0
    fuel_bonus = 0.0
    module_mass = 0.0

    for module_id in equipment.values():
        module = modules.get(module_id)
        if not module:
            continue
        module_mass += float(module.get("mass", 0.0))
        stats = module.get("stats", {})
        if isinstance(stats, dict):
            hull_bonus += float(stats.get("hull_bonus", 0.0))
            fuel_bonus += float(stats.get("fuel_bonus", 0.0))

    total_mass = base_mass + module_mass
    overload_ratio = max(0.0, total_mass / max(1.0, mass_limit) - 1.0)

    # Heavier ships burn more fuel and maneuver less effectively.
    mass_ratio = total_mass / max(1.0, base_mass)
    fuel_rate = 1.0 + max(0.0, mass_ratio - 1.0) * 0.8 + overload_ratio * 0.8
    speed_mult = max(0.58, 1.0 - max(0.0, mass_ratio - 1.0) * 0.22 - overload_ratio * 0.2)

    return {
        "base_hull": base_hull,
        "base_fuel": base_fuel,
        "base_speed": base_speed,
        "mass": total_mass,
        "mass_limit": mass_limit,
        "mass_ratio": mass_ratio,
        "hull": base_hull + hull_bonus,
        "hull_delta": hull_bonus,
        "fuel": base_fuel + fuel_bonus,
        "fuel_delta": fuel_bonus,
        "speed": base_speed * speed_mult,
        "speed_delta": base_speed * speed_mult - base_speed,
        "fuel_rate": fuel_rate,
        "overloaded": 1 if total_mass > mass_limit else 0,
        "overload_ratio": overload_ratio,
    }


def format_module_stat_lines(module: dict[str, Any]) -> list[str]:
    stats = module.get("stats", {})
    if not isinstance(stats, dict):
        return []
    lines: list[str] = []
    if "damage" in stats:
        lines.append(f"DMG {float(stats['damage']):.0f}")
    if "fire_rate" in stats:
        lines.append(f"ROF {float(stats['fire_rate']):.2f}/s")
    if "ammo" in stats:
        lines.append(f"AMMO {int(stats['ammo'])}")
    if "gimbal_degrees" in stats:
        lines.append(f"GIMBAL ±{float(stats['gimbal_degrees']):.0f}°")
    if "hull_bonus" in stats:
        lines.append(f"HULL +{float(stats['hull_bonus']):.0f}")
    if "fuel_bonus" in stats:
        lines.append(f"FUEL +{float(stats['fuel_bonus']):.0f}")
    return lines


def build_archive_entries(
    modules: dict[str, dict[str, Any]],
    unlocked_module_ids: set[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for module_id, module in modules.items():
        unlock_cost = int(module.get("unlock_cost", 0))
        entries.append(
            {
                "id": module_id,
                "name": str(module.get("name", module_id)),
                "type": str(module.get("type", "module")),
                "tier": int(module.get("tier", 1)),
                "unlock_cost": unlock_cost,
                "unlocked": module_id in unlocked_module_ids or unlock_cost <= 0,
            }
        )
    entries.sort(key=lambda entry: (int(entry["tier"]), str(entry["name"])))
    return entries


def try_unlock_module(
    save_data: dict[str, Any],
    modules: dict[str, dict[str, Any]],
    module_id: str,
) -> tuple[bool, str]:
    module = modules.get(module_id)
    if module is None:
        return False, "Unknown module"

    unlocks = save_data.setdefault("unlocks", {})
    module_ids = unlocks.setdefault("modules", [])
    if module_id in module_ids:
        return False, "Already unlocked"

    cost = int(module.get("unlock_cost", 0))
    meta = save_data.setdefault("meta", {})
    data_pool = float(meta.get("total_data_gb", 0.0))
    if data_pool < cost:
        return False, "Insufficient data"

    meta["total_data_gb"] = round(data_pool - cost, 2)
    module_ids.append(module_id)
    return True, "Module unlocked"
