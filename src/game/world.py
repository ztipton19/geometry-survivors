"""Core game loop and state."""

from __future__ import annotations

import math
import random

import pygame

from game import assets, settings
from game.entities.bullet import Bullet
from game.entities.enemy import Enemy
from game.entities.particle import Particle
from game.entities.player import Player
from game.entities.weapon_state import WeaponState
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
    FPS,
    NEON_BLUE,
    NEON_MAGENTA,
    NEON_YELLOW,
    PLAYER_RADIUS,
    RED,
    WHITE,
    EXTRACTION_AVAILABLE_AT,
    EXTRACTION_CHANNEL_TIME,
    DATA_PER_MINUTE,
    DATA_PER_KILL,
    DATA_EXTRACT_BONUS,
    get_ship_selection_colors,
)
from game.systems import (
    collisions,
    combat,
    fitting,
    progression,
    save_system,
    spawner,
    telemetry,
    threat_board,
)
from game.ui import (
    draw_data_archive_screen,
    draw_debrief_screen,
    draw_end_screen,
    draw_fitting_screen,
    draw_hud,
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
        self.particles: list[Particle] = []
        self.primary_weapon = WeaponState(
            name="PDC",
            ammo_max=1,
            ammo_current=1,
            damage=settings.BULLET_DAMAGE,
            fire_rate=1.0,
            gimbal_degrees=15.0,
            mounting="forward",
        )
        self.secondary_weapon = WeaponState(
            name="RAIL",
            ammo_max=1,
            ammo_current=1,
            damage=100.0,
            fire_rate=0.5,
            gimbal_degrees=5.0,
            mounting="forward",
        )

        self.shake_timer = 0.0
        self.shake_strength = 0.0

        self.spawner = spawner.Spawner()
        self.elapsed, self.remaining = progression.reset_timer()

        self.running = True
        self.state = "MENU"
        self.menu_selection = 0
        self.options_selection = 0
        self.pause_selection = 0
        self.selected_weapon_group = 3
        self.extraction_active = False
        self.extraction_timer = 0.0
        self.show_threat_board = False
        self.current_threats: list[dict[str, object]] = []
        self.debrief_summary: dict[str, object] = {}
        self.save_data = save_system.load_save_data()
        self.modules = fitting.load_modules()
        self.ships = fitting.load_ships()
        self.selected_ship_id = next(iter(self.ships.keys()), "")
        self.ship_equipment: dict[str, str] = {}
        self.fitting_selection = 0
        self.archive_selection = 0
        self.run_start_ammo = 0
        self.run_start_fuel = 0.0
        self.run_start_hp = 0.0
        self.fitting_status = ""
        self.archive_status = ""
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
        self._ensure_save_compatibility()
        self._reset_fitting_state()

    def restart(self) -> None:
        self.player = Player(settings.WIDTH / 2, settings.HEIGHT / 2)
        self.space = create_space()
        attach_body(self.space, self.player, PLAYER_RADIUS)
        self.enemies.clear()
        self.bullets.clear()
        self.particles.clear()
        self._apply_selected_loadout()
        self.shake_timer = 0.0
        self.shake_strength = 0.0
        self.shooting_stars.clear()
        self.spawner.reset()
        self.elapsed, self.remaining = progression.reset_timer()
        self.state = "PLAY"
        self.selected_weapon_group = 3
        self.extraction_active = False
        self.extraction_timer = 0.0
        self.current_threats = []
        self.run_start_ammo = self.primary_weapon.ammo_current + self.secondary_weapon.ammo_current
        self.run_start_fuel = self.player.fuel
        self.run_start_hp = self.player.hp
        self.cutscene = None
        self.debug_overlay.params["collision_enabled"] = True

    def _apply_selected_loadout(self) -> None:
        ship = self.ships.get(self.selected_ship_id, {})
        unlocked_module_ids = fitting.get_unlocked_module_ids(self.save_data)
        self.ship_equipment = fitting.sanitize_equipment(
            self.ship_equipment,
            ship,
            self.modules,
            unlocked_module_ids,
        )
        stats = fitting.calculate_ship_stats(ship, self.modules, self.ship_equipment)
        self.player.max_fuel = float(stats["fuel"])
        self.player.fuel = self.player.max_fuel
        self.player.max_hp = float(stats["hull"])
        self.player.hp = self.player.max_hp
        self.player.fuel_rate = float(stats["fuel_rate"])
        self.player.speed_value = float(stats["speed"])

        slots = ship.get("slots", [])
        primary_module = self._get_module_for_slot(slots, "weapon_primary")
        secondary_module = self._get_module_for_slot(slots, "weapon_secondary")
        self.primary_weapon = self._build_weapon_state(primary_module, "PRIMARY")
        self.secondary_weapon = self._build_weapon_state(secondary_module, "SECONDARY")

    def _finish_run(self, outcome: str) -> None:
        survival_time = self.elapsed
        kills = self.player.enemies_killed
        ammo_spent = max(
            0,
            self.run_start_ammo
            - (self.primary_weapon.ammo_current + self.secondary_weapon.ammo_current),
        )
        fuel_spent = max(0.0, self.run_start_fuel - self.player.fuel)
        hull_damage_taken = max(0.0, self.run_start_hp - self.player.hp)
        data_earned = (survival_time / 60.0) * DATA_PER_MINUTE + kills * DATA_PER_KILL
        if outcome == "Extracted":
            data_earned += DATA_EXTRACT_BONUS
        data_earned = round(data_earned, 2)

        meta = self.save_data["meta"]
        meta["total_runs"] = int(meta.get("total_runs", 0)) + 1
        meta["total_data_gb"] = round(float(meta.get("total_data_gb", 0.0)) + data_earned, 2)
        meta["best_time_seconds"] = max(float(meta.get("best_time_seconds", 0.0)), survival_time)
        meta["total_kills"] = int(meta.get("total_kills", 0)) + kills
        meta["total_fuel_burned"] = round(float(meta.get("total_fuel_burned", 0.0)) + fuel_spent, 2)
        meta["total_ammo_spent"] = int(meta.get("total_ammo_spent", 0)) + ammo_spent
        save_system.save_data(self.save_data)

        self.debrief_summary = {
            "outcome": outcome,
            "survival_time": survival_time,
            "kills": kills,
            "ammo_spent": ammo_spent,
            "fuel_spent": fuel_spent,
            "hull_damage": hull_damage_taken,
            "data_earned": data_earned,
            "total_data_gb": meta["total_data_gb"],
            "clone_number": meta["total_runs"],
        }
        telemetry.append_run_telemetry(
            {
                "clone_number": meta["total_runs"],
                "outcome": outcome,
                "survival_time": round(survival_time, 2),
                "kills": int(kills),
                "ammo_spent": int(ammo_spent),
                "fuel_spent": round(fuel_spent, 2),
                "hull_damage": round(hull_damage_taken, 2),
                "data_earned": data_earned,
                "total_data_gb": meta["total_data_gb"],
                "primary_weapon": self.primary_weapon.name,
                "secondary_weapon": self.secondary_weapon.name,
                "primary_mounting": self.primary_weapon.mounting,
                "secondary_mounting": self.secondary_weapon.mounting,
                "ship_id": self.selected_ship_id,
                "equipment": dict(self.ship_equipment),
            }
        )
        self.state = "DEBRIEF"

    def _ensure_save_compatibility(self) -> None:
        defaults = save_system.default_save_data()
        for key, value in defaults.items():
            if key not in self.save_data:
                self.save_data[key] = value
        meta = self.save_data.setdefault("meta", {})
        for key, value in defaults["meta"].items():
            meta.setdefault(key, value)
        unlocks = self.save_data.setdefault("unlocks", {})
        unlocked_modules = unlocks.setdefault("modules", [])
        for module_id in defaults["unlocks"]["modules"]:
            if module_id not in unlocked_modules:
                unlocked_modules.append(module_id)
        save_system.save_data(self.save_data)

    def _reset_fitting_state(self) -> None:
        if not self.selected_ship_id or self.selected_ship_id not in self.ships:
            self.selected_ship_id = next(iter(self.ships.keys()), "")
        ship = self.ships.get(self.selected_ship_id, {})
        unlocked_module_ids = fitting.get_unlocked_module_ids(self.save_data)
        self.ship_equipment = fitting.default_equipment_for_ship(
            ship,
            self.modules,
            unlocked_module_ids,
        )
        self.ship_equipment = fitting.sanitize_equipment(
            self.ship_equipment,
            ship,
            self.modules,
            unlocked_module_ids,
        )
        self.fitting_selection = 0

    def _get_module_for_slot(self, ship_slots: object, slot_id: str) -> dict[str, object]:
        if not isinstance(ship_slots, list):
            return {}
        for slot in ship_slots:
            if not isinstance(slot, dict):
                continue
            if str(slot.get("id")) == slot_id:
                module_id = self.ship_equipment.get(slot_id)
                if module_id and module_id in self.modules:
                    return self.modules[module_id]
        return {}

    def _build_weapon_state(self, module: dict[str, object], fallback_name: str) -> WeaponState:
        stats = module.get("stats", {}) if isinstance(module, dict) else {}
        if not isinstance(stats, dict):
            stats = {}
        ammo = max(1, int(stats.get("ammo", 1)))
        return WeaponState(
            name=str(module.get("name", fallback_name)),
            ammo_max=ammo,
            ammo_current=ammo,
            damage=float(stats.get("damage", settings.BULLET_DAMAGE)),
            fire_rate=float(stats.get("fire_rate", 1.0)),
            gimbal_degrees=float(stats.get("gimbal_degrees", 15.0)),
            mounting=str(module.get("mounting", "forward")),
        )

    def _get_fitting_ship_and_stats(self) -> tuple[dict[str, object], dict[str, float | int]]:
        ship = self.ships.get(self.selected_ship_id, {})
        stats = fitting.calculate_ship_stats(ship, self.modules, self.ship_equipment)
        return ship, stats

    def _cycle_slot_module(self, direction: int) -> None:
        ship = self.ships.get(self.selected_ship_id, {})
        slots = ship.get("slots", [])
        if not isinstance(slots, list) or not slots:
            return
        slot_index = self.fitting_selection % len(slots)
        slot = slots[slot_index]
        if not isinstance(slot, dict):
            return
        slot_id = str(slot.get("id", ""))
        compatible_ids = fitting.compatible_modules_for_slot(
            self.modules,
            fitting.get_unlocked_module_ids(self.save_data),
            slot,
        )
        if not compatible_ids:
            self.fitting_status = "No unlocked modules fit this slot."
            return
        current_id = self.ship_equipment.get(slot_id)
        if current_id not in compatible_ids:
            self.ship_equipment[slot_id] = compatible_ids[0]
            module_name = str(self.modules.get(compatible_ids[0], {}).get("name", compatible_ids[0]))
            self.fitting_status = f"Equipped {module_name}"
            return
        current_index = compatible_ids.index(current_id)
        next_index = (current_index + direction) % len(compatible_ids)
        self.ship_equipment[slot_id] = compatible_ids[next_index]
        module_name = str(self.modules.get(compatible_ids[next_index], {}).get("name", compatible_ids[next_index]))
        self.fitting_status = f"Equipped {module_name}"

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

        self.elapsed, self.remaining, completed = progression.update_timer(
            self.elapsed, self.remaining, dt
        )
        if completed:
            self._finish_run("Signal Lost")
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
        self.current_threats = threat_board.collect_threats(self.enemies, self.player.pos)

        death_positions: list[tuple[float, float]] = []
        hit_positions: list[tuple[float, float]] = []
        collisions_enabled = bool(self.debug_overlay.params["collision_enabled"])
        self.primary_weapon.update(dt)
        self.secondary_weapon.update(dt)

        mouse_buttons = pygame.mouse.get_pressed(3)
        mouse_world = self._screen_to_world(pygame.mouse.get_pos())
        if self.selected_weapon_group == 1:
            primary_enabled = True
            secondary_enabled = False
        elif self.selected_weapon_group == 2:
            primary_enabled = False
            secondary_enabled = True
        else:
            primary_enabled = True
            secondary_enabled = True
        if mouse_buttons[0] and primary_enabled:
            bullet = combat.fire_weapon(self.player, self.primary_weapon, mouse_world)
            if bullet is not None:
                self.bullets.append(bullet)
        if mouse_buttons[2] and secondary_enabled:
            bullet = combat.fire_weapon(self.player, self.secondary_weapon, mouse_world)
            if bullet is not None:
                self.bullets.append(bullet)

        combat.update_bullets(self.bullets, dt)
        self.bullets = [bullet for bullet in self.bullets if bullet.ttl > 0]
        if collisions_enabled:
            collisions.resolve_bullet_hits(
                self.bullets,
                self.enemies,
                self.player,
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
        for pos in death_positions:
            self._spawn_explosion(pos, RED, 12)
        for pos in hit_positions:
            self._spawn_hit_sparks(pos)

        if self.elapsed >= EXTRACTION_AVAILABLE_AT:
            if self.extraction_active:
                self.extraction_timer = max(0.0, self.extraction_timer - dt)
                if self.extraction_timer <= 0:
                    self._finish_run("Extracted")
                    return

        # Check death
        if self.player.hp <= 0:
            self.player.hp = 0
            self._spawn_explosion(self.player.pos, NEON_BLUE, 18)
            self._add_screen_shake(10.0)
            self._finish_run("Destroyed")
            return

        self._update_particles(dt)
        self._spawn_engine_particles()
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)
        self._update_shooting_stars(dt)

    def draw(self) -> None:
        if self.state in ("PLAY", "PAUSE", "WIN", "LOSE", "DEBRIEF"):
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
        if self.state == "FITTING":
            ship, fitting_stats = self._get_fitting_ship_and_stats()
            unlocked_module_ids = fitting.get_unlocked_module_ids(self.save_data)
            draw_fitting_screen(
                self.screen,
                self.font,
                self.big_font,
                ship,
                self.modules,
                self.ship_equipment,
                self.fitting_selection,
                fitting_stats,
                float(self.save_data["meta"].get("total_data_gb", 0.0)),
                unlocked_module_ids,
                self.fitting_status,
            )
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
        if self.state == "ARCHIVE":
            entries = fitting.build_archive_entries(
                self.modules,
                fitting.get_unlocked_module_ids(self.save_data),
            )
            if entries:
                self.archive_selection %= len(entries)
            draw_data_archive_screen(
                self.screen,
                self.font,
                self.big_font,
                float(self.save_data["meta"].get("total_data_gb", 0.0)),
                int(self.save_data["meta"].get("total_runs", 0)),
                entries,
                self.archive_selection,
                self.modules,
                self.archive_status,
            )
            pygame.display.flip()
            return
        if self.state == "DEBRIEF":
            draw_debrief_screen(self.screen, self.font, self.big_font, self.debrief_summary)
            pygame.display.flip()
            return

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

        for enemy in self.enemies:
            self._draw_enemy(enemy, cam_x, cam_y, shake_x, shake_y)
        threat_board.draw_edge_indicators(
            self.screen,
            self.current_threats,
            self._world_to_screen,
            cam_x,
            cam_y,
            shake_x,
            shake_y,
        )

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

        self._draw_particles(cam_x, cam_y, shake_x, shake_y)
        self._draw_vignette()

        draw_hud(
            self.screen,
            self.font,
            self.player,
            self.remaining,
            [
                {
                    "label": f"{self.primary_weapon.name} [{self.primary_weapon.mounting[:1].upper()}] G{self.selected_weapon_group}",
                    "ammo_current": self.primary_weapon.ammo_current,
                    "ammo_max": self.primary_weapon.ammo_max,
                },
                {
                    "label": f"{self.secondary_weapon.name} [{self.secondary_weapon.mounting[:1].upper()}]",
                    "ammo_current": self.secondary_weapon.ammo_current,
                    "ammo_max": self.secondary_weapon.ammo_max,
                },
            ],
            [],
            self._get_extraction_text(),
            int(self.save_data["meta"].get("total_runs", 0)),
        )
        if self.show_threat_board:
            threat_board.draw_threat_board(self.screen, self.font, self.current_threats)

        if self.state == "PAUSE":
            draw_pause_menu(self.screen, self.font, self.big_font, self.pause_selection)
        
        draw_end_screen(self.screen, self.font, self.big_font, self.state, self.player)
        if self.state in ("PLAY", "PAUSE"):
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
                                    self.state = "FITTING"
                                elif self.menu_selection == 1:
                                    self.state = "OPTIONS"
                                elif self.menu_selection == 2:
                                    self.running = False
                            elif event.key == pygame.K_ESCAPE:
                                self.running = False
                        elif self.state == "FITTING":
                            ship = self.ships.get(self.selected_ship_id, {})
                            slots = ship.get("slots", []) if isinstance(ship, dict) else []
                            slot_count = len(slots) if isinstance(slots, list) else 0
                            if event.key in (pygame.K_UP, pygame.K_w):
                                if slot_count > 0:
                                    self.fitting_selection = (self.fitting_selection - 1) % slot_count
                            elif event.key in (pygame.K_DOWN, pygame.K_s):
                                if slot_count > 0:
                                    self.fitting_selection = (self.fitting_selection + 1) % slot_count
                            elif event.key in (pygame.K_LEFT, pygame.K_a):
                                self._cycle_slot_module(-1)
                            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                                self._cycle_slot_module(1)
                            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                                self.fitting_status = ""
                                self.restart()
                            elif event.key == pygame.K_TAB:
                                self.archive_status = ""
                                self.state = "ARCHIVE"
                            elif event.key == pygame.K_ESCAPE:
                                self.state = "MENU"
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
                            elif pygame.K_1 <= event.key <= pygame.K_5:
                                self.selected_weapon_group = event.key - pygame.K_0
                            elif event.key == pygame.K_TAB:
                                self.show_threat_board = not self.show_threat_board
                            elif event.key == pygame.K_x and self.elapsed >= EXTRACTION_AVAILABLE_AT:
                                if not self.extraction_active:
                                    self.extraction_active = True
                                    self.extraction_timer = EXTRACTION_CHANNEL_TIME
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
                        elif self.state == "DEBRIEF":
                            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                                self.state = "FITTING"
                            elif event.key == pygame.K_m:
                                self.state = "MENU"
                        elif self.state == "ARCHIVE":
                            entries = fitting.build_archive_entries(
                                self.modules,
                                fitting.get_unlocked_module_ids(self.save_data),
                            )
                            if entries:
                                self.archive_selection %= len(entries)
                            if event.key in (pygame.K_UP, pygame.K_w):
                                if entries:
                                    self.archive_selection = (self.archive_selection - 1) % len(entries)
                            elif event.key in (pygame.K_DOWN, pygame.K_s):
                                if entries:
                                    self.archive_selection = (self.archive_selection + 1) % len(entries)
                            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                                if entries:
                                    selected = entries[self.archive_selection]
                                    unlocked, message = fitting.try_unlock_module(
                                        self.save_data,
                                        self.modules,
                                        str(selected["id"]),
                                    )
                                    self.archive_status = message
                                    if unlocked:
                                        save_system.save_data(self.save_data)
                                        ship = self.ships.get(self.selected_ship_id, {})
                                        self.ship_equipment = fitting.sanitize_equipment(
                                            self.ship_equipment,
                                            ship,
                                            self.modules,
                                            fitting.get_unlocked_module_ids(self.save_data),
                                        )
                            if event.key == pygame.K_ESCAPE:
                                self.archive_status = ""
                                self.state = "FITTING"
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

    def _get_extraction_text(self) -> str:
        if self.elapsed < EXTRACTION_AVAILABLE_AT:
            return ""
        if self.extraction_active:
            return f"EXTRACTING... {self.extraction_timer:0.1f}s"
        return "EXTRACTION AVAILABLE - Press X"

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
            base_color = NEON_BLUE
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

    def _is_world_position_on_screen(
        self,
        world_x: float,
        world_y: float,
        cam_x: float,
        cam_y: float,
        screen_w: int,
        screen_h: int,
    ) -> bool:
        screen_x = world_x - cam_x
        screen_y = world_y - cam_y
        return 0.0 <= screen_x <= float(screen_w) and 0.0 <= screen_y <= float(screen_h)

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
