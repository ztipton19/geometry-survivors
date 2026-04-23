"""UI rendering helpers."""

from __future__ import annotations

import pygame

from game.entities.player import Player
from game.settings import (
    NEON_BLUE,
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_YELLOW,
    RED,
    WHITE,
    get_ship_selection_colors,
)


def draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    player: Player,
    remaining: float,
    weapon_slots: list[dict[str, object]],
    utility_slots: list[dict[str, object]],
    extraction_text: str = "",
    clone_number: int = 0,
) -> None:
    width, height = screen.get_size()
    # Dimmer single color at 50% opacity
    palette = get_ship_selection_colors()
    hud_color = palette["ui_primary"]
    alpha = 128  # 50%
    text_color = palette["ui_text"]

    # Top bar - timer center, kills right
    mm = int(remaining) // 60
    ss = int(remaining) % 60
    timer_text = f"{mm:02d}:{ss:02d}"

    time_font = pygame.font.SysFont("consolas", 36)
    time_surf = time_font.render(timer_text, True, text_color)
    screen.blit(time_surf, (width // 2 - time_surf.get_width() // 2, 12))

    kill_surf = font.render(f"{player.enemies_killed}", True, text_color)
    screen.blit(kill_surf, (width - kill_surf.get_width() - 16, 16))
    clone_surf = font.render(f"CLONE #{clone_number}", True, text_color)
    screen.blit(clone_surf, (width - clone_surf.get_width() - 16, 38))
    for i, slot in enumerate(weapon_slots[:2]):
        ammo_current = int(slot.get("ammo_current", 0))
        ammo_max = int(slot.get("ammo_max", 0))
        label = str(slot.get("label", f"W{i + 1}"))
        ammo_surf = font.render(f"{label}: {ammo_current}/{ammo_max}", True, text_color)
        screen.blit(ammo_surf, (16, 16 + i * 20))
    fuel_surf = font.render(f"FUEL: {int(player.fuel)}/{int(player.max_fuel)}", True, text_color)
    screen.blit(fuel_surf, (16, 56))
    if extraction_text:
        extract_surf = font.render(extraction_text, True, NEON_YELLOW)
        screen.blit(extract_surf, (16, 80))

    # Bottom center - minimalist bars and minimap circle
    center_x = width // 2
    center_y = height - 50

    # Minimap circle (placeholder)
    minimap_radius = 30
    minimap_surface = pygame.Surface((minimap_radius * 2, minimap_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(minimap_surface, (*hud_color, alpha), (minimap_radius, minimap_radius), minimap_radius, 1)
    screen.blit(minimap_surface, (center_x - minimap_radius, center_y - minimap_radius))

    # Vertical bar dimensions
    bar_width = 8
    bar_height = 50
    bar_gap = 10  # Gap between bars

    # Calculate ratios
    boost_ratio = max(0.0, min(1.0, float(player.boost_charge)))
    throttle_ratio = max(0.0, min(1.0, float(player.throttle_level)))
    hp_ratio = max(0.0, min(1.0, player.hp / max(1.0, player.max_hp)))
    fuel_ratio = max(0.0, min(1.0, player.fuel / max(1.0, player.max_fuel)))
    # Left side: Boost and Throttle
    boost_x = center_x - minimap_radius - bar_gap - bar_width * 3 - bar_gap * 2
    throttle_x = center_x - minimap_radius - bar_gap - bar_width * 2 - bar_gap
    fuel_x = center_x - minimap_radius - bar_gap - bar_width

    _draw_vertical_bar(screen, "B", boost_ratio, boost_x, center_y - bar_height // 2, bar_width, bar_height, hud_color, alpha, text_color)
    _draw_vertical_bar(screen, "T", throttle_ratio, throttle_x, center_y - bar_height // 2, bar_width, bar_height, hud_color, alpha, text_color)
    _draw_vertical_bar(screen, "F", fuel_ratio, fuel_x, center_y - bar_height // 2, bar_width, bar_height, hud_color, alpha, text_color)

    # Right side: Health
    hp_x = center_x + minimap_radius + bar_gap

    _draw_vertical_bar(screen, "H", hp_ratio, hp_x, center_y - bar_height // 2, bar_width, bar_height, hud_color, alpha, text_color)

    # Bottom left: 6 weapon slots (simple squares)
    slot_size = 24
    slot_gap = 6
    weapon_start_x = 16
    weapon_y = height - slot_size - 16

    for i, slot in enumerate(weapon_slots[:6]):
        slot_x = weapon_start_x + i * (slot_size + slot_gap)
        _draw_simple_slot(screen, slot_x, weapon_y, slot_size, slot, hud_color, alpha)

    # Bottom right: 6 utility slots (simple squares)
    utility_end_x = width - 16
    utility_y = height - slot_size - 16

    for i, slot in enumerate(utility_slots[:6]):
        slot_x = utility_end_x - (6 - i) * (slot_size + slot_gap)
        _draw_simple_slot(screen, slot_x, utility_y, slot_size, slot, hud_color, alpha)


def _draw_simple_slot(
    screen: pygame.Surface,
    x: int,
    y: int,
    size: int,
    slot: dict[str, object],
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    """Draw a simple minimalist slot square."""
    slot_surface = pygame.Surface((size, size), pygame.SRCALPHA)

    # Draw outline
    pygame.draw.rect(slot_surface, (*color, alpha), (0, 0, size, size), 1)

    # Fill if active/unlocked (icon_color is present and not gray)
    icon_color = slot.get("icon_color", (80, 80, 80))
    if icon_color != (70, 70, 70) and icon_color != (80, 80, 80):  # Active slot
        # Slight fill to show it's active
        pygame.draw.rect(slot_surface, (*color, alpha // 2), (2, 2, size - 4, size - 4), 0)

    screen.blit(slot_surface, (x, y))


def _draw_vertical_bar(
    screen: pygame.Surface,
    label: str,
    ratio: float,
    x: int,
    y: int,
    width: int,
    height: int,
    color: tuple[int, int, int],
    alpha: int,
    text_color: tuple[int, int, int],
) -> None:
    """Draw a minimalist vertical bar with single letter label."""
    # Draw bar outline
    bar_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(bar_surface, (*color, alpha), (0, 0, width, height), 1)

    # Draw fill from bottom up
    fill_height = int(height * max(0.0, min(1.0, ratio)))
    if fill_height > 0:
        pygame.draw.rect(bar_surface, (*color, alpha), (1, height - fill_height, width - 2, fill_height), 0)

    screen.blit(bar_surface, (x, y))

    # Draw label above bar
    label_font = pygame.font.SysFont("consolas", 12)
    label_surf = label_font.render(label, True, text_color)
    screen.blit(label_surf, (x + width // 2 - label_surf.get_width() // 2, y - 14))


def draw_end_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    state: str,
    player: Player | None = None,
) -> None:
    if state not in ("WIN", "LOSE"):
        return
    width, height = screen.get_size()
    msg = "YOU SURVIVED" if state == "WIN" else "YOU DIED"
    sub = "Press R to restart or ESC to quit"
    title = big_font.render(msg, True, NEON_GREEN if state == "WIN" else RED)
    subtitle = font.render(sub, True, WHITE)
    screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 80))
    screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, height // 2 + 80))
    
    # Stats display
    if player:
        stats_y = height // 2 - 20
        stats = [
            f"Enemies Killed: {player.enemies_killed}",
            f"Damage Dealt: {player.damage_dealt}",
        ]
        for i, stat in enumerate(stats):
            stat_surf = font.render(stat, True, WHITE)
            screen.blit(stat_surf, (width // 2 - stat_surf.get_width() // 2, stats_y + i * 25))


def draw_start_menu(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    selection: int,
) -> None:
    width, height = screen.get_size()
    title = big_font.render("NEON SURVIVORS", True, NEON_CYAN)
    screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 180))
    prompt = font.render("Pilot the drone. Survive 15 minutes.", True, WHITE)
    screen.blit(prompt, (width // 2 - prompt.get_width() // 2, height // 2 - 130))

    options = ["Start Mission", "Options", "Quit"]
    for i, label in enumerate(options):
        color = NEON_YELLOW if i == selection else WHITE
        text = font.render(label, True, color)
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 40 + i * 40))


def draw_options_menu(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    selection: int,
    resolution_label: str,
    fullscreen: bool,
) -> None:
    width, height = screen.get_size()
    title = big_font.render("OPTIONS", True, NEON_MAGENTA)
    screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 180))

    items = [
        f"Resolution: {resolution_label}",
        f"Fullscreen: {'On' if fullscreen else 'Off'}",
        "Back",
    ]
    for i, label in enumerate(items):
        color = NEON_YELLOW if i == selection else WHITE
        text = font.render(label, True, color)
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 40 + i * 40))

    hint = font.render("Use ↑/↓ to select, ←/→ to change, Enter to confirm.", True, WHITE)
    screen.blit(hint, (width // 2 - hint.get_width() // 2, height - 60))


def draw_intro_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
) -> None:
    width, height = screen.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = big_font.render("MISSION BRIEF", True, NEON_GREEN)
    screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 160))

    lines = [
        "We've gotten your drone into the enemy stronghold.",
        "You only have 15 minutes to take them out.",
        "Get moving.",
    ]
    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 90 + i * 32))

    prompt = font.render("Press any key to deploy.", True, NEON_YELLOW)
    screen.blit(prompt, (width // 2 - prompt.get_width() // 2, height // 2 + 60))


def draw_pause_menu(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    selection: int,
) -> None:
    width, height = screen.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title = big_font.render("PAUSED", True, NEON_MAGENTA)
    screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 140))

    options = ["Resume", "Restart", "Quit to Menu"]
    for i, label in enumerate(options):
        color = NEON_YELLOW if i == selection else WHITE
        text = font.render(label, True, color)
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 40 + i * 40))

    hint = font.render("ESC to resume. Enter to select.", True, WHITE)
    screen.blit(hint, (width // 2 - hint.get_width() // 2, height // 2 + 100))


def draw_fitting_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    ship: dict[str, object],
    modules: dict[str, dict[str, object]],
    equipment: dict[str, str],
    selected_index: int,
    fitting_stats: dict[str, float | int],
    total_data_gb: float,
    unlocked_module_ids: set[str],
    status_text: str,
) -> None:
    width, height = screen.get_size()
    title = big_font.render("FITTING BAY", True, NEON_CYAN)
    screen.blit(title, (width // 2 - title.get_width() // 2, 70))
    ship_name = str(ship.get("name", "Unknown Ship"))
    ship_surf = font.render(f"Hull: {ship_name}", True, WHITE)
    screen.blit(ship_surf, (width // 2 - ship_surf.get_width() // 2, 118))
    info = font.render(f"Research Data: {total_data_gb:.1f} GB", True, WHITE)
    screen.blit(info, (width // 2 - info.get_width() // 2, 144))

    y = 200
    slots = ship.get("slots", []) if isinstance(ship, dict) else []
    size_rank = {"S": 1, "M": 2, "L": 3}
    selected_slot: dict[str, object] | None = None
    selected_module: dict[str, object] | None = None
    for i, slot in enumerate(slots):
        if not isinstance(slot, dict):
            continue
        slot_id = str(slot.get("id", f"slot_{i}"))
        module_id = equipment.get(slot_id, "")
        module = modules.get(module_id, {})
        if i == selected_index:
            selected_slot = slot
            selected_module = module
        module_name = str(module.get("name", "Empty"))
        color = NEON_YELLOW if i == selected_index else WHITE
        text = font.render(f"{i + 1}. {slot_id}: {module_name}", True, color)
        screen.blit(text, (width // 2 - 280, y))
        details = font.render(
            f"Type: {slot.get('type')}  Size: {slot.get('slot_size')}  Mass {int(module.get('mass', 0))}",
            True,
            (180, 180, 180),
        )
        screen.blit(details, (width // 2 - 240, y + 24))
        y += 58

    mass = float(fitting_stats.get("mass", 0.0))
    mass_limit = float(fitting_stats.get("mass_limit", 1.0))
    hull = float(fitting_stats.get("hull", 0.0))
    hull_delta = float(fitting_stats.get("hull_delta", 0.0))
    fuel = float(fitting_stats.get("fuel", 0.0))
    fuel_delta = float(fitting_stats.get("fuel_delta", 0.0))
    speed = float(fitting_stats.get("speed", 0.0))
    speed_delta = float(fitting_stats.get("speed_delta", 0.0))
    fuel_rate = float(fitting_stats.get("fuel_rate", 1.0))
    overload_ratio = float(fitting_stats.get("overload_ratio", 0.0))
    overloaded = bool(fitting_stats.get("overloaded", 0))
    mass_color = RED if overloaded else WHITE
    mass_surf = font.render(f"Mass: {mass:.0f}/{mass_limit:.0f}", True, mass_color)
    hull_surf = font.render(
        f"Hull: {hull:.0f} ({hull_delta:+.0f})  Fuel: {fuel:.0f} ({fuel_delta:+.0f})  Speed: {speed:.1f} ({speed_delta:+.1f})",
        True,
        WHITE,
    )
    screen.blit(mass_surf, (width // 2 - mass_surf.get_width() // 2, height - 160))
    screen.blit(hull_surf, (width // 2 - hull_surf.get_width() // 2, height - 132))
    penalty_color = RED if overloaded else (200, 200, 200)
    penalty_text = f"Fuel Burn Mult: x{fuel_rate:.2f}"
    if overloaded:
        penalty_text += f"  OVER LIMIT +{overload_ratio * 100:.0f}%"
    penalty_surf = font.render(penalty_text, True, penalty_color)
    screen.blit(penalty_surf, (width // 2 - penalty_surf.get_width() // 2, height - 104))

    if selected_slot is not None:
        type_matches = 0
        for module in modules.values():
            if not isinstance(module, dict):
                continue
            if module.get("type") != selected_slot.get("type"):
                continue
            if size_rank.get(str(module.get("slot_size", "S")), 1) > size_rank.get(
                str(selected_slot.get("slot_size", "S")), 1
            ):
                continue
            type_matches += 1
        unlocked_matches = 0
        if selected_slot is not None:
            for module_id in unlocked_module_ids:
                module = modules.get(module_id, {})
                if not isinstance(module, dict):
                    continue
                if module.get("type") != selected_slot.get("type"):
                    continue
                if size_rank.get(str(module.get("slot_size", "S")), 1) > size_rank.get(
                    str(selected_slot.get("slot_size", "S")), 1
                ):
                    continue
                unlocked_matches += 1
        compat = font.render(
            f"Compatible Modules: {unlocked_matches}/{type_matches} unlocked",
            True,
            (210, 210, 210),
        )
        screen.blit(compat, (width // 2 - compat.get_width() // 2, height - 188))

    if selected_module:
        stats = selected_module.get("stats", {})
        if isinstance(stats, dict):
            stat_chunks: list[str] = []
            if "damage" in stats:
                stat_chunks.append(f"DMG {float(stats['damage']):.0f}")
            if "fire_rate" in stats:
                stat_chunks.append(f"ROF {float(stats['fire_rate']):.2f}")
            if "ammo" in stats:
                stat_chunks.append(f"AMMO {int(stats['ammo'])}")
            if "gimbal_degrees" in stats:
                stat_chunks.append(f"GIMBAL ±{float(stats['gimbal_degrees']):.0f}°")
            if "hull_bonus" in stats:
                stat_chunks.append(f"HULL +{float(stats['hull_bonus']):.0f}")
            if "fuel_bonus" in stats:
                stat_chunks.append(f"FUEL +{float(stats['fuel_bonus']):.0f}")
            if stat_chunks:
                stat_surf = font.render(" | ".join(stat_chunks), True, (210, 210, 210))
                screen.blit(stat_surf, (width // 2 - stat_surf.get_width() // 2, height - 216))
    if status_text:
        status_surf = font.render(status_text, True, NEON_YELLOW)
        screen.blit(status_surf, (width // 2 - status_surf.get_width() // 2, height - 96))
    hint = font.render("↑/↓ Select Slot  ←/→ Cycle Module  ENTER Deploy  TAB Archive  ESC Menu", True, WHITE)
    screen.blit(hint, (width // 2 - hint.get_width() // 2, height - 70))


def draw_debrief_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    summary: dict[str, object],
) -> None:
    width, height = screen.get_size()
    title = big_font.render("DEBRIEF", True, NEON_GREEN)
    screen.blit(title, (width // 2 - title.get_width() // 2, 80))
    y = 170
    lines = [
        f"Clone Number: {summary.get('clone_number', 0)}",
        f"Outcome: {summary.get('outcome', 'N/A')}",
        f"Survival Time: {summary.get('survival_time', 0.0):.1f}s",
        f"Kills: {summary.get('kills', 0)}",
        f"Ammo Spent: {summary.get('ammo_spent', 0)}",
        f"Fuel Spent: {summary.get('fuel_spent', 0.0):.1f}",
        f"Hull Damaged: {summary.get('hull_damage', 0.0):.1f}",
        f"Data Earned: +{summary.get('data_earned', 0.0):.2f} GB",
        f"Total Data: {summary.get('total_data_gb', 0.0):.2f} GB",
    ]
    for line in lines:
        surf = font.render(line, True, WHITE)
        screen.blit(surf, (width // 2 - surf.get_width() // 2, y))
        y += 36
    hint = font.render("ENTER Return To Fitting   M Main Menu", True, NEON_YELLOW)
    screen.blit(hint, (width // 2 - hint.get_width() // 2, height - 80))


def draw_data_archive_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    total_data_gb: float,
    total_runs: int,
    entries: list[dict[str, object]],
    selected_index: int,
    modules: dict[str, dict[str, object]],
    status_text: str,
) -> None:
    width, height = screen.get_size()
    title = big_font.render("DATA ARCHIVE", True, NEON_MAGENTA)
    screen.blit(title, (width // 2 - title.get_width() // 2, 80))
    lines = [
        f"Total Data: {total_data_gb:.2f} GB",
        f"Total Runs: {total_runs}",
    ]
    y = 180
    for line in lines:
        surf = font.render(line, True, WHITE)
        screen.blit(surf, (width // 2 - surf.get_width() // 2, y))
        y += 40
    y += 10
    visible_entries = entries[:10]
    for i, entry in enumerate(visible_entries):
        unlocked = bool(entry.get("unlocked", False))
        cost = int(entry.get("unlock_cost", 0))
        status = "UNLOCKED" if unlocked else f"{cost} GB"
        if unlocked:
            color = NEON_GREEN
        elif cost > total_data_gb:
            color = RED if i == selected_index else (200, 120, 120)
        else:
            color = NEON_YELLOW if i == selected_index else WHITE
        text = font.render(
            f"{i + 1}. T{entry.get('tier', 1)} {entry.get('name', 'Unknown')} [{entry.get('type', '')}] - {status}",
            True,
            color,
        )
        screen.blit(text, (width // 2 - 320, y))
        y += 30
    if entries:
        clamped_index = max(0, min(selected_index, len(entries) - 1))
        selected = entries[clamped_index]
        module = modules.get(str(selected.get("id", "")), {})
        stat_line: list[str] = []
        stats = module.get("stats", {})
        if isinstance(stats, dict):
            if "damage" in stats:
                stat_line.append(f"DMG {float(stats['damage']):.0f}")
            if "fire_rate" in stats:
                stat_line.append(f"ROF {float(stats['fire_rate']):.2f}")
            if "ammo" in stats:
                stat_line.append(f"AMMO {int(stats['ammo'])}")
            if "hull_bonus" in stats:
                stat_line.append(f"HULL +{float(stats['hull_bonus']):.0f}")
            if "fuel_bonus" in stats:
                stat_line.append(f"FUEL +{float(stats['fuel_bonus']):.0f}")
        mass = int(module.get("mass", 0)) if isinstance(module, dict) else 0
        detail_text = f"Mass {mass}"
        if stat_line:
            detail_text += " | " + " | ".join(stat_line)
        detail_surf = font.render(detail_text, True, (210, 210, 210))
        screen.blit(detail_surf, (width // 2 - detail_surf.get_width() // 2, height - 142))
    if status_text:
        status_surf = font.render(status_text, True, NEON_YELLOW)
        screen.blit(status_surf, (width // 2 - status_surf.get_width() // 2, height - 112))
    hint = font.render("↑/↓ Select  ENTER Unlock  ESC Back To Fitting", True, NEON_YELLOW)
    screen.blit(hint, (width // 2 - hint.get_width() // 2, height - 80))
