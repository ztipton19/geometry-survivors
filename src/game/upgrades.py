"""Upgrade system for player progression."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Upgrade:
    id: str
    name: str
    description: str
    category: str  # "weapon", "health", "shield"
    max_level: int
    values: list[dict]  # Per-level stat changes
    is_unlockable: bool = False  # True if starts locked

    def get_description(self, level: int) -> str:
        """Get description with current/next level values."""
        if level >= self.max_level:
            return f"{self.description} (MAXED)"
        
        if self.id == "minigun":
            cd = self.values[level]["fire_cooldown"]
            dmg = self.values[level]["bullet_damage"]
            return f"Minigun: {cd:.2f}s fire rate, {dmg} damage"
        
        elif self.id == "rockets":
            if self.is_unlockable and level == -1:
                return "Unlock: Dual forward rocket racks"
            dmg = self.values[level]["damage"]
            radius = self.values[level]["splash_radius"]
            cd = self.values[level]["fire_cooldown"]
            missiles = int(self.values[level]["missiles_per_rack"])
            return f"Rockets: {missiles}x2 missiles, {dmg} dmg, {radius:.0f}px splash, {cd:.1f}s CD"
        
        elif self.id == "laser":
            if self.is_unlockable and level == -1:
                return "Unlock: Piercing laser beam"
            dmg = self.values[level]["damage"]
            cd = self.values[level]["fire_cooldown"]
            return f"Laser: {dmg} dmg, pierces enemies, {cd:.1f}s CD"
        
        elif self.id == "emp":
            if self.is_unlockable and level == -1:
                return "Unlock: EMP pulse field"
            dmg = self.values[level]["damage"]
            radius = self.values[level]["radius"]
            return f"EMP: {dmg} dmg/tick, {radius:.0f}px radius"

        elif self.id == "mines":
            if self.is_unlockable and level == -1:
                return "Unlock: Auto-dropping proximity mines"
            cooldown = self.values[level]["drop_cooldown"]
            return f"Mines: Drops every {cooldown:.1f}s behind ship"
        
        elif self.id == "health":
            hp = int(self.values[level]["max_hp_increase"])
            heal = self.values[level]["instant_heal"]
            return f"Health: +{hp} max HP, +{heal} heal"
        
        elif self.id == "shield":
            if self.is_unlockable and level == -1:
                return "Unlock: Shield system"
            shield = int(self.values[level]["shield_max"])
            return f"Shield: +{shield} max shield, regenerates"

        elif self.id == "tractor":
            radius = int(self.values[level]["pickup_radius"])
            if radius <= 0:
                return "Tractor Beam: Manual pickup only"
            return f"Tractor Beam: {radius}px pickup radius"

        elif self.id == "speed":
            speed = int(self.values[level]["speed"])
            return f"Thrusters: {speed} movement speed"
        
        return self.description


# Define all upgrades
UPGRADES: dict[str, Upgrade] = {
    "minigun": Upgrade(
        id="minigun",
        name="Minigun Upgrade",
        description="Improve minigun fire rate and damage",
        category="weapon",
        max_level=5,
        values=[
            {"fire_cooldown": 0.4, "bullet_damage": 10.0},
            {"fire_cooldown": 0.35, "bullet_damage": 12.0},
            {"fire_cooldown": 0.3, "bullet_damage": 14.0},
            {"fire_cooldown": 0.26, "bullet_damage": 16.0},
            {"fire_cooldown": 0.22, "bullet_damage": 18.0},
            {"fire_cooldown": 0.18, "bullet_damage": 20.0},
        ],
    ),
    "rockets": Upgrade(
        id="rockets",
        name="Rockets",
        description="Dual forward rocket racks with splash damage",
        category="weapon",
        max_level=5,
        is_unlockable=True,
        values=[
            {"damage": 12, "splash_radius": 34, "fire_cooldown": 1.6, "missiles_per_rack": 3},
            {"damage": 14, "splash_radius": 38, "fire_cooldown": 1.45, "missiles_per_rack": 4},
            {"damage": 16, "splash_radius": 42, "fire_cooldown": 1.3, "missiles_per_rack": 4},
            {"damage": 18, "splash_radius": 46, "fire_cooldown": 1.2, "missiles_per_rack": 5},
            {"damage": 20, "splash_radius": 50, "fire_cooldown": 1.05, "missiles_per_rack": 5},
            {"damage": 22, "splash_radius": 55, "fire_cooldown": 0.95, "missiles_per_rack": 6},
        ],
    ),
    "laser": Upgrade(
        id="laser",
        name="Laser",
        description="Piercing laser beam",
        category="weapon",
        max_level=5,
        is_unlockable=True,
        values=[
            {"damage": 15, "fire_cooldown": 5.0},
            {"damage": 20, "fire_cooldown": 4.5},
            {"damage": 25, "fire_cooldown": 4.0},
            {"damage": 30, "fire_cooldown": 3.5},
            {"damage": 35, "fire_cooldown": 3.0},
            {"damage": 40, "fire_cooldown": 2.5},
        ],
    ),
    "emp": Upgrade(
        id="emp",
        name="EMP Field",
        description="Constant damage pulse around player",
        category="weapon",
        max_level=5,
        is_unlockable=True,
        values=[
            {"damage": 5, "radius": 100},
            {"damage": 7, "radius": 120},
            {"damage": 10, "radius": 140},
            {"damage": 15, "radius": 160},
            {"damage": 20, "radius": 180},
            {"damage": 25, "radius": 200},
        ],
    ),
    "mines": Upgrade(
        id="mines",
        name="Proximity Mines",
        description="Drop explosive mines behind the ship",
        category="weapon",
        max_level=5,
        is_unlockable=True,
        values=[
            {"drop_cooldown": 5.0},
            {"drop_cooldown": 4.5},
            {"drop_cooldown": 4.05},
            {"drop_cooldown": 3.64},
            {"drop_cooldown": 3.28},
            {"drop_cooldown": 2.95},
        ],
    ),
    "health": Upgrade(
        id="health",
        name="Health Boost",
        description="Increase max HP and heal",
        category="health",
        max_level=5,
        values=[
            {"max_hp_increase": 25, "instant_heal": 25},
            {"max_hp_increase": 25, "instant_heal": 25},
            {"max_hp_increase": 25, "instant_heal": 25},
            {"max_hp_increase": 25, "instant_heal": 25},
            {"max_hp_increase": 25, "instant_heal": 25},
            {"max_hp_increase": 25, "instant_heal": 25},
        ],
    ),
    "shield": Upgrade(
        id="shield",
        name="Shield System",
        description="Absorbs damage, regenerates over time",
        category="shield",
        max_level=5,
        is_unlockable=True,
        values=[
            {"shield_max": 50, "regen_rate": 5.0, "regen_delay": 3.0},
            {"shield_max": 62, "regen_rate": 6.0, "regen_delay": 2.8},
            {"shield_max": 75, "regen_rate": 7.0, "regen_delay": 2.6},
            {"shield_max": 87, "regen_rate": 8.0, "regen_delay": 2.4},
            {"shield_max": 100, "regen_rate": 9.0, "regen_delay": 2.2},
            {"shield_max": 112, "regen_rate": 10.0, "regen_delay": 2.0},
        ],
    ),
    "tractor": Upgrade(
        id="tractor",
        name="Tractor Beam",
        description="Magnetize XP gems toward the drone",
        category="utility",
        max_level=5,
        values=[
            {"pickup_radius": 0},
            {"pickup_radius": 50},
            {"pickup_radius": 100},
            {"pickup_radius": 150},
            {"pickup_radius": 200},
            {"pickup_radius": 250},
        ],
    ),
    "speed": Upgrade(
        id="speed",
        name="Thruster Tuning",
        description="Increase drone movement speed",
        category="utility",
        max_level=5,
        values=[
            {"speed": 27.0},
            {"speed": 29.25},
            {"speed": 31.5},
            {"speed": 33.75},
            {"speed": 36.0},
            {"speed": 38.25},
        ],
    ),
}


def get_available_upgrades(player_level: int, unlocked_weapons: set[str]) -> list[str]:
    """Get upgrade IDs that are available for the current state."""
    available = []
    
    # Always offer minigun upgrades
    available.append("minigun")
    
    # Always offer health upgrades
    available.append("health")

    # Always offer shield upgrades
    available.append("shield")
    
    # Offer unlockable weapons based on player level
    if player_level >= 3 and "rockets" not in unlocked_weapons:
        available.append("rockets")
    if player_level >= 5 and "laser" not in unlocked_weapons:
        available.append("laser")
    if player_level >= 7 and "emp" not in unlocked_weapons:
        available.append("emp")

    # Mines can always be offered and scale their drop rate with upgrades
    available.append("mines")

    # Tractor beam upgrades are always available
    available.append("tractor")

    # Thruster upgrades are always available
    available.append("speed")
    
    return available
