"""Runtime debug tuning overlay."""

from __future__ import annotations

import pygame


class DebugOverlay:
    def __init__(self, game: object) -> None:
        self.game = game
        self.active = False
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.params: dict[str, float | bool] = {
            "player_thrust_power": 73.125,
            "player_strafe_power": 64.35,
            "player_max_speed": 56.25,
            "player_drift_factor": 0.995,
            "enemy_speed": 19.40625,
            "collision_enabled": True,
        }

        self.presets: dict[int, dict[str, float | str]] = {
            1: {
                "name": "Fighter",
                "player_thrust_power": 82.0,
                "player_strafe_power": 72.0,
                "player_max_speed": 68.0,
                "player_drift_factor": 0.992,
            },
            2: {
                "name": "Tank",
                "player_thrust_power": 58.0,
                "player_strafe_power": 50.0,
                "player_max_speed": 45.0,
                "player_drift_factor": 0.997,
            },
            3: {
                "name": "Interceptor",
                "player_thrust_power": 96.0,
                "player_strafe_power": 84.0,
                "player_max_speed": 78.0,
                "player_drift_factor": 0.990,
            },
            4: {
                "name": "Starter",
                "player_thrust_power": 73.125,
                "player_strafe_power": 64.35,
                "player_max_speed": 56.25,
                "player_drift_factor": 0.995,
            },
            5: {
                "name": "Custom_1",
                "player_thrust_power": 73.125,
                "player_strafe_power": 64.35,
                "player_max_speed": 56.25,
                "player_drift_factor": 0.995,
            },
        }

        self.selected_index = 0
        self.param_keys = list(self.params.keys())
        self.mode = "tuning"

    def toggle(self) -> None:
        self.active = not self.active

    def handle_input(self, event: pygame.event.Event) -> bool:
        if not self.active or event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_TAB:
            self.mode = "preset" if self.mode == "tuning" else "tuning"
            return True

        if self.mode == "tuning":
            return self._handle_tuning_input(event)
        return self._handle_preset_input(event)

    def _handle_tuning_input(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.param_keys)
            return True
        if event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.param_keys)
            return True
        if event.key == pygame.K_LEFT:
            self.adjust_value(-1)
            return True
        if event.key == pygame.K_RIGHT:
            self.adjust_value(1)
            return True
        if event.key == pygame.K_LEFTBRACKET:
            self.adjust_value(-10)
            return True
        if event.key == pygame.K_RIGHTBRACKET:
            self.adjust_value(10)
            return True
        if event.key == pygame.K_c:
            self.params["collision_enabled"] = not bool(self.params["collision_enabled"])
            return True
        return False

    def _handle_preset_input(self, event: pygame.event.Event) -> bool:
        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
            self.load_preset(event.key - pygame.K_0)
            return True
        if event.key == pygame.K_s:
            self.save_current_to_preset()
            return True
        if event.key == pygame.K_p:
            self.print_presets_to_console()
            return True
        return False

    def adjust_value(self, delta: int) -> None:
        key = self.param_keys[self.selected_index]
        if key == "collision_enabled":
            return

        current = float(self.params[key])
        if "drift_factor" in key:
            self.params[key] = max(0.5, min(0.999, current + delta * 0.005))
        else:
            self.params[key] = max(0.0, current + delta * 1.5)

    def load_preset(self, preset_num: int) -> None:
        if preset_num not in self.presets:
            return
        preset = self.presets[preset_num]
        for key, value in preset.items():
            if key != "name" and key in self.params:
                self.params[key] = float(value)
        print(f"Loaded preset: {preset['name']}")

    def save_current_to_preset(self) -> None:
        preset_num = 5
        self.presets[preset_num] = {
            "name": f"Custom_{preset_num}",
            "player_thrust_power": float(self.params["player_thrust_power"]),
            "player_strafe_power": float(self.params["player_strafe_power"]),
            "player_max_speed": float(self.params["player_max_speed"]),
            "player_drift_factor": float(self.params["player_drift_factor"]),
        }
        print(f"Saved to preset {preset_num}: {self.presets[preset_num]}")

    def print_presets_to_console(self) -> None:
        print("\n=== SHIP PRESETS ===")
        print("SHIP_STATS = {")
        for _, preset in sorted(self.presets.items()):
            print(f"    '{preset['name']}': {{")
            print(f"        'thrust_power': {preset['player_thrust_power']},")
            print(f"        'strafe_power': {preset['player_strafe_power']},")
            print(f"        'max_speed': {preset['player_max_speed']},")
            print(f"        'drift_factor': {preset['player_drift_factor']},")
            print("    },")
        print("}\n")

    def apply_to_game(self) -> None:
        player = getattr(self.game, "player", None)
        if player is not None:
            player.debug_thrust_power = float(self.params["player_thrust_power"])
            player.debug_strafe_power = float(self.params["player_strafe_power"])
            player.debug_max_speed = float(self.params["player_max_speed"])
            player.debug_drift_factor = float(self.params["player_drift_factor"])

        for enemy in getattr(self.game, "enemies", []):
            enemy.speed = float(self.params["enemy_speed"])

    def draw(self, screen: pygame.Surface) -> None:
        if not self.active:
            return
        overlay = pygame.Surface((520, 370), pygame.SRCALPHA)
        overlay.fill((20, 20, 30, 210))
        screen.blit(overlay, (10, 10))

        screen.blit(self.font.render("DEBUG MODE (F3)", True, (255, 255, 0)), (20, 20))
        mode_text = self.small_font.render(
            f"Mode: {self.mode.upper()} (TAB to switch)", True, (100, 200, 255)
        )
        screen.blit(mode_text, (20, 45))

        if self.mode == "tuning":
            self._draw_tuning_mode(screen)
        else:
            self._draw_preset_mode(screen)

    def _draw_tuning_mode(self, screen: pygame.Surface) -> None:
        instructions = self.small_font.render(
            "↑/↓: Select | ←/→: Adjust | [/]: Fast | C: Toggle collision",
            True,
            (150, 150, 150),
        )
        screen.blit(instructions, (20, 70))

        y = 100
        for i, key in enumerate(self.param_keys):
            value = self.params[key]
            color = (255, 255, 255) if i == self.selected_index else (150, 150, 150)
            if isinstance(value, bool):
                value_str = "ON" if value else "OFF"
            elif isinstance(value, float):
                value_str = f"{value:.3f}"
            else:
                value_str = str(value)
            screen.blit(self.font.render(f"{key}: {value_str}", True, color), (30, y))
            if i == self.selected_index:
                screen.blit(self.font.render(">", True, (255, 255, 0)), (15, y))
            y += 30

        enabled = bool(self.params["collision_enabled"])
        collision_status = self.small_font.render(
            f"Collisions: {'ON' if enabled else 'OFF'}",
            True,
            (100, 255, 100) if enabled else (255, 100, 100),
        )
        screen.blit(collision_status, (20, 340))

    def _draw_preset_mode(self, screen: pygame.Surface) -> None:
        instructions = self.small_font.render(
            "1-5: Load preset | S: Save to slot 5 | P: Print to console",
            True,
            (150, 150, 150),
        )
        screen.blit(instructions, (20, 70))

        y = 100
        for num in sorted(self.presets.keys()):
            preset = self.presets[num]
            color = (150, 255, 150) if num >= 5 else (200, 200, 200)
            screen.blit(self.font.render(f"{num}: {preset['name']}", True, color), (30, y))
            stats = self.small_font.render(
                "Thrust:{:.1f} Strafe:{:.1f} Max:{:.1f} Drift:{:.3f}".format(
                    float(preset["player_thrust_power"]),
                    float(preset["player_strafe_power"]),
                    float(preset["player_max_speed"]),
                    float(preset["player_drift_factor"]),
                ),
                True,
                (150, 150, 150),
            )
            screen.blit(stats, (50, y + 20))
            y += 50
