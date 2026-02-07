"""Collision handling for bullets and enemies."""

from __future__ import annotations

from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.entities.xpgem import XPGem
from game.settings import BULLET_DAMAGE, BULLET_RADIUS, ENEMY_RADIUS, PLAYER_RADIUS
from game.util import dist2, norm


def update_enemy_positions(enemies: list[Enemy], player: Player, dt: float) -> None:
    px, py = player.pos
    for enemy in enemies:
        dx, dy = px - enemy.x, py - enemy.y
        nx, ny = norm(dx, dy)
        enemy.x += nx * enemy.speed * dt
        enemy.y += ny * enemy.speed * dt


def resolve_bullet_hits(
    bullets: list[Bullet],
    enemies: list[Enemy],
    player: Player,
    xpgems: list[XPGem],
) -> None:
    """Handle bullet collisions and spawn XP gems for killed enemies."""
    for bullet in bullets:
        for enemy in enemies:
            if dist2(bullet.x, bullet.y, enemy.x, enemy.y) <= (BULLET_RADIUS + ENEMY_RADIUS) ** 2:
                enemy.hp -= bullet.damage
                player.damage_dealt += bullet.damage
                bullet.ttl = 0
                
                # Spawn XP gem if enemy dies
                if enemy.hp <= 0:
                    player.enemies_killed += 1
                    # XP value based on enemy HP (weaker enemies give less)
                    xp_value = max(5, int(enemy.hp + bullet.damage)) // 3
                    xpgems.append(XPGem(x=enemy.x, y=enemy.y, value=xp_value))
                
                break


def resolve_player_hits(player: Player, enemies: list[Enemy], dt: float) -> None:
    """Handle enemy-player collisions, with shield damage absorption."""
    px, py = player.pos
    
    for enemy in enemies:
        if dist2(px, py, enemy.x, enemy.y) <= (PLAYER_RADIUS + ENEMY_RADIUS) ** 2:
            damage = 25 * dt
            
            # Shield absorbs damage first
            if player.shield_level > 0 and player.shield_hp > 0:
                shield_max = player.get_shield_max()
                if player.shield_hp >= damage:
                    player.shield_hp -= damage
                else:
                    remaining = damage - player.shield_hp
                    player.shield_hp = 0
                    player.hp -= remaining
            else:
                player.hp -= damage
