"""Core game loop and state."""

from __future__ import annotations

import sys

import pygame

from game import assets
from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.input import handle_player_input
from game.settings import (
    BG,
    BULLET_RADIUS,
    ENEMY_RADIUS,
    FIRE_COOLDOWN_START,
    FPS,
    HEIGHT,
    NEON_CYAN,
    NEON_MAGENTA,
    NEON_YELLOW,
    PLAYER_RADIUS,
    WIDTH,
)
from game.systems import collisions, combat, progression, spawner
from game.ui import draw_end_screen, draw_hud


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Neon Survivors (prototype)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font, self.big_font = assets.load_fonts()

        self.player = Player(WIDTH / 2, HEIGHT / 2)
        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []

        self.fire_cd = FIRE_COOLDOWN_START
        self.fire_timer = 0.0

        self.spawner = spawner.Spawner()
        self.elapsed, self.remaining = progression.reset_timer()

        self.running = True
        self.state = "PLAY"

    def restart(self) -> None:
        self.player = Player(WIDTH / 2, HEIGHT / 2)
        self.enemies.clear()
        self.bullets.clear()
        self.fire_cd = FIRE_COOLDOWN_START
        self.fire_timer = 0.0
        self.spawner.reset()
        self.elapsed, self.remaining = progression.reset_timer()
        self.state = "PLAY"

    def update(self, dt: float) -> None:
        if self.state != "PLAY":
            return

        self.elapsed, self.remaining, completed = progression.update_timer(
            self.elapsed, self.remaining, dt
        )
        if completed:
            self.state = "WIN"
            return

        handle_player_input(self.player, dt)

        self.spawner.update(dt, self.elapsed, self.enemies)

        self.fire_timer += dt
        while self.fire_timer >= self.fire_cd:
            self.fire_timer -= self.fire_cd
            combat.fire_minigun(self.player, self.enemies, self.bullets)

        combat.update_bullets(self.bullets, dt)
        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.ttl > 0 and -80 < bullet.x < WIDTH + 80 and -80 < bullet.y < HEIGHT + 80
        ]

        collisions.update_enemy_positions(self.enemies, self.player, dt)
        collisions.resolve_bullet_hits(self.bullets, self.enemies)
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
        collisions.resolve_player_hits(self.player, self.enemies, dt)

        if self.player.hp <= 0:
            self.player.hp = 0
            self.state = "LOSE"

    def draw(self) -> None:
        self.screen.fill(BG)

        for bullet in self.bullets:
            pygame.draw.circle(
                self.screen, NEON_YELLOW, (int(bullet.x), int(bullet.y)), BULLET_RADIUS
            )

        for enemy in self.enemies:
            pygame.draw.circle(
                self.screen, NEON_MAGENTA, (int(enemy.x), int(enemy.y)), ENEMY_RADIUS, 2
            )
            pygame.draw.circle(
                self.screen, (70, 0, 70), (int(enemy.x), int(enemy.y)), ENEMY_RADIUS - 3, 0
            )

        px, py = int(self.player.x), int(self.player.y)
        pygame.draw.circle(self.screen, NEON_CYAN, (px, py), PLAYER_RADIUS, 2)
        pygame.draw.circle(self.screen, (0, 40, 40), (px, py), PLAYER_RADIUS - 3, 0)

        draw_hud(
            self.screen,
            self.font,
            self.player,
            self.fire_cd,
            len(self.enemies),
            self.remaining,
        )
        draw_end_screen(self.screen, self.font, self.big_font, self.state)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_r and self.state in ("WIN", "LOSE"):
                        self.restart()

            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
