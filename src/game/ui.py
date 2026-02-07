"""UI rendering helpers."""

import random

import pygame

from game.entities.player import Player
from game.settings import (
    BG,
    HEIGHT,
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_YELLOW,
    RED,
    WHITE,
    WIDTH,
)
from game.upgrades import UPGRADES


def draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    player: Player,
    fire_cd: float,
    enemy_count: int,
    remaining: float,
) -> None:
    mm = int(remaining) // 60
    ss = int(remaining) % 60
    timer_text = f"{mm:02d}:{ss:02d}"
    hud = font.render(
        f"HP {int(player.hp):3d}   FIRE {fire_cd:.2f}s   ENEMIES {enemy_count:3d}   TIME {timer_text}",
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
    # Background
    pygame.draw.rect(screen, (30, 30, 30), (x, y, width, 16), 0, 4)
    # Fill
    if player.xp_to_next > 0:
        fill_width = int((player.xp / player.xp_to_next) * width)
        fill_width = min(fill_width, width)
        pygame.draw.rect(screen, NEON_CYAN, (x, y, fill_width, 16), 0, 4)
    # Border
    pygame.draw.rect(screen, WHITE, (x, y, width, 16), 1, 4)
    # Text
    level_text = font.render(f"LVL {player.level}", True, WHITE)
    screen.blit(level_text, (x + width // 2 - level_text.get_width() // 2, y + 1))


def draw_level_up_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    options: list[str],
) -> None:
    """Draw level-up upgrade selection screen."""
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Title
    title = big_font.render("LEVEL UP!", True, NEON_YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    
    subtitle = font.render("Choose an upgrade (1, 2, or 3)", True, WHITE)
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 150))
    
    # Draw upgrade cards
    card_width = 320
    card_height = 220
    card_y = 200
    gap = 30
    total_width = (card_width * 3) + (gap * 2)
    start_x = (WIDTH - total_width) // 2
    
    colors = [NEON_CYAN, NEON_MAGENTA, NEON_GREEN]
    
    for i, option_id in enumerate(options):
        upgrade = UPGRADES[option_id]
        card_x = start_x + i * (card_width + gap)
        
        # Card background
        pygame.draw.rect(
            screen, (40, 40, 50), (card_x, card_y, card_width, card_height), 0, 10
        )
        pygame.draw.rect(
            screen, colors[i], (card_x, card_y, card_width, card_height), 2, 10
        )
        
        # Option number
        num_text = big_font.render(str(i + 1), True, colors[i])
        screen.blit(num_text, (card_x + 15, card_y + 15))
        
        # Upgrade name
        name_text = font.render(upgrade.name, True, WHITE)
        screen.blit(name_text, (card_x + 60, card_y + 20))
        
        # Upgrade description
        desc_text = font.render(upgrade.description, True, (200, 200, 200))
        # Wrap text if too long
        if desc_text.get_width() > card_width - 40:
            words = upgrade.description.split()
            line1 = " ".join(words[:len(words)//2])
            line2 = " ".join(words[len(words)//2:])
            line1_text = font.render(line1, True, (200, 200, 200))
            line2_text = font.render(line2, True, (200, 200, 200))
            screen.blit(line1_text, (card_x + card_width // 2 - line1_text.get_width() // 2, card_y + 60))
            screen.blit(line2_text, (card_x + card_width // 2 - line2_text.get_width() // 2, card_y + 85))
        else:
            screen.blit(desc_text, (card_x + card_width // 2 - desc_text.get_width() // 2, card_y + 60))
        
        # Category badge
        category_text = font.render(upgrade.category.upper(), True, colors[i])
        screen.blit(category_text, (card_x + card_width // 2 - category_text.get_width() // 2, card_y + 115))
        
        # Press to select hint
        hint_text = font.render("Press " + str(i + 1) + " to select", True, (150, 150, 150))
        screen.blit(hint_text, (card_x + card_width // 2 - hint_text.get_width() // 2, card_y + card_height - 30))


def draw_end_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    state: str,
    player: Player | None = None,
) -> None:
    if state not in ("WIN", "LOSE"):
        return
    msg = "YOU SURVIVED" if state == "WIN" else "YOU DIED"
    sub = "Press R to restart or ESC to quit"
    title = big_font.render(msg, True, NEON_GREEN if state == "WIN" else RED)
    subtitle = font.render(sub, True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 80))
    
    # Stats display
    if player:
        stats_y = HEIGHT // 2 - 20
        stats = [
            f"Level Reached: {player.level}",
            f"Enemies Killed: {player.enemies_killed}",
            f"Damage Dealt: {player.damage_dealt}",
            f"Upgrades Collected: {player.upgrades_collected}",
        ]
        for i, stat in enumerate(stats):
            stat_surf = font.render(stat, True, WHITE)
            screen.blit(stat_surf, (WIDTH // 2 - stat_surf.get_width() // 2, stats_y + i * 25))
