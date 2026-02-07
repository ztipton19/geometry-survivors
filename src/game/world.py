"""Core game loop and state."""

from __future__ import annotations

import math
import random
import sys

import pygame

from game import assets, settings
from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.particle import Particle
from game.entities.emp_pulse import EmpPulse
from game.entities.laser import LaserBeam
from game.entities.player import Player
from game.entities.rocket import Rocket
from game.entities.xpgem import XPGem
from game.input import handle_player_input
from game.settings import (
    BG,
    BULLET_RADIUS,
    EMP_PULSE_LIFETIME,
    FPS,
    LASER_LIFETIME,
    LASER_WIDTH,
    NEON_BLUE,
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_ORANGE,
    NEON_YELLOW,
    PLAYER_RADIUS,
    RED,
)
from game.systems import collisions, combat, progression, spawner, upgrades, xp
from game.ui import (
    draw_end_screen,
    draw_hud,
    draw_intro_screen,
    get_level_up_card_rects,
    draw_level_up_screen,
    draw_options_menu,
    draw_pause_menu,
    draw_start_menu,
)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Neon Survivors (prototype)")
        self.fullscreen = False
        self.available_resolutions = [
            ("Default (1100x700)", (settings.WIDTH, settings.HEIGHT)),
            ("720p (1280x720)", (1280, 720)),
            ("1080p (1920x1080)", (1920, 1080)),
        ]
        self.resolution_index = 0
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font, self.big_font = assets.load_fonts()

        self.player = Player(settings.WIDTH / 2, settings.HEIGHT / 2)
        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []
        self.rockets: list[Rocket] = []
        self.lasers: list[LaserBeam] = []
        self.emp_pulses: list[EmpPulse] = []
        self.xpgems: list[XPGem] = []
        self.particles: list[Particle] = []

        self.fire_timer = 0.0
        self.rocket_timer = 0.0
        self.laser_timer = 0.0
        self.emp_timer = 0.0
        self.shake_timer = 0.0
        self.shake_strength = 0.0

        self.spawner = spawner.Spawner()
        self.elapsed, self.remaining = progression.reset_timer()

        self.running = True
        self.state = "MENU"
        self.menu_selection = 0
        self.options_selection = 0
        self.pause_selection = 0
        
        # Upgrade system
        self.upgrade_options: list[str] = []
        self.upgrade_resume_grace = 0.0

    def restart(self) -> None:
        self.player = Player(settings.WIDTH / 2, settings.HEIGHT / 2)
        self.enemies.clear()
        self.bullets.clear()
        self.rockets.clear()
        self.lasers.clear()
        self.emp_pulses.clear()
        self.xpgems.clear()
        self.particles.clear()
        self.fire_timer = 0.0
        self.rocket_timer = 0.0
        self.laser_timer = 0.0
        self.emp_timer = 0.0
        self.shake_timer = 0.0
        self.shake_strength = 0.0
        self.spawner.reset()
        self.elapsed, self.remaining = progression.reset_timer()
        self.state = "PLAY"
        self.upgrade_options.clear()
        self.upgrade_resume_grace = 0.0

    def update(self, dt: float) -> None:
        if self.state != "PLAY":
            return
        if self.upgrade_resume_grace > 0:
            self.upgrade_resume_grace = max(0.0, self.upgrade_resume_grace - dt)
            return

        self.elapsed, self.remaining, completed = progression.update_timer(
            self.elapsed, self.remaining, dt
        )
        if completed:
            self.state = "WIN"
            return

        handle_player_input(self.player, dt)

        self.spawner.update(dt, self.elapsed, self.enemies, self.player.pos)

        death_positions: list[tuple[float, float]] = []
        hit_positions: list[tuple[float, float]] = []

        # Use player's fire cooldown
        fire_cd = self.player.get_fire_cooldown()
        self.fire_timer += dt
        while self.fire_timer >= fire_cd:
            self.fire_timer -= fire_cd
            bullet = combat.fire_minigun(self.player, self.enemies)
            if bullet:
                self.bullets.append(bullet)
                self._spawn_muzzle_flash(bullet)

        if self.player.rockets_level >= 0:
            rocket_stats = self.player.get_rocket_stats()
            self.rocket_timer += dt
            while self.rocket_timer >= rocket_stats["fire_cooldown"]:
                self.rocket_timer -= rocket_stats["fire_cooldown"]
                target_pos = pygame.mouse.get_pos()
                self.rockets.append(combat.fire_rocket(self.player, target_pos))

        if self.player.laser_level >= 0:
            laser_stats = self.player.get_laser_stats()
            self.laser_timer += dt
            if self.laser_timer >= laser_stats["fire_cooldown"]:
                self.laser_timer -= laser_stats["fire_cooldown"]
                px, py = self.player.pos
                tx, ty = pygame.mouse.get_pos()
                beam = LaserBeam(px, py, tx, ty, LASER_LIFETIME)
                self.lasers.append(beam)
                collisions.resolve_laser_hits(
                    self.player,
                    self.enemies,
                    (px, py),
                    (tx, ty),
                    laser_stats["damage"],
                    LASER_WIDTH,
                    self.xpgems,
                    death_positions,
                    hit_positions,
                )

        if self.player.emp_level >= 0:
            emp_stats = self.player.get_emp_stats()
            self.emp_timer += dt
            if self.emp_timer >= 0.5:
                self.emp_timer -= 0.5
                self.emp_pulses.append(
                    EmpPulse(
                        x=self.player.x,
                        y=self.player.y,
                        radius=emp_stats["radius"],
                        ttl=EMP_PULSE_LIFETIME,
                    )
                )
                for enemy in self.enemies:
                    if (enemy.x - self.player.x) ** 2 + (enemy.y - self.player.y) ** 2 <= emp_stats[
                        "radius"
                    ] ** 2:
                        collisions.apply_enemy_damage(
                            enemy,
                            emp_stats["damage"],
                            self.player,
                            self.xpgems,
                            death_positions,
                            hit_positions,
                            (enemy.x, enemy.y),
                        )

        combat.update_bullets(self.bullets, dt)
        combat.update_rockets(self.rockets, dt)
        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.ttl > 0
            and -80 < bullet.x < settings.WIDTH + 80
            and -80 < bullet.y < settings.HEIGHT + 80
        ]
        self.rockets = [
            rocket
            for rocket in self.rockets
            if rocket.ttl > 0
            and -120 < rocket.x < settings.WIDTH + 120
            and -120 < rocket.y < settings.HEIGHT + 120
        ]
        self.lasers = [laser for laser in self.lasers if laser.ttl > 0]

        collisions.update_enemy_positions(self.enemies, self.player, dt)
        collisions.resolve_bullet_hits(
            self.bullets,
            self.enemies,
            self.player,
            self.xpgems,
            death_positions,
            hit_positions,
        )
        collisions.resolve_rocket_hits(
            self.rockets,
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
            if self.player.shield_level >= 0:
                self.player.shield_regen_delay = self.player.get_shield_regen_delay()

        if self.player.shield_level >= 0:
            self.player.shield_max = self.player.get_shield_max()
            if self.player.shield_hp < self.player.shield_max:
                if self.player.shield_regen_delay > 0:
                    self.player.shield_regen_delay = max(
                        0.0, self.player.shield_regen_delay - dt
                    )
                else:
                    regen_rate = self.player.get_shield_regen_rate()
                    self.player.shield_hp = min(
                        self.player.shield_max, self.player.shield_hp + regen_rate * dt
                    )

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
        for laser in self.lasers:
            laser.ttl -= dt
        for pulse in self.emp_pulses:
            pulse.ttl -= dt
        self.emp_pulses = [pulse for pulse in self.emp_pulses if pulse.ttl > 0]
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def draw(self) -> None:
        if self.state in ("PLAY", "LEVEL_UP", "PAUSE", "WIN", "LOSE"):
            shake_x, shake_y = self._get_shake_offset()
        else:
            shake_x, shake_y = (0.0, 0.0)
        self.screen.fill(BG)
        self._draw_background(shake_x, shake_y)

        if self.state == "MENU":
            draw_start_menu(self.screen, self.font, self.big_font, self.menu_selection)
            pygame.display.flip()
            return
        if self.state == "OPTIONS":
            resolution_label = self.available_resolutions[self.resolution_index][0]
            draw_options_menu(
                self.screen,
                self.font,
                self.big_font,
                self.options_selection,
                resolution_label,
                self.fullscreen,
            )
            pygame.display.flip()
            return
        if self.state == "INTRO":
            draw_intro_screen(self.screen, self.font, self.big_font)
            pygame.display.flip()
            return

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

        for rocket in self.rockets:
            pygame.draw.line(
                self.screen,
                NEON_ORANGE,
                (int(rocket.prev_x + shake_x), int(rocket.prev_y + shake_y)),
                (int(rocket.x + shake_x), int(rocket.y + shake_y)),
                3,
            )
            pygame.draw.circle(
                self.screen,
                NEON_ORANGE,
                (int(rocket.x + shake_x), int(rocket.y + shake_y)),
                6,
            )

        for laser in self.lasers:
            pygame.draw.line(
                self.screen,
                NEON_CYAN,
                (int(laser.start_x + shake_x), int(laser.start_y + shake_y)),
                (int(laser.end_x + shake_x), int(laser.end_y + shake_y)),
                LASER_WIDTH,
            )

        for pulse in self.emp_pulses:
            alpha = int(200 * (pulse.ttl / EMP_PULSE_LIFETIME))
            width, height = self.screen.get_size()
            pulse_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(
                pulse_surface,
                (*NEON_MAGENTA, alpha),
                (int(pulse.x + shake_x), int(pulse.y + shake_y)),
                int(pulse.radius),
                2,
            )
            self.screen.blit(pulse_surface, (0, 0))

        for enemy in self.enemies:
            self._draw_enemy(enemy, shake_x, shake_y)

        px, py = self.player.pos
        triangle = self._get_player_triangle(px + shake_x, py + shake_y)
        pygame.draw.polygon(self.screen, (20, 40, 80), triangle, 0)
        pygame.draw.polygon(self.screen, NEON_BLUE, triangle, 2)
        
        # Draw shield if active
        if self.player.shield_level >= 0 and self.player.shield_hp > 0:
            shield_radius = PLAYER_RADIUS + 6
            shield_ratio = 0.0
            if self.player.shield_max > 0:
                shield_ratio = max(0.0, min(1.0, self.player.shield_hp / self.player.shield_max))
            shield_color = (
                int(80 + 70 * shield_ratio),
                int(120 + 80 * shield_ratio),
                255,
            )
            pygame.draw.circle(
                self.screen,
                shield_color,
                (int(px + shake_x), int(py + shake_y)),
                shield_radius,
                2,
            )

        self._draw_particles(shake_x, shake_y)

        draw_hud(
            self.screen,
            self.font,
            self.player,
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
                self.player,
            )

        if self.state == "PAUSE":
            draw_pause_menu(self.screen, self.font, self.big_font, self.pause_selection)
        
        draw_end_screen(self.screen, self.font, self.big_font, self.state, self.player)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == "MENU":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.menu_selection = (self.menu_selection - 1) % 3
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.menu_selection = (self.menu_selection + 1) % 3
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if self.menu_selection == 0:
                                self.restart()
                                self.state = "INTRO"
                            elif self.menu_selection == 1:
                                self.state = "OPTIONS"
                            elif self.menu_selection == 2:
                                self.running = False
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                    elif self.state == "OPTIONS":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.options_selection = (self.options_selection - 1) % 3
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.options_selection = (self.options_selection + 1) % 3
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            if self.options_selection == 0:
                                self.resolution_index = (self.resolution_index - 1) % len(
                                    self.available_resolutions
                                )
                                self._apply_display_mode()
                            elif self.options_selection == 1:
                                self.fullscreen = not self.fullscreen
                                self._apply_display_mode()
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if self.options_selection == 0:
                                self.resolution_index = (self.resolution_index + 1) % len(
                                    self.available_resolutions
                                )
                                self._apply_display_mode()
                            elif self.options_selection == 1:
                                self.fullscreen = not self.fullscreen
                                self._apply_display_mode()
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if self.options_selection == 2:
                                self.state = "MENU"
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "MENU"
                    elif self.state == "INTRO":
                        self.state = "PLAY"
                    elif self.state == "PLAY":
                        if event.key == pygame.K_ESCAPE:
                            self.state = "PAUSE"
                    elif self.state == "PAUSE":
                        if event.key == pygame.K_ESCAPE:
                            self.state = "PLAY"
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            self.pause_selection = (self.pause_selection - 1) % 3
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.pause_selection = (self.pause_selection + 1) % 3
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if self.pause_selection == 0:
                                self.state = "PLAY"
                            elif self.pause_selection == 1:
                                self.restart()
                            elif self.pause_selection == 2:
                                self.state = "MENU"
                    elif self.state in ("WIN", "LOSE"):
                        if event.key == pygame.K_r:
                            self.restart()
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                    # Level-up key selection
                    if self.state == "LEVEL_UP":
                        if event.key == pygame.K_1 and len(self.upgrade_options) >= 1:
                            self._select_upgrade(0)
                        elif event.key == pygame.K_2 and len(self.upgrade_options) >= 2:
                            self._select_upgrade(1)
                        elif event.key == pygame.K_3 and len(self.upgrade_options) >= 3:
                            self._select_upgrade(2)
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.state == "LEVEL_UP"
                ):
                    card_rects = get_level_up_card_rects(
                        self.screen, len(self.upgrade_options)
                    )
                    for i, rect in enumerate(card_rects):
                        if rect.collidepoint(event.pos):
                            self._select_upgrade(i)
                            break

            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def _apply_display_mode(self) -> None:
        _, (width, height) = self.available_resolutions[self.resolution_index]
        settings.WIDTH = width
        settings.HEIGHT = height
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        self.font, self.big_font = assets.load_fonts()
        self.player.x = min(max(self.player.x, PLAYER_RADIUS), settings.WIDTH - PLAYER_RADIUS)
        self.player.y = min(max(self.player.y, PLAYER_RADIUS), settings.HEIGHT - PLAYER_RADIUS)

    def _select_upgrade(self, index: int) -> None:
        if index < 0 or index >= len(self.upgrade_options):
            return
        upgrades.apply_upgrade(self.player, self.upgrade_options[index])
        self.state = "PLAY"
        self.upgrade_options.clear()
        self.upgrade_resume_grace = 0.5

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

        for x in range(-spacing, settings.WIDTH + spacing, spacing):
            xpos = x - offset_x + shake_x
            pygame.draw.line(
                self.screen,
                grid_color,
                (int(xpos), int(0 + shake_y)),
                (int(xpos), int(settings.HEIGHT + shake_y)),
                1,
            )
        for y in range(-spacing, settings.HEIGHT + spacing, spacing):
            ypos = y - offset_y + shake_y
            pygame.draw.line(
                self.screen,
                grid_color,
                (int(0 + shake_x), int(ypos)),
                (int(settings.WIDTH + shake_x), int(ypos)),
                1,
            )

    def _get_player_triangle(self, x: float, y: float) -> list[tuple[float, float]]:
        size = PLAYER_RADIUS + 4
        return [
            (x, y - size),
            (x - size * 0.85, y + size * 0.7),
            (x + size * 0.85, y + size * 0.7),
        ]

    def _draw_enemy(self, enemy: Enemy, shake_x: float, shake_y: float) -> None:
        ex = enemy.x + shake_x
        ey = enemy.y + shake_y
        outline_color = NEON_MAGENTA if enemy.is_boss else RED
        fill_color = (80, 0, 80) if enemy.is_boss else (60, 0, 0)

        if enemy.sides <= 1:
            pygame.draw.circle(
                self.screen,
                outline_color,
                (int(ex), int(ey)),
                int(enemy.radius),
                2,
            )
            pygame.draw.circle(
                self.screen,
                fill_color,
                (int(ex), int(ey)),
                max(1, int(enemy.radius - 3)),
                0,
            )
            return

        points = self._get_polygon_points(ex, ey, enemy.radius, enemy.sides)
        inner_points = self._get_polygon_points(ex, ey, max(1.0, enemy.radius - 3), enemy.sides)
        pygame.draw.polygon(self.screen, outline_color, points, 2)
        pygame.draw.polygon(self.screen, fill_color, inner_points, 0)

    def _get_polygon_points(
        self, x: float, y: float, radius: float, sides: int
    ) -> list[tuple[float, float]]:
        angle_offset = -math.pi / 2
        step = math.tau / sides
        return [
            (
                x + math.cos(angle_offset + step * i) * radius,
                y + math.sin(angle_offset + step * i) * radius,
            )
            for i in range(sides)
        ]
