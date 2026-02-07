"""Upgrade application system."""

import random

from game.entities.player import Player
from game.upgrades import UPGRADES, get_available_upgrades


def generate_upgrade_options(player: Player) -> list[str]:
    """Generate 3 random upgrade options based on current state."""
    # Get unlocked weapons
    unlocked_weapons = set()
    if player.rockets_level >= 0:
        unlocked_weapons.add("rockets")
    if player.laser_level >= 0:
        unlocked_weapons.add("laser")
    if player.emp_level >= 0:
        unlocked_weapons.add("emp")
    if player.shield_level >= 0:
        unlocked_weapons.add("shield")
    
    # Get available upgrades
    available = get_available_upgrades(player.level, unlocked_weapons)
    
    # Filter out maxed out upgrades
    valid_options = []
    for upgrade_id in available:
        upgrade = UPGRADES[upgrade_id]
        current_level = getattr(player, f"{upgrade_id}_level", 0)
        if current_level < upgrade.max_level:
            valid_options.append(upgrade_id)
    
    # Select 3 random options (or fewer if not enough available)
    num_options = min(3, len(valid_options))
    if num_options == 0:
        # No valid upgrades remain (everything maxed).
        return []
    
    return random.sample(valid_options, num_options)


def apply_upgrade(player: Player, upgrade_id: str) -> None:
    """Apply an upgrade to the player."""
    upgrade = UPGRADES[upgrade_id]
    
    # Get current level
    current_level = getattr(player, f"{upgrade_id}_level", 0)
    if current_level >= upgrade.max_level:
        # Already maxed; ignore safely.
        return
    new_level = current_level + 1 if current_level >= 0 else 0
    
    # Get upgrade values for this level
    if upgrade_id == "minigun":
        player.minigun_level = new_level
        # Stats are calculated dynamically from player methods
    elif upgrade_id == "rockets":
        player.rockets_level = new_level
    elif upgrade_id == "laser":
        player.laser_level = new_level
    elif upgrade_id == "emp":
        player.emp_level = new_level
    elif upgrade_id == "health":
        player.health_level = new_level
        values = upgrade.values[new_level]
        # Increase max HP
        player.max_hp = player.get_max_hp()
        # Instant heal
        heal_amount = values["instant_heal"]
        player.hp = min(player.max_hp, player.hp + heal_amount)
    elif upgrade_id == "shield":
        player.shield_level = new_level
        # Initialize shield if newly unlocked
        if current_level < 0:
            player.shield_hp = player.get_shield_max()
        else:
            player.shield_hp = min(player.shield_hp, player.get_shield_max())
    elif upgrade_id == "tractor":
        player.tractor_level = new_level
    
    player.upgrades_collected += 1
