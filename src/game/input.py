"""Input handling."""

import pygame

from game.entities.player import Player
from game.util import norm


def handle_player_input(player: Player, dt: float) -> None:
    keys = pygame.key.get_pressed()
    mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
    nx, ny = norm(float(mx), float(my))

    speed = player.get_speed()
    player.x += nx * speed * dt
    player.y += ny * speed * dt
