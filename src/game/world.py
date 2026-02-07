"""Core game loop and state."""

from __future__ import annotations

import sys

import pygame

from game import assets
from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.player import Player
from game.entities.xpgem import XPGem
from game.input import handle_player_input
from game.settings import (
    BG,
    BULLET_RADIUS,
    ENEMY_RADIUS,
    FPS,
    HEIGHT,
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_YELLOW,
    PLAYER_RADIUS,
    WIDTH,
)
from game.systems import collisions, combat, progression, spawner, upgrades, xp
from game.ui import draw_end_screen, draw_hud, draw_level_up_screen


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
        self.xpgems: list[XPGem] = []

        self.fire_timer = 0.0

        self.spawner = spawner.Spawner()
        self.elapsed, self.remaining = progression.reset_timer()

        self.running = True
        self.state = "PLAY"
        
        # Upgrade system
        self.upgrade_options: list[str] = []

    def restart(self) -> None:
        self.player = Player(WIDTH / 2, HEIGHT / 2)
        self.enemies.clear()
        self.bullets.clear()
        self.xpgems.clear()
        self.fire_timer = 0.0
        self.spawner.reset()
        self.elapsed, self.remaining = progression.reset_timer()
        self.state = "PLAY"
        self.upgrade_options.clear()

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

        # Use player's fire cooldown
        fire_cd = self.player.get_fire_cooldown()
        self.fire_timer += dt
        while self.fire_timer >= fire_cd:
            self.fire_timer -= fire_cd
            combat.fire_minigun(self.player, self.enemies, self.bullets)

        combat.update_bullets(self.bullets, dt)
        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.ttl > 0 and -80 < bullet.x < WIDTH + 80 and -80 < bullet.y < HEIGHT + 80
        ]

        collisions.update_enemy_positions(self.enemies, self.player, dt)
        collisions.resolve_bullet_hits(self.bullets, self.enemies, self.player, self.xpgems)
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
        collisions.resolve_player_hits(self.player, self.enemies, dt)

        # Update XP gems
        leveled_up = xp.update_xp_gems(self.xpgems, self.player, dt)
        
        # Level up
        if leveled_up:
            self.state = "LEVEL_UP"
            self.upgrade_options = upgrades.generate_upgrade_options(self.player)

        # Check death
        if self.player.hp <= 0:
            self.player.hp = 0
            self.state = "LOSE"

    def draw(self) -> None:
        self.screen.fill(BG)

        # Draw XP gems
        for gem in self.xpgems:
            # Pulse effect
            pulse = int(5 * (1 + 0.3 * (gem.x % 100) / 100))
            pygame.draw.circle(
                self.screen, NEON_GREEN, (int(gem.x), int(gem.y)), pulse, 0
            )
            pygame.draw.circle(
                self.screen, NEON_CYAN, (int(gem.x), int(gem.y)), pulse + 2, 1
            )

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
        
        # Draw shield if active
        if self.player.shield_level > 0 and self.player.shield_hp > 0:
            shield_radius = PLAYER_RADIUS + 5
            pygame.draw.circle(
                self.screen, (100, 100, 255), (px, py), shield_radius, 2
            )

        draw_hud(
            self.screen,
            self.font,
            self.player,
            self.player.get_fire_cooldown(),
            len(self.enemies),
            self.remaining,
        )
        
        # Draw level-up screen if in that state
        if self.state == "LEVEL_UP":
            draw_level_up_screen(
                self.screen,
                self.font,
                self.big_font,
                self.upgrade_options,
            )
        
        draw_end_screen(self.screen, self.font, self.big_font, self.state, self.player)

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
                    # Level-up selection
                    if self.state == "LEVEL_UP":
                        if event.key == pygame.K_1 and len(self.upgrade_options) >= 1:
                            upgrades.apply_upgrade(self.player, self.upgrade_options[0])
                            self.state = "PLAY"
                        elif event.key == pygame.K_2 and len(self.upgrade_options) >= 2:
                            upgrades.apply_upgrade(self.player, self.upgrade_options[1])
                            self.state = "PLAY"
                        elif event.key == pygame.K_3 and len(self.upgrade_options) >= 3:
                            upgrades.apply_upgrade(self.player, self.upgrade_options[2])
                            self.state = "PLAY"

            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
