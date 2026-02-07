"""Core game loop and state."""

from __future__ import annotations

import math
import random
import sys

import pygame

from game import assets
from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.particle import Particle
from game.entities.player import Player
from game.entities.xpgem import XPGem
from game.input import handle_player_input
from game.settings import (
    BG,
    BULLET_RADIUS,
    ENEMY_RADIUS,
    FPS,
    HEIGHT,
    NEON_BLUE,
    NEON_CYAN,
    NEON_GREEN,
    NEON_YELLOW,
    PLAYER_RADIUS,
    RED,
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
        self.particles: list[Particle] = []

        self.fire_timer = 0.0
        self.shake_timer = 0.0
        self.shake_strength = 0.0

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
        self.particles.clear()
        self.fire_timer = 0.0
        self.shake_timer = 0.0
        self.shake_strength = 0.0
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

        self.spawner.update(dt, self.elapsed, self.enemies, self.player.pos)

        # Use player's fire cooldown
        fire_cd = self.player.get_fire_cooldown()
        self.fire_timer += dt
        while self.fire_timer >= fire_cd:
            self.fire_timer -= fire_cd
            bullet = combat.fire_minigun(self.player, self.enemies)
            if bullet:
                self.bullets.append(bullet)
                self._spawn_muzzle_flash(bullet)

        combat.update_bullets(self.bullets, dt)
        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.ttl > 0 and -80 < bullet.x < WIDTH + 80 and -80 < bullet.y < HEIGHT + 80
        ]

        collisions.update_enemy_positions(self.enemies, self.player, dt)
        death_positions: list[tuple[float, float]] = []
        hit_positions: list[tuple[float, float]] = []
        collisions.resolve_bullet_hits(
            self.bullets,
            self.enemies,
            self.player,
            self.xpgems,
            death_positions,
            hit_positions,
        )
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
        total_damage = collisions.resolve_player_hits(self.player, self.enemies, dt)
        if total_damage > 0:
            self._add_screen_shake(min(6.0, 2.0 + total_damage * 1.5))

        for pos in death_positions:
            self._spawn_explosion(pos, RED, 12)
            self._add_screen_shake(5.0)

        for pos in hit_positions:
            self._spawn_hit_sparks(pos)

        # Update XP gems
        leveled_up = xp.update_xp_gems(self.xpgems, self.player, dt)
        
        # Level up
        if leveled_up:
            self.state = "LEVEL_UP"
            self.upgrade_options = upgrades.generate_upgrade_options(self.player)

        # Check death
        if self.player.hp <= 0:
            self.player.hp = 0
            self._spawn_explosion(self.player.pos, NEON_BLUE, 18)
            self._add_screen_shake(10.0)
            self.state = "LOSE"

        self._update_particles(dt)
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def draw(self) -> None:
        shake_x, shake_y = self._get_shake_offset()
        self.screen.fill(BG)
        self._draw_background(shake_x, shake_y)

        # Draw XP gems
        for gem in self.xpgems:
            # Pulse effect
            pulse = int(5 * (1 + 0.3 * (gem.x % 100) / 100))
            pygame.draw.circle(
                self.screen,
                NEON_GREEN,
                (int(gem.x + shake_x), int(gem.y + shake_y)),
                pulse,
                0,
            )
            pygame.draw.circle(
                self.screen,
                NEON_CYAN,
                (int(gem.x + shake_x), int(gem.y + shake_y)),
                pulse + 2,
                1,
            )

        for bullet in self.bullets:
            pygame.draw.line(
                self.screen,
                NEON_YELLOW,
                (int(bullet.prev_x + shake_x), int(bullet.prev_y + shake_y)),
                (int(bullet.x + shake_x), int(bullet.y + shake_y)),
                2,
            )
            pygame.draw.circle(
                self.screen,
                NEON_YELLOW,
                (int(bullet.x + shake_x), int(bullet.y + shake_y)),
                BULLET_RADIUS,
            )

        for enemy in self.enemies:
            pygame.draw.circle(
                self.screen,
                RED,
                (int(enemy.x + shake_x), int(enemy.y + shake_y)),
                ENEMY_RADIUS,
                2,
            )
            pygame.draw.circle(
                self.screen,
                (60, 0, 0),
                (int(enemy.x + shake_x), int(enemy.y + shake_y)),
                ENEMY_RADIUS - 3,
                0,
            )

        px, py = self.player.pos
        triangle = self._get_player_triangle(px + shake_x, py + shake_y)
        pygame.draw.polygon(self.screen, (20, 40, 80), triangle, 0)
        pygame.draw.polygon(self.screen, NEON_BLUE, triangle, 2)
        
        # Draw shield if active
        if self.player.shield_level > 0 and self.player.shield_hp > 0:
            shield_radius = PLAYER_RADIUS + 5
            pygame.draw.circle(
                self.screen,
                (100, 100, 255),
                (int(px + shake_x), int(py + shake_y)),
                shield_radius,
                2,
            )

        self._draw_particles(shake_x, shake_y)

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

    def _get_shake_offset(self) -> tuple[float, float]:
        if self.shake_timer <= 0:
            return (0.0, 0.0)
        ratio = min(1.0, self.shake_timer / 0.18)
        strength = self.shake_strength * ratio
        return (
            random.uniform(-strength, strength),
            random.uniform(-strength, strength),
        )

    def _add_screen_shake(self, strength: float) -> None:
        self.shake_strength = max(self.shake_strength, strength)
        self.shake_timer = max(self.shake_timer, 0.18)

    def _update_particles(self, dt: float) -> None:
        for particle in self.particles:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.ttl -= dt
            particle.vx *= 0.98
            particle.vy *= 0.98
        self.particles = [p for p in self.particles if p.ttl > 0]

    def _draw_particles(self, shake_x: float, shake_y: float) -> None:
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle.color,
                (int(particle.x + shake_x), int(particle.y + shake_y)),
                max(1, int(particle.radius)),
            )

    def _spawn_explosion(
        self, pos: tuple[float, float], color: tuple[int, int, int], count: int
    ) -> None:
        x, y = pos
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(120, 280)
            radius = random.uniform(1.5, 3.5)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    ttl=random.uniform(0.3, 0.6),
                    radius=radius,
                    color=color,
                )
            )

    def _spawn_hit_sparks(self, pos: tuple[float, float]) -> None:
        x, y = pos
        for _ in range(4):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(60, 160)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    ttl=random.uniform(0.12, 0.25),
                    radius=random.uniform(1.0, 2.0),
                    color=NEON_YELLOW,
                )
            )

    def _spawn_muzzle_flash(self, bullet: Bullet) -> None:
        angle = math.atan2(bullet.vy, bullet.vx)
        for _ in range(3):
            jitter = random.uniform(-0.6, 0.6)
            speed = random.uniform(140, 240)
            self.particles.append(
                Particle(
                    x=bullet.x,
                    y=bullet.y,
                    vx=math.cos(angle + jitter) * speed,
                    vy=math.sin(angle + jitter) * speed,
                    ttl=random.uniform(0.08, 0.15),
                    radius=random.uniform(1.0, 2.0),
                    color=NEON_YELLOW,
                )
            )

    def _draw_background(self, shake_x: float, shake_y: float) -> None:
        spacing = 60
        offset_x = (self.player.x * 0.3 + self.elapsed * 24) % spacing
        offset_y = (self.player.y * 0.3 + self.elapsed * 18) % spacing
        grid_color = (12, 12, 24)

        for x in range(-spacing, WIDTH + spacing, spacing):
            xpos = x - offset_x + shake_x
            pygame.draw.line(
                self.screen,
                grid_color,
                (int(xpos), int(0 + shake_y)),
                (int(xpos), int(HEIGHT + shake_y)),
                1,
            )
        for y in range(-spacing, HEIGHT + spacing, spacing):
            ypos = y - offset_y + shake_y
            pygame.draw.line(
                self.screen,
                grid_color,
                (int(0 + shake_x), int(ypos)),
                (int(WIDTH + shake_x), int(ypos)),
                1,
            )

    def _get_player_triangle(self, x: float, y: float) -> list[tuple[float, float]]:
        size = PLAYER_RADIUS + 4
        return [
            (x, y - size),
            (x - size * 0.85, y + size * 0.7),
            (x + size * 0.85, y + size * 0.7),
        ]
