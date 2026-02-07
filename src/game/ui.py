"""UI rendering helpers."""

import pygame

from game.entities.player import Player
from game.settings import (
    NEON_CYAN,
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
    enemy_count: int,
    remaining: float,
) -> None:
    mm = int(remaining) // 60
    ss = int(remaining) % 60
    timer_text = f"{mm:02d}:{ss:02d}"
    shield_text = "   SHIELD ---"
    if player.shield_level >= 0:
        shield_text = f"   SHIELD {int(player.shield_hp):3d}/{int(player.shield_max):3d}"
    hud = font.render(
        f"HP {int(player.hp):3d}{shield_text}   ENEMIES {enemy_count:3d}   TIME {timer_text}",
        True,
        WHITE,
    )
    screen.blit(hud, (16, 12))
    
    # Draw XP bar
    draw_xp_bar(screen, font, player, 16, 36)


def draw_xp_bar(
    screen: pygame.Surface,
    font: pygame.font.Font,
    player: Player,
    x: int,
    y: int,
    width: int = 200,
) -> None:
    """Draw XP progress bar."""
    bar_height = 20
    # Background
    pygame.draw.rect(screen, (30, 30, 30), (x, y, width, bar_height), 0, 4)
    # Fill
    if player.xp_to_next > 0:
        fill_width = int((player.xp / player.xp_to_next) * width)
        fill_width = min(fill_width, width)
        pygame.draw.rect(screen, NEON_CYAN, (x, y, fill_width, bar_height), 0, 4)
    # Border
    pygame.draw.rect(screen, WHITE, (x, y, width, bar_height), 1, 4)
    # Text (smaller font to keep it fully inside the bar)
    level_font = pygame.font.SysFont("consolas", 14)
    level_text = level_font.render(f"LVL {player.level}", True, WHITE)
    screen.blit(
        level_text,
        (
            x + width // 2 - level_text.get_width() // 2,
            y + (bar_height - level_text.get_height()) // 2,
        ),
    )


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
