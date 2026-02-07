"""XP gem spawning and collection system."""

from __future__ import annotations

import math

from game.entities.player import Player
from game.entities.xpgem import XPGem
from game.util import dist2


def spawn_xp_gem(enemies: list, xpgems: list[XPGem], enemy_x: float, enemy_y: float) -> None:
    """Spawn an XP gem at enemy position."""
    # XP value based on enemy type (placeholder - could vary by enemy strength)
    xp_value = 10
    xpgems.append(XPGem(x=enemy_x, y=enemy_y, value=xp_value))


def update_xp_gems(
    xpgems: list[XPGem],
    player: Player,
    dt: float,
) -> bool:
    """Update XP gem positions and check for collection. Returns True if leveled up."""
    leveled_up = False
    
    for gem in xpgems:
        gem.lifetime -= dt
        
        # Magnetism - move toward player when close
        px, py = player.pos
        d2 = dist2(gem.x, gem.y, px, py)
        
        magnet_range = player.get_tractor_range()
        if d2 < magnet_range ** 2:
            # Accelerate toward player
            d = math.sqrt(d2)
            if d > 0:
                speed = 600.0  # Magnet speed
                dx, dy = (px - gem.x) / d, (py - gem.y) / d
                gem.x += dx * speed * dt
                gem.y += dy * speed * dt
        
        # Collection
        if d2 < 20 ** 2:  # Player collision radius (approx)
            if player.add_xp(gem.value):
                leveled_up = True
            gem.lifetime = 0  # Mark for removal
    
    # Remove expired or collected gems
    xpgems[:] = [gem for gem in xpgems if gem.lifetime > 0]
    
    return leveled_up
