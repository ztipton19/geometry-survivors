"""Input handling."""

import pygame

from game import settings
from game.entities.player import Player
from game.settings import PLAYER_RADIUS, PLAYER_SPEED
from game.util import clamp, norm


def handle_player_input(player: Player, dt: float) -> None:
    keys = pygame.key.get_pressed()
    mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
    nx, ny = norm(float(mx), float(my))

    player.x += nx * PLAYER_SPEED * dt
    player.y += ny * PLAYER_SPEED * dt
    player.x = clamp(player.x, PLAYER_RADIUS, settings.WIDTH - PLAYER_RADIUS)
    player.y = clamp(player.y, PLAYER_RADIUS, settings.HEIGHT - PLAYER_RADIUS)
