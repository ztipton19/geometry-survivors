"""UI rendering helpers."""

import pygame

from game.entities.player import Player
from game.settings import (
    HURDLE_COOLDOWN,
    NEON_BLUE,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_YELLOW,
    RED,
    WHITE,
)
from game.upgrades import UPGRADES


def draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    player: Player,
    remaining: float,
    weapon_slots: list[dict[str, object]],
    utility_slots: list[dict[str, object]],
) -> None:
    width, height = screen.get_size()
    hud_color = (0, 212, 255)
    alpha = 166  # ~65%
    text_color = (220, 245, 255)

    mm = int(remaining) // 60
    ss = int(remaining) % 60
    timer_text = f"{mm:02d}:{ss:02d}"
    draw_xp_bar(screen, font, player, 16, 16, width=260, color=hud_color, alpha=alpha)

    time_font = pygame.font.SysFont("consolas", 40)
    time_surf = time_font.render(timer_text, True, text_color)
    screen.blit(time_surf, (width // 2 - time_surf.get_width() // 2, 10))

    kill_surf = font.render(f"KILLS {player.enemies_killed:04d}", True, text_color)
    screen.blit(kill_surf, (width - kill_surf.get_width() - 16, 20))

    weapon_rect = pygame.Rect(16, height - 178, 252, 162)
    utility_rect = pygame.Rect(width - 268, height - 178, 252, 162)
    center_width = max(320, width - weapon_rect.width - utility_rect.width - 80)
    center_rect = pygame.Rect((width - center_width) // 2, height - 178, center_width, 162)

    _draw_panel(screen, weapon_rect, hud_color, alpha)
    _draw_panel(screen, center_rect, hud_color, alpha)
    _draw_panel(screen, utility_rect, hud_color, alpha)

    _draw_slot_grid(screen, font, weapon_rect, weapon_slots, text_color)
    _draw_slot_grid(screen, font, utility_rect, utility_slots, text_color)

    boost_ratio = max(0.0, min(1.0, float(player.boost_charge)))
    throttle_ratio = max(0.0, min(1.0, float(player.throttle_level)))
    hp_ratio = max(0.0, min(1.0, player.hp / max(1.0, player.max_hp)))
    shield_ratio = 0.0
    if player.shield_max > 0:
        shield_ratio = max(0.0, min(1.0, player.shield_hp / player.shield_max))

    center_x = center_rect.x + 14
    center_w = center_rect.width - 28
    _draw_progress_bar(screen, font, "BOOST", boost_ratio, center_x, center_rect.y + 16, center_w, NEON_BLUE)
    _draw_progress_bar(
        screen,
        font,
        f"THROTTLE {int(throttle_ratio * 100):3d}%",
        throttle_ratio,
        center_x,
        center_rect.y + 46,
        center_w,
        NEON_YELLOW,
    )
    _draw_progress_bar(screen, font, "HP", hp_ratio, center_x, center_rect.y + 98, center_w, NEON_GREEN)
    _draw_progress_bar(
        screen,
        font,
        "SHIELD",
        shield_ratio,
        center_x,
        center_rect.y + 128,
        center_w,
        NEON_BLUE,
    )

    minimap_rect = pygame.Rect(center_rect.centerx - 56, center_rect.y + 66, 112, 26)
    pygame.draw.rect(screen, (18, 30, 38), minimap_rect, 0, 4)
    pygame.draw.rect(screen, hud_color, minimap_rect, 1, 4)
    minimap_text = pygame.font.SysFont("consolas", 12).render("MINI MAP TBD", True, text_color)
    screen.blit(
        minimap_text,
        (
            minimap_rect.centerx - minimap_text.get_width() // 2,
            minimap_rect.centery - minimap_text.get_height() // 2,
        ),
    )


def draw_xp_bar(
    screen: pygame.Surface,
    font: pygame.font.Font,
    player: Player,
    x: int,
    y: int,
    width: int = 200,
    color: tuple[int, int, int] = (0, 212, 255),
    alpha: int = 166,
) -> None:
    """Draw XP progress bar."""
    bar_height = 24
    bg_surface = pygame.Surface((width, bar_height), pygame.SRCALPHA)
    bg_surface.fill((14, 24, 34, alpha))
    screen.blit(bg_surface, (x, y))
    # Fill
    if player.xp_to_next > 0:
        fill_width = int((player.xp / player.xp_to_next) * width)
        fill_width = min(fill_width, width)
        pygame.draw.rect(screen, color, (x, y, fill_width, bar_height), 0, 4)
    # Border
    pygame.draw.rect(screen, color, (x, y, width, bar_height), 1, 4)
    level_font = pygame.font.SysFont("consolas", 14)
    level_text = level_font.render(f"XP LVL {player.level}", True, WHITE)
    screen.blit(
        level_text,
        (
            x + width // 2 - level_text.get_width() // 2,
            y + (bar_height - level_text.get_height()) // 2,
        ),
    )


def _draw_panel(
    screen: pygame.Surface,
    rect: pygame.Rect,
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((10, 20, 28, alpha))
    screen.blit(panel, rect.topleft)
    pygame.draw.rect(screen, color, rect, 1, 8)


def _draw_progress_bar(
    screen: pygame.Surface,
    font: pygame.font.Font,
    label: str,
    ratio: float,
    x: int,
    y: int,
    width: int,
    color: tuple[int, int, int],
) -> None:
    bar_h = 18
    pygame.draw.rect(screen, (18, 18, 24), (x, y, width, bar_h), 0, 4)
    fill_w = int(width * max(0.0, min(1.0, ratio)))
    if fill_w > 0:
        pygame.draw.rect(screen, color, (x, y, fill_w, bar_h), 0, 4)
    pygame.draw.rect(screen, color, (x, y, width, bar_h), 1, 4)
    label_surf = pygame.font.SysFont("consolas", 14).render(label, True, WHITE)
    screen.blit(label_surf, (x + 6, y + 1))


def _draw_slot_grid(
    screen: pygame.Surface,
    font: pygame.font.Font,
    rect: pygame.Rect,
    slots: list[dict[str, object]],
    text_color: tuple[int, int, int],
) -> None:
    cols = 3
    rows = 2
    cell_w = 72
    cell_h = 68
    gap_x = 8
    gap_y = 8
    start_x = rect.x + (rect.width - (cols * cell_w + (cols - 1) * gap_x)) // 2
    start_y = rect.y + (rect.height - (rows * cell_h + (rows - 1) * gap_y)) // 2
    icon_font = pygame.font.SysFont("consolas", 18)
    small_font = pygame.font.SysFont("consolas", 12)

    for idx in range(6):
        row = idx // cols
        col = idx % cols
        slot = slots[idx] if idx < len(slots) else {}
        sx = start_x + col * (cell_w + gap_x)
        sy = start_y + row * (cell_h + gap_y)
        slot_rect = pygame.Rect(sx, sy, cell_w, cell_h)
        pygame.draw.rect(screen, (12, 24, 34), slot_rect, 0, 6)
        pygame.draw.rect(screen, (0, 212, 255), slot_rect, 1, 6)

        icon_color = slot.get("icon_color", (80, 80, 80))
        pygame.draw.rect(screen, icon_color, (sx + 5, sy + 6, 18, 18), 0, 3)

        type_icon = str(slot.get("type_icon", ""))
        if type_icon:
            type_surf = icon_font.render(type_icon, True, text_color)
            screen.blit(type_surf, (sx + cell_w - type_surf.get_width() - 6, sy + 4))

        name = str(slot.get("label", "LOCKED"))
        name_surf = small_font.render(name[:8], True, text_color)
        screen.blit(name_surf, (sx + 6, sy + 30))

        ratio = float(slot.get("cooldown_ratio", 0.0))
        bar_y = sy + cell_h - 12
        pygame.draw.rect(screen, (20, 20, 26), (sx + 6, bar_y, cell_w - 12, 6), 0, 3)
        fill = int((cell_w - 12) * max(0.0, min(1.0, ratio)))
        if fill > 0:
            pygame.draw.rect(screen, (0, 212, 255), (sx + 6, bar_y, fill, 6), 0, 3)
        pygame.draw.rect(screen, (0, 212, 255), (sx + 6, bar_y, cell_w - 12, 6), 1, 3)

        if str(slot.get("label", "")).lower() == "hurdle":
            cd = float(slot.get("remaining_cd", 0.0))
            if cd > 0:
                cd_surf = font.render(f"{cd:.1f}", True, text_color)
                screen.blit(cd_surf, (sx + cell_w - cd_surf.get_width() - 4, sy + 26))
            elif HURDLE_COOLDOWN > 0:
                ready_surf = small_font.render("READY", True, NEON_GREEN)
                screen.blit(ready_surf, (sx + cell_w - ready_surf.get_width() - 4, sy + 26))


def get_level_up_card_rects(
    screen: pygame.Surface,
    option_count: int,
) -> list[pygame.Rect]:
    """Get card rectangles for level-up options."""
    width, height = screen.get_size()
    card_width = min(760, max(560, width - 120))
    card_height = 130
    gap = 18
    total_height = option_count * card_height + max(0, option_count - 1) * gap
    start_y = max(190, (height - total_height) // 2 + 20)
    start_x = (width - card_width) // 2
    return [
        pygame.Rect(start_x, start_y + i * (card_height + gap), card_width, card_height)
        for i in range(option_count)
    ]


def _wrap_text(
    font: pygame.font.Font, text: str, max_width: int
) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        test = f"{current} {word}"
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_level_up_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    options: list[str],
    player: Player,
) -> None:
    """Draw level-up upgrade selection screen."""
    width, height = screen.get_size()
    # Semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Title
    title = big_font.render("LEVEL UP!", True, NEON_YELLOW)
    screen.blit(title, (width // 2 - title.get_width() // 2, 100))
    
    subtitle = font.render("Choose an upgrade (1, 2, or 3)", True, WHITE)
    screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, 150))
    
    # Draw upgrade cards
    card_rects = get_level_up_card_rects(screen, len(options))
    colors = [NEON_CYAN, NEON_MAGENTA, NEON_GREEN]
    
    for i, option_id in enumerate(options):
        upgrade = UPGRADES[option_id]
        card = card_rects[i]
        
        # Card background
        pygame.draw.rect(
            screen, (40, 40, 50), card, 0, 10
        )
        pygame.draw.rect(
            screen, colors[i], card, 2, 10
        )
        
        # Option number
        num_text = big_font.render(str(i + 1), True, colors[i])
        screen.blit(num_text, (card.x + 15, card.y + 6))
        
        # Upgrade name
        name_text = font.render(upgrade.name, True, WHITE)
        screen.blit(name_text, (card.x + 70, card.y + 18))
        
        current_level = getattr(player, f"{option_id}_level", 0)
        if current_level < 0:
            description = upgrade.get_description(-1)
            detail_lines = _wrap_text(font, description, card.width - 170)
        else:
            next_level = min(current_level + 1, upgrade.max_level)
            current_desc = upgrade.get_description(current_level)
            next_desc = upgrade.get_description(next_level)
            detail_lines = _wrap_text(
                font,
                f"Current: {current_desc} | Next: {next_desc}",
                card.width - 170,
            )
        for line_idx, line in enumerate(detail_lines[:3]):
            desc_text = font.render(line, True, (200, 200, 200))
            screen.blit(desc_text, (card.x + 70, card.y + 48 + line_idx * 22))
        
        # Category badge
        category_text = font.render(upgrade.category.upper(), True, colors[i])
        screen.blit(category_text, (card.right - 140, card.y + 18))
        
        # Press to select hint
        hint_text = font.render(
            "Press " + str(i + 1) + " or click to select",
            True,
            (150, 150, 150),
        )
        screen.blit(hint_text, (card.right - hint_text.get_width() - 16, card.bottom - 28))


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
            f"Level Reached: {player.level}",
            f"Enemies Killed: {player.enemies_killed}",
            f"Damage Dealt: {player.damage_dealt}",
            f"Upgrades Collected: {player.upgrades_collected}",
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
