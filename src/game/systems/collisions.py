"""Collision handling for bullets and enemies."""

from __future__ import annotations

from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.settings import BULLET_DAMAGE, BULLET_RADIUS, ENEMY_RADIUS, PLAYER_RADIUS
from game.util import dist2, norm


def update_enemy_positions(enemies: list[Enemy], player: Player, dt: float) -> None:
    px, py = player.pos
    for enemy in enemies:
        dx, dy = px - enemy.x, py - enemy.y
        nx, ny = norm(dx, dy)
        enemy.x += nx * enemy.speed * dt
        enemy.y += ny * enemy.speed * dt


def resolve_bullet_hits(bullets: list[Bullet], enemies: list[Enemy]) -> None:
    for bullet in bullets:
        for enemy in enemies:
            if dist2(bullet.x, bullet.y, enemy.x, enemy.y) <= (BULLET_RADIUS + ENEMY_RADIUS) ** 2:
                enemy.hp -= BULLET_DAMAGE
                bullet.ttl = 0
                break


def resolve_player_hits(player: Player, enemies: list[Enemy], dt: float) -> None:
    px, py = player.pos
    for enemy in enemies:
        if dist2(px, py, enemy.x, enemy.y) <= (PLAYER_RADIUS + ENEMY_RADIUS) ** 2:
            player.hp -= 25 * dt
