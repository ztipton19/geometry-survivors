"""Core game loop and state."""

from __future__ import annotations

import math
import random

import pygame

from game import assets, settings
from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.particle import Particle
from game.entities.emp_pulse import EmpPulse
from game.entities.laser import LaserBeam
from game.entities.mine import Mine
from game.entities.player import Player
from game.entities.rocket import Rocket
from game.entities.xpgem import XPGem
from game.cutscene import Cutscene
from game.debug_overlay import DebugOverlay
from game.input import handle_player_input
from game.physics import (
    attach_body,
    clamp_entity_speeds,
    create_space,
    remove_body,
    step_space,
    sync_entity_positions,
    update_enemy_ai,
)
from game.settings import (
    BG,
    BULLET_RADIUS,
    EMP_PULSE_LIFETIME,
    FPS,
    LASER_LIFETIME,
    LASER_WIDTH,
    HURDLE_COOLDOWN,
    NEON_BLUE,
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_ORANGE,
    NEON_YELLOW,
    PLAYER_RADIUS,
    RED,
    WHITE,
    get_ship_selection_colors,
)
from game.systems import collisions, combat, progression, spawner, upgrades, xp
from game.ui import (
    draw_end_screen,
    draw_hud,
    get_level_up_card_rects,
    draw_level_up_screen,
    draw_options_menu,
    draw_pause_menu,
    draw_start_menu,
)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Clone Protocol (prototype)")
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
        self.space = create_space()
        attach_body(self.space, self.player, PLAYER_RADIUS)
        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []
        self.rockets: list[Rocket] = []
        self.lasers: list[LaserBeam] = []
        self.emp_pulses: list[EmpPulse] = []
        self.mines: list[Mine] = []
        self.xpgems: list[XPGem] = []
        self.particles: list[Particle] = []

        self.fire_timer = 0.0
        self.rocket_timer = 0.0
        self.laser_timer = 0.0
        self.emp_timer = 0.0
        self.mine_timer = 0.0
        self.shake_timer = 0.0
        self.shake_strength = 0.0

        self.spawner = spawner.Spawner()
        self.elapsed, self.remaining = progression.reset_timer()

        self.running = True
        self.state = "MENU"
        self.menu_selection = 0
        self.options_selection = 0
        self.pause_selection = 0
        self.cutscene: Cutscene | None = None
        self.cutscene_font = pygame.font.SysFont("consolas", 24)
        self.debug_overlay = DebugOverlay(self)

        self.background_seed = 1337
        self.star_chunk_size = 500
        self.nebula_chunk_size = 2000
        self.star_chunks: dict[tuple[int, int], list[dict[str, object]]] = {}
        self.nebula_chunks: dict[tuple[int, int], list[dict[str, object]]] = {}
        self.shooting_stars: list[dict[str, float]] = []
        self.vignette_surface: pygame.Surface | None = None
        self.vignette_size: tuple[int, int] | None = None
        
        # Upgrade system
        self.upgrade_options: list[str] = []
        self.upgrade_resume_grace = 0.0

    def restart(self) -> None:
        self.player = Player(settings.WIDTH / 2, settings.HEIGHT / 2)
        self.space = create_space()
        attach_body(self.space, self.player, PLAYER_RADIUS)
        self.enemies.clear()
        self.bullets.clear()
        self.rockets.clear()
        self.lasers.clear()
        self.emp_pulses.clear()
        self.mines.clear()
        self.xpgems.clear()
        self.particles.clear()
        self.fire_timer = 0.0
        self.rocket_timer = 0.0
        self.laser_timer = 0.0
        self.emp_timer = 0.0
        self.mine_timer = 0.0
        self.shake_timer = 0.0
        self.shake_strength = 0.0
        self.shooting_stars.clear()
        self.spawner.reset()
        self.elapsed, self.remaining = progression.reset_timer()
        self.state = "PLAY"
        self.upgrade_options.clear()
        self.upgrade_resume_grace = 0.0
        self.cutscene = None
        self.debug_overlay.params["collision_enabled"] = True

    def _start_intro_cutscene(self) -> None:
        intro_text = (
            "Mission Brief: Clone Pilot #2847\n\n"
            "You are one of thousands. Every pilot before you has been lost to the void.\n"
            "Each clone carries the combat data of those who came before.\n"
            "Your mission: gather more data. Survive as long as you can.\n\n"
            "The enemy is unknown. Their origin is unknown.\n"
            "But they are endless.\n\n"
            "Good luck, pilot. You'll need it."
        )
        self.cutscene = Cutscene(intro_text, typing_speed=40.0)
        self.state = "CUTSCENE"

    def update(self, dt: float) -> None:
        if self.state == "CUTSCENE":
            if self.cutscene:
                self.cutscene.update(dt)
            return
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
        self.debug_overlay.apply_to_game()

        self.spawner.update(dt, self.elapsed, self.enemies, self.player.pos)
        for enemy in self.enemies:
            attach_body(self.space, enemy, enemy.radius)
        update_enemy_ai(self.enemies, self.player.pos, dt)
        step_space(self.space, dt)
        clamp_entity_speeds(self.player, self.enemies)
        sync_entity_positions([self.player])
        sync_entity_positions(self.enemies)

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
                target_pos = self._screen_to_world(pygame.mouse.get_pos())
                self.rockets.append(combat.fire_rocket(self.player, target_pos))

        collisions_enabled = bool(self.debug_overlay.params["collision_enabled"])

        if self.player.laser_level >= 0:
            laser_stats = self.player.get_laser_stats()
            self.laser_timer += dt
            if self.laser_timer >= laser_stats["fire_cooldown"]:
                self.laser_timer -= laser_stats["fire_cooldown"]
                px, py = self.player.pos
                mx, my = self._screen_to_world(pygame.mouse.get_pos())
                dx, dy = mx - px, my - py
                length = max(self.screen.get_width(), self.screen.get_height()) * 1.25
                if dx == 0 and dy == 0:
                    nx, ny = (0.0, -1.0)
                else:
                    mag = math.hypot(dx, dy)
                    nx, ny = (dx / mag, dy / mag)
                tx = px + nx * length
                ty = py + ny * length
                beam = LaserBeam(px, py, tx, ty, LASER_LIFETIME)
                self.lasers.append(beam)
                if collisions_enabled:
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
                if collisions_enabled:
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

        if self.player.mines_level >= 0:
            mine_stats = self.player.get_mine_stats()
            self.mine_timer += dt
            while self.mine_timer >= mine_stats["drop_cooldown"]:
                self.mine_timer -= mine_stats["drop_cooldown"]
                angle = 0.0
                if self.player.body is not None:
                    angle = float(self.player.body.angle)
                drop_distance = PLAYER_RADIUS + 18
                back_dx = -math.sin(angle)
                back_dy = math.cos(angle)
                mine_x = self.player.x + back_dx * drop_distance
                mine_y = self.player.y + back_dy * drop_distance
                self.mines.append(
                    Mine(
                        x=mine_x,
                        y=mine_y,
                        ttl=15.0,
                        damage=55.0,
                        splash_radius=80.0,
                        trigger_radius=24.0,
                    )
                )

        combat.update_bullets(self.bullets, dt)
        combat.update_rockets(self.rockets, dt)
        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.ttl > 0
        ]
        self.rockets = [
            rocket
            for rocket in self.rockets
            if rocket.ttl > 0
        ]
        self.lasers = [laser for laser in self.lasers if laser.ttl > 0]
        for mine in self.mines:
            mine.ttl -= dt
        self.mines = [mine for mine in self.mines if mine.ttl > 0]

        if collisions_enabled:
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
            collisions.resolve_mine_hits(
                self.mines,
                self.enemies,
                self.player,
                self.xpgems,
                death_positions,
                hit_positions,
            )
        alive_enemies: list[Enemy] = []
        for enemy in self.enemies:
            if enemy.hp > 0:
                alive_enemies.append(enemy)
            else:
                remove_body(self.space, enemy)
        self.enemies = alive_enemies
        total_damage = collisions.resolve_player_hits(self.player, self.enemies, dt) if collisions_enabled else 0.0
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

        for pos in hit_positions:
            self._spawn_hit_sparks(pos)

        # Update XP gems
        leveled_up = xp.update_xp_gems(self.xpgems, self.player, dt)
        
        # Level up
        if leveled_up:
            self.upgrade_options = upgrades.generate_upgrade_options(self.player)
            if self.upgrade_options:
                self.state = "LEVEL_UP"
            else:
                # No upgrades remain; continue play without opening level-up UI.
                self.state = "PLAY"

        # Check death
        if self.player.hp <= 0:
            self.player.hp = 0
            self._spawn_explosion(self.player.pos, NEON_BLUE, 18)
            self._add_screen_shake(10.0)
            self.state = "LOSE"

        self._update_particles(dt)
        self._spawn_engine_particles()  # Continuous engine thrust particles
        for laser in self.lasers:
            laser.ttl -= dt
        for pulse in self.emp_pulses:
            pulse.ttl -= dt
        self.emp_pulses = [pulse for pulse in self.emp_pulses if pulse.ttl > 0]
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)
        self._update_shooting_stars(dt)

    def draw(self) -> None:
        if self.state in ("PLAY", "LEVEL_UP", "PAUSE", "WIN", "LOSE"):
            shake_x, shake_y = self._get_shake_offset()
            cam_x, cam_y = self._get_camera_origin()
        else:
            shake_x, shake_y = (0.0, 0.0)
            cam_x, cam_y = (0.0, 0.0)
        self.screen.fill(BG)
        self._draw_background(cam_x, cam_y, shake_x, shake_y)

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
        if self.state == "CUTSCENE" and self.cutscene:
            self.cutscene.draw(self.screen, self.cutscene_font)
            pygame.display.flip()
            return

        # Draw XP gems
        for gem in self.xpgems:
            # Pulse effect
            pulse = int(5 * (1 + 0.3 * (gem.x % 100) / 100))
            gx, gy = self._world_to_screen(gem.x, gem.y, cam_x, cam_y, shake_x, shake_y)
            pygame.draw.circle(
                self.screen,
                NEON_GREEN,
                (gx, gy),
                pulse,
                0,
            )
            pygame.draw.circle(
                self.screen,
                NEON_CYAN,
                (gx, gy),
                pulse + 2,
                1,
            )

        for bullet in self.bullets:
            prev_x, prev_y = self._world_to_screen(
                bullet.prev_x, bullet.prev_y, cam_x, cam_y, shake_x, shake_y
            )
            bullet_x, bullet_y = self._world_to_screen(
                bullet.x, bullet.y, cam_x, cam_y, shake_x, shake_y
            )
            pygame.draw.line(
                self.screen,
                NEON_YELLOW,
                (prev_x, prev_y),
                (bullet_x, bullet_y),
                2,
            )
            pygame.draw.circle(
                self.screen,
                NEON_YELLOW,
                (bullet_x, bullet_y),
                BULLET_RADIUS,
            )

        for rocket in self.rockets:
            prev_x, prev_y = self._world_to_screen(
                rocket.prev_x, rocket.prev_y, cam_x, cam_y, shake_x, shake_y
            )
            rocket_x, rocket_y = self._world_to_screen(
                rocket.x, rocket.y, cam_x, cam_y, shake_x, shake_y
            )
            pygame.draw.line(
                self.screen,
                NEON_ORANGE,
                (prev_x, prev_y),
                (rocket_x, rocket_y),
                3,
            )
            pygame.draw.circle(
                self.screen,
                NEON_ORANGE,
                (rocket_x, rocket_y),
                6,
            )

        for laser in self.lasers:
            start_x, start_y = self._world_to_screen(
                laser.start_x, laser.start_y, cam_x, cam_y, shake_x, shake_y
            )
            end_x, end_y = self._world_to_screen(
                laser.end_x, laser.end_y, cam_x, cam_y, shake_x, shake_y
            )
            pygame.draw.line(
                self.screen,
                NEON_CYAN,
                (start_x, start_y),
                (end_x, end_y),
                LASER_WIDTH,
            )

        for pulse in self.emp_pulses:
            alpha = int(200 * (pulse.ttl / EMP_PULSE_LIFETIME))
            width, height = self.screen.get_size()
            pulse_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(
                pulse_surface,
                (*NEON_MAGENTA, alpha),
                self._world_to_screen(pulse.x, pulse.y, cam_x, cam_y, shake_x, shake_y),
                int(pulse.radius),
                2,
            )
            self.screen.blit(pulse_surface, (0, 0))

        for mine in self.mines:
            mine_x, mine_y = self._world_to_screen(
                mine.x, mine.y, cam_x, cam_y, shake_x, shake_y
            )
            pygame.draw.circle(self.screen, NEON_ORANGE, (mine_x, mine_y), 8, 2)
            pygame.draw.circle(self.screen, RED, (mine_x, mine_y), 3, 0)

        for enemy in self.enemies:
            self._draw_enemy(enemy, cam_x, cam_y, shake_x, shake_y)

        px, py = self.player.pos
        screen_px, screen_py = self._world_to_screen(px, py, cam_x, cam_y, shake_x, shake_y)
        angle = 0.0
        if self.player.body is not None:
            angle = float(self.player.body.angle)
        ship_colors = get_ship_selection_colors()
        catamaran_polys, front_point = self._get_player_catamaran(screen_px, screen_py, angle)
        for poly in catamaran_polys:
            pygame.draw.polygon(self.screen, ship_colors["ship_fill"], poly, 0)
            pygame.draw.polygon(self.screen, ship_colors["ship_outline"], poly, 2)

        # Draw bright front tip glow for directionality
        front_x, front_y = front_point
        pygame.draw.circle(self.screen, ship_colors["ship_tip"], (int(front_x), int(front_y)), 3, 0)
        pygame.draw.circle(self.screen, ship_colors["ship_tip"], (int(front_x), int(front_y)), 5, 1)
        
        # Draw shield if active
        if self.player.shield_level >= 0 and self.player.shield_hp > 0:
            # Keep shield clearly outside the player triangle.
            ship_outer_radius = PLAYER_RADIUS + 4
            shield_radius = int(ship_outer_radius + 8)
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
                (screen_px, screen_py),
                shield_radius,
                3,
            )

        self._draw_particles(cam_x, cam_y, shake_x, shake_y)
        self._draw_vignette()

        draw_hud(
            self.screen,
            self.font,
            self.player,
            self.remaining,
            self._get_weapon_slots(),
            self._get_utility_slots(),
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
        if self.state in ("PLAY", "LEVEL_UP", "PAUSE"):
            self.debug_overlay.draw(self.screen)

        pygame.display.flip()

    def run(self) -> None:
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F3:
                            self.debug_overlay.toggle()
                            continue
                        if self.state == "PLAY" and self.debug_overlay.handle_input(event):
                            continue
                        if self.state == "MENU":
                            if event.key in (pygame.K_UP, pygame.K_w):
                                self.menu_selection = (self.menu_selection - 1) % 3
                            elif event.key in (pygame.K_DOWN, pygame.K_s):
                                self.menu_selection = (self.menu_selection + 1) % 3
                            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                                if self.menu_selection == 0:
                                    self.restart()
                                    self._start_intro_cutscene()
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
                        elif self.state == "CUTSCENE":
                            if event.key == pygame.K_SPACE and self.cutscene:
                                if self.cutscene.finished:
                                    self.state = "PLAY"
                                    self.cutscene = None
                                else:
                                    self.cutscene.skip()
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

                if not self.running:
                    break

                self.update(dt)
                self.draw()
        finally:
            pygame.quit()

    def _apply_display_mode(self) -> None:
        _, (width, height) = self.available_resolutions[self.resolution_index]
        settings.WIDTH = width
        settings.HEIGHT = height
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        self.font, self.big_font = assets.load_fonts()
        self.cutscene_font = pygame.font.SysFont("consolas", 24)

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

    def _draw_particles(
        self, cam_x: float, cam_y: float, shake_x: float, shake_y: float
    ) -> None:
        for particle in self.particles:
            sx, sy = self._world_to_screen(
                particle.x, particle.y, cam_x, cam_y, shake_x, shake_y
            )
            pygame.draw.circle(
                self.screen,
                particle.color,
                (sx, sy),
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

    def _spawn_engine_particles(self) -> None:
        """Spawn engine thrust particles from the back of the ship."""
        if self.player.body is None:
            return

        angle = float(self.player.body.angle)
        px, py = self.player.pos

        throttle_level = max(0.0, min(1.0, float(getattr(self.player, "throttle_level", 0.0))))
        boost_timer = float(getattr(self.player, "boost_timer", 0.0))
        thrust_ratio = 1.0 if boost_timer > 0.0 else throttle_level

        # Only spawn particles while thrust is applied
        if thrust_ratio <= 0.0:
            return

        # Calculate back of ship position
        size = PLAYER_RADIUS + 4
        # Backward direction vector (opposite of forward which is (0, -1) rotated)
        back_dx = -math.sin(angle)
        back_dy = math.cos(angle)
        back_offset = size * 0.8  # Position at back of ship
        back_x = px + back_dx * back_offset
        back_y = py + back_dy * back_offset

        # Spawn 0-2 particles per frame depending on thrust ratio
        max_particles = 2
        particle_count = int(thrust_ratio * max_particles)
        if random.random() < (thrust_ratio * max_particles - particle_count):
            particle_count += 1

        for _ in range(particle_count):
            # Particles shoot out the back (opposite of ship direction)
            particle_angle = math.atan2(back_dy, back_dx) + random.uniform(-0.3, 0.3)
            particle_speed = random.uniform(80, 150) * (0.4 + 0.6 * thrust_ratio)

            # Color shifts from cyan to white based on thrust
            intensity = thrust_ratio
            base_color = NEON_CYAN
            color = (
                int(base_color[0] + (255 - base_color[0]) * intensity * 0.3),
                int(base_color[1] + (255 - base_color[1]) * intensity * 0.3),
                int(base_color[2]),
            )

            self.particles.append(
                Particle(
                    x=back_x,
                    y=back_y,
                    vx=math.cos(particle_angle) * particle_speed,
                    vy=math.sin(particle_angle) * particle_speed,
                    ttl=random.uniform(0.12, 0.3) * (0.6 + 0.4 * thrust_ratio),
                    radius=random.uniform(1.0, 2.2) * (0.6 + 0.4 * thrust_ratio),
                    color=color,
                )
            )

    def _draw_background(
        self, cam_x: float, cam_y: float, shake_x: float, shake_y: float
    ) -> None:
        self._draw_nebulae(cam_x, cam_y, shake_x, shake_y)
        spacing = 60
        grid_color = (12, 12, 24)
        width, height = self.screen.get_size()
        start_world_x = int(math.floor(cam_x / spacing) * spacing)
        start_world_y = int(math.floor(cam_y / spacing) * spacing)
        end_world_x = int(cam_x + width + spacing)
        end_world_y = int(cam_y + height + spacing)

        for world_x in range(start_world_x, end_world_x, spacing):
            xpos = int(world_x - cam_x + shake_x)
            pygame.draw.line(
                self.screen,
                grid_color,
                (xpos, int(0 + shake_y)),
                (xpos, int(height + shake_y)),
                1,
            )
        for world_y in range(start_world_y, end_world_y, spacing):
            ypos = int(world_y - cam_y + shake_y)
            pygame.draw.line(
                self.screen,
                grid_color,
                (int(0 + shake_x), ypos),
                (int(width + shake_x), ypos),
                1,
            )
        self._draw_stars(cam_x, cam_y, shake_x, shake_y)
        self._draw_shooting_stars(cam_x, cam_y, shake_x, shake_y)

    def _get_star_chunk(self, chunk_x: int, chunk_y: int) -> list[dict[str, object]]:
        key = (chunk_x, chunk_y)
        if key in self.star_chunks:
            return self.star_chunks[key]

        seed = (
            self.background_seed
            + chunk_x * 92837111
            + chunk_y * 689287499
        ) & 0xFFFFFFFF
        rng = random.Random(seed)
        stars: list[dict[str, object]] = []
        star_count = rng.randint(40, 60)
        colored_chance = 0.08
        tints = [(180, 200, 255), (255, 190, 190), (255, 240, 200)]
        for _ in range(star_count):
            roll = rng.random()
            if roll < 0.7:
                size = 1
            elif roll < 0.95:
                size = 2
            else:
                size = 3
            base_brightness = rng.randint(150, 255)
            is_colored = rng.random() < colored_chance
            tint = rng.choice(tints) if is_colored else (255, 255, 255)
            stars.append(
                {
                    "x": chunk_x * self.star_chunk_size + rng.uniform(0, self.star_chunk_size),
                    "y": chunk_y * self.star_chunk_size + rng.uniform(0, self.star_chunk_size),
                    "size": size,
                    "brightness": base_brightness,
                    "tint": tint,
                    "twinkle_speed": rng.uniform(0.01, 0.03),
                    "twinkle_offset": rng.uniform(0, math.tau),
                }
            )
        self.star_chunks[key] = stars
        return stars

    def _get_nebula_chunk(self, chunk_x: int, chunk_y: int) -> list[dict[str, object]]:
        key = (chunk_x, chunk_y)
        if key in self.nebula_chunks:
            return self.nebula_chunks[key]

        seed = (
            self.background_seed
            + chunk_x * 15187177
            + chunk_y * 51790321
        ) & 0xFFFFFFFF
        rng = random.Random(seed)
        nebulae: list[dict[str, object]] = []
        if rng.random() < 0.3:
            radius = rng.randint(400, 800)
            color = rng.choice([(255, 100, 150), (150, 100, 255), (100, 150, 255)])
            alpha = rng.randint(15, 35)
            surface = self._create_nebula_surface(radius, color, alpha)
            nebulae.append(
                {
                    "x": chunk_x * self.nebula_chunk_size + rng.uniform(0, self.nebula_chunk_size),
                    "y": chunk_y * self.nebula_chunk_size + rng.uniform(0, self.nebula_chunk_size),
                    "radius": radius,
                    "surface": surface,
                }
            )
        self.nebula_chunks[key] = nebulae
        return nebulae

    def _create_nebula_surface(
        self, radius: int, color: tuple[int, int, int], alpha: int
    ) -> pygame.Surface:
        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        steps = 12
        for step in range(steps):
            ratio = 1 - step / steps
            layer_radius = int(radius * ratio)
            layer_alpha = int(alpha * (ratio**2))
            if layer_radius <= 0 or layer_alpha <= 0:
                continue
            pygame.draw.circle(
                surface,
                (*color, layer_alpha),
                (radius, radius),
                layer_radius,
            )
        return surface

    def _draw_nebulae(
        self, cam_x: float, cam_y: float, shake_x: float, shake_y: float
    ) -> None:
        width, height = self.screen.get_size()
        start_chunk_x = int(math.floor(cam_x / self.nebula_chunk_size))
        start_chunk_y = int(math.floor(cam_y / self.nebula_chunk_size))
        end_chunk_x = int(math.floor((cam_x + width) / self.nebula_chunk_size)) + 1
        end_chunk_y = int(math.floor((cam_y + height) / self.nebula_chunk_size)) + 1

        for chunk_x in range(start_chunk_x, end_chunk_x):
            for chunk_y in range(start_chunk_y, end_chunk_y):
                for nebula in self._get_nebula_chunk(chunk_x, chunk_y):
                    nebula_x = float(nebula["x"])
                    nebula_y = float(nebula["y"])
                    radius = int(nebula["radius"])
                    screen_x = int(nebula_x - cam_x + shake_x)
                    screen_y = int(nebula_y - cam_y + shake_y)
                    if (
                        screen_x + radius < 0
                        or screen_x - radius > width
                        or screen_y + radius < 0
                        or screen_y - radius > height
                    ):
                        continue
                    surface = nebula["surface"]
                    self.screen.blit(surface, (screen_x - radius, screen_y - radius))

    def _draw_stars(
        self, cam_x: float, cam_y: float, shake_x: float, shake_y: float
    ) -> None:
        width, height = self.screen.get_size()
        start_chunk_x = int(math.floor(cam_x / self.star_chunk_size))
        start_chunk_y = int(math.floor(cam_y / self.star_chunk_size))
        end_chunk_x = int(math.floor((cam_x + width) / self.star_chunk_size)) + 1
        end_chunk_y = int(math.floor((cam_y + height) / self.star_chunk_size)) + 1
        time_seconds = pygame.time.get_ticks() / 1000.0

        for chunk_x in range(start_chunk_x, end_chunk_x):
            for chunk_y in range(start_chunk_y, end_chunk_y):
                for star in self._get_star_chunk(chunk_x, chunk_y):
                    world_x = float(star["x"])
                    world_y = float(star["y"])
                    screen_x = int(world_x - cam_x + shake_x)
                    screen_y = int(world_y - cam_y + shake_y)
                    if screen_x < -3 or screen_x > width + 3 or screen_y < -3 or screen_y > height + 3:
                        continue
                    base_brightness = float(star["brightness"])
                    twinkle_speed = float(star["twinkle_speed"])
                    twinkle_offset = float(star["twinkle_offset"])
                    brightness = base_brightness + math.sin(time_seconds * twinkle_speed + twinkle_offset) * 55
                    brightness = max(80, min(255, brightness))
                    tint = star["tint"]
                    factor = brightness / 255.0
                    color = (
                        int(tint[0] * factor),
                        int(tint[1] * factor),
                        int(tint[2] * factor),
                    )
                    size = int(star["size"])
                    if size <= 1:
                        self.screen.set_at((screen_x, screen_y), color)
                    else:
                        pygame.draw.circle(self.screen, color, (screen_x, screen_y), size)

    def _update_shooting_stars(self, dt: float) -> None:
        if random.random() < dt * 0.02:
            cam_x, cam_y = self._get_camera_origin()
            width, height = self.screen.get_size()
            edge = random.choice(["left", "right", "top", "bottom"])
            if edge == "left":
                start_x = cam_x - 40
                start_y = cam_y + random.uniform(0, height)
                vx = random.uniform(120, 180)
                vy = random.uniform(-30, 30)
            elif edge == "right":
                start_x = cam_x + width + 40
                start_y = cam_y + random.uniform(0, height)
                vx = random.uniform(-180, -120)
                vy = random.uniform(-30, 30)
            elif edge == "top":
                start_x = cam_x + random.uniform(0, width)
                start_y = cam_y - 40
                vx = random.uniform(-60, 60)
                vy = random.uniform(120, 180)
            else:
                start_x = cam_x + random.uniform(0, width)
                start_y = cam_y + height + 40
                vx = random.uniform(-60, 60)
                vy = random.uniform(-180, -120)
            self.shooting_stars.append(
                {"x": start_x, "y": start_y, "vx": vx, "vy": vy, "ttl": random.uniform(1.2, 2.0)}
            )

        for star in self.shooting_stars:
            star["x"] += star["vx"] * dt
            star["y"] += star["vy"] * dt
            star["ttl"] -= dt
        self.shooting_stars = [star for star in self.shooting_stars if star["ttl"] > 0]

    def _draw_shooting_stars(
        self, cam_x: float, cam_y: float, shake_x: float, shake_y: float
    ) -> None:
        if not self.shooting_stars:
            return
        width, height = self.screen.get_size()
        for star in self.shooting_stars:
            screen_x = int(star["x"] - cam_x + shake_x)
            screen_y = int(star["y"] - cam_y + shake_y)
            if screen_x < -100 or screen_x > width + 100 or screen_y < -100 or screen_y > height + 100:
                continue
            vx = star["vx"]
            vy = star["vy"]
            length = 40
            mag = math.hypot(vx, vy)
            if mag == 0:
                continue
            nx = vx / mag
            ny = vy / mag
            tail_x = int(screen_x - nx * length)
            tail_y = int(screen_y - ny * length)
            pygame.draw.line(self.screen, (220, 220, 255), (tail_x, tail_y), (screen_x, screen_y), 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), 2)

    def _draw_vignette(self) -> None:
        width, height = self.screen.get_size()
        if self.vignette_surface is None or self.vignette_size != (width, height):
            self.vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            self.vignette_surface.fill((0, 0, 0, 0))
            steps = 12
            for step in range(steps):
                alpha = int(90 * (step + 1) / steps)
                inset = step * 4
                rect = pygame.Rect(inset, inset, width - inset * 2, height - inset * 2)
                pygame.draw.rect(self.vignette_surface, (0, 0, 0, alpha), rect, 4)
            self.vignette_size = (width, height)
        if self.vignette_surface is not None:
            self.screen.blit(self.vignette_surface, (0, 0))

    def _get_player_catamaran(
        self, x: float, y: float, angle: float
    ) -> tuple[list[list[tuple[float, float]]], tuple[float, float]]:
        scale = (PLAYER_RADIUS * 2) / 40.0
        # OBA catamaran hull points (from ship-test.py), facing up
        left_hull = [(-15, -20), (-7, -20), (-7, 4), (-15, 4)]
        right_hull = [(7, -20), (15, -20), (15, 4), (7, 4)]
        base = [(-15, 0), (15, 0), (15, 14), (-15, 14)]
        left_engine = [(-12, 14), (-8, 14), (-6, 20), (-14, 20)]
        right_engine = [(8, 14), (12, 14), (14, 20), (6, 20)]

        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        def _transform(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
            rotated: list[tuple[float, float]] = []
            for px, py in points:
                sx = px * scale
                sy = py * scale
                rx = sx * cos_a - sy * sin_a
                ry = sx * sin_a + sy * cos_a
                rotated.append((x + rx, y + ry))
            return rotated

        polys = [
            _transform(base),
            _transform(left_hull),
            _transform(right_hull),
            _transform(left_engine),
            _transform(right_engine),
        ]

        # Front tip glow centered between hulls
        front_px, front_py = 0.0, -20.0 * scale
        front_x = x + (front_px * cos_a - front_py * sin_a)
        front_y = y + (front_px * sin_a + front_py * cos_a)
        return polys, (front_x, front_y)

    def _get_weapon_slots(self) -> list[dict[str, object]]:
        minigun_cd = self.player.get_fire_cooldown()
        minigun_ratio = min(1.0, self.fire_timer / max(0.0001, minigun_cd))

        rocket_ratio = 0.0
        if self.player.rockets_level >= 0:
            rocket_cd = self.player.get_rocket_stats()["fire_cooldown"]
            rocket_ratio = min(1.0, self.rocket_timer / max(0.0001, rocket_cd))

        laser_ratio = 0.0
        if self.player.laser_level >= 0:
            laser_cd = self.player.get_laser_stats()["fire_cooldown"]
            laser_ratio = min(1.0, self.laser_timer / max(0.0001, laser_cd))

        emp_ratio = 0.0
        if self.player.emp_level >= 0:
            emp_ratio = min(1.0, self.emp_timer / 0.5)

        mine_ratio = 0.0
        if self.player.mines_level >= 0:
            mine_cd = self.player.get_mine_stats()["drop_cooldown"]
            mine_ratio = min(1.0, self.mine_timer / max(0.0001, mine_cd))

        return [
            {
                "label": "MINIGUN",
                "type_icon": "◎",
                "cooldown_ratio": minigun_ratio,
                "icon_color": NEON_YELLOW,
            },
            {
                "label": "ROCKET",
                "type_icon": "⊕",
                "cooldown_ratio": rocket_ratio,
                "icon_color": NEON_ORANGE if self.player.rockets_level >= 0 else (70, 70, 70),
            },
            {
                "label": "LASER",
                "type_icon": "⊕",
                "cooldown_ratio": laser_ratio,
                "icon_color": NEON_CYAN if self.player.laser_level >= 0 else (70, 70, 70),
            },
            {
                "label": "EMP",
                "type_icon": "◎",
                "cooldown_ratio": emp_ratio,
                "icon_color": NEON_MAGENTA if self.player.emp_level >= 0 else (70, 70, 70),
            },
            {
                "label": "MINES",
                "type_icon": "✹",
                "cooldown_ratio": mine_ratio,
                "icon_color": NEON_ORANGE if self.player.mines_level >= 0 else (70, 70, 70),
            },
            {
                "label": "LOCKED",
                "type_icon": "",
                "cooldown_ratio": 0.0,
                "icon_color": (70, 70, 70),
            },
        ]

    def _get_utility_slots(self) -> list[dict[str, object]]:
        hurdle_ratio = 1.0
        if self.player.hurdle_cooldown > 0:
            hurdle_ratio = max(0.0, 1.0 - (self.player.hurdle_cooldown / max(0.001, HURDLE_COOLDOWN)))

        shield_ratio = 0.0
        if self.player.shield_max > 0:
            shield_ratio = max(0.0, min(1.0, self.player.shield_hp / self.player.shield_max))

        return [
            {
                "label": "BOOST",
                "type_icon": "",
                "cooldown_ratio": self.player.boost_charge,
                "icon_color": NEON_BLUE,
            },
            {
                "label": "HURDLE",
                "type_icon": "",
                "cooldown_ratio": hurdle_ratio,
                "icon_color": NEON_YELLOW,
                "remaining_cd": self.player.hurdle_cooldown,
            },
            {
                "label": "SHIELD",
                "type_icon": "",
                "cooldown_ratio": shield_ratio,
                "icon_color": NEON_CYAN if self.player.shield_level >= 0 else (70, 70, 70),
            },
            {
                "label": "TRACTOR",
                "type_icon": "",
                "cooldown_ratio": self.player.tractor_level / 5,
                "icon_color": NEON_GREEN,
            },
            {
                "label": "SPEED",
                "type_icon": "",
                "cooldown_ratio": self.player.speed_level / 5,
                "icon_color": NEON_MAGENTA,
            },
            {
                "label": "LOCKED",
                "type_icon": "",
                "cooldown_ratio": 0.0,
                "icon_color": (70, 70, 70),
            },
        ]

    def _draw_enemy(
        self, enemy: Enemy, cam_x: float, cam_y: float, shake_x: float, shake_y: float
    ) -> None:
        ex, ey = self._world_to_screen(enemy.x, enemy.y, cam_x, cam_y, shake_x, shake_y)
        outline_color = NEON_MAGENTA if enemy.is_boss else WHITE
        fill_color = (80, 0, 80) if enemy.is_boss else (180, 180, 180)

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

    def _get_camera_origin(self) -> tuple[float, float]:
        width, height = self.screen.get_size()
        return (self.player.x - width / 2.0, self.player.y - height / 2.0)

    def _world_to_screen(
        self,
        world_x: float,
        world_y: float,
        cam_x: float,
        cam_y: float,
        shake_x: float = 0.0,
        shake_y: float = 0.0,
    ) -> tuple[int, int]:
        return (
            int(world_x - cam_x + shake_x),
            int(world_y - cam_y + shake_y),
        )

    def _screen_to_world(self, screen_pos: tuple[int, int]) -> tuple[float, float]:
        cam_x, cam_y = self._get_camera_origin()
        return (screen_pos[0] + cam_x, screen_pos[1] + cam_y)

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
