"""UI rendering helpers."""

import pygame

from game.entities.player import Player
from game.settings import NEON_GREEN, RED, WHITE, WIDTH, HEIGHT


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


def draw_end_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    state: str,
) -> None:
    if state not in ("WIN", "LOSE"):
        return
    msg = "YOU SURVIVED" if state == "WIN" else "YOU DIED"
    sub = "Press R to restart or ESC to quit"
    title = big_font.render(msg, True, NEON_GREEN if state == "WIN" else RED)
    subtitle = font.render(sub, True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 10))
