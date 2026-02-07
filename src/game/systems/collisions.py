"""Collision handling for bullets and enemies."""

from __future__ import annotations

from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.entities.xpgem import XPGem
from game.settings import BULLET_RADIUS, PLAYER_RADIUS
from game.util import dist2, norm, dist_to_segment2


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
    death_positions: list[tuple[float, float]],
    hit_positions: list[tuple[float, float]],
) -> None:
    """Handle bullet collisions and spawn XP gems for killed enemies."""
    for bullet in bullets:
        for enemy in enemies:
            if dist2(bullet.x, bullet.y, enemy.x, enemy.y) <= (
                BULLET_RADIUS + enemy.radius
            ) ** 2:
                apply_enemy_damage(
                    enemy,
                    bullet.damage,
                    player,
                    xpgems,
                    death_positions,
                    hit_positions,
                    (bullet.x, bullet.y),
                )
                bullet.ttl = 0
                
                break


def apply_enemy_damage(
    enemy: Enemy,
    damage: float,
    player: Player,
    xpgems: list[XPGem],
    death_positions: list[tuple[float, float]],
    hit_positions: list[tuple[float, float]],
    hit_pos: tuple[float, float],
) -> None:
    if enemy.hp <= 0:
        return
    enemy.hp -= damage
    player.damage_dealt += damage
    hit_positions.append(hit_pos)

    if enemy.hp <= 0:
        player.enemies_killed += 1
        xpgems.append(XPGem(x=enemy.x, y=enemy.y, value=enemy.xp_value))
        death_positions.append((enemy.x, enemy.y))


def resolve_rocket_hits(
    rockets: list,
    enemies: list[Enemy],
    player: Player,
    xpgems: list[XPGem],
    death_positions: list[tuple[float, float]],
    hit_positions: list[tuple[float, float]],
) -> None:
    for rocket in rockets:
        exploded = False
        for enemy in enemies:
            if dist2(rocket.x, rocket.y, enemy.x, enemy.y) <= (
                enemy.radius + 6
            ) ** 2:
                exploded = True
                break
        if not exploded:
            if dist2(rocket.x, rocket.y, rocket.target_x, rocket.target_y) <= 16**2:
                exploded = True

        if exploded:
            for enemy in enemies:
                if dist2(rocket.x, rocket.y, enemy.x, enemy.y) <= rocket.splash_radius**2:
                    apply_enemy_damage(
                        enemy,
                        rocket.damage,
                        player,
                        xpgems,
                        death_positions,
                        hit_positions,
                        (rocket.x, rocket.y),
                    )
            rocket.ttl = 0


def resolve_laser_hits(
    player: Player,
    enemies: list[Enemy],
    start: tuple[float, float],
    end: tuple[float, float],
    damage: float,
    width: float,
    xpgems: list[XPGem],
    death_positions: list[tuple[float, float]],
    hit_positions: list[tuple[float, float]],
) -> None:
    ax, ay = start
    bx, by = end
    for enemy in enemies:
        if dist_to_segment2(enemy.x, enemy.y, ax, ay, bx, by) <= (
            enemy.radius + width
        ) ** 2:
            apply_enemy_damage(
                enemy,
                damage,
                player,
                xpgems,
                death_positions,
                hit_positions,
                (enemy.x, enemy.y),
            )


def resolve_player_hits(player: Player, enemies: list[Enemy], dt: float) -> float:
    """Handle enemy-player collisions, with shield damage absorption."""
    px, py = player.pos
    total_damage = 0.0
    
    for enemy in enemies:
        if dist2(px, py, enemy.x, enemy.y) <= (PLAYER_RADIUS + enemy.radius) ** 2:
            damage = enemy.damage * dt
            total_damage += damage
            
            # Shield absorbs damage first
            if player.shield_level >= 0 and player.shield_hp > 0:
                if player.shield_hp >= damage:
                    player.shield_hp -= damage
                else:
                    remaining = damage - player.shield_hp
                    player.shield_hp = 0
                    player.hp -= remaining
            else:
                player.hp -= damage

    return total_damage
