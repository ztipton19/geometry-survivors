"""Input handling."""

import pygame

from game.entities.player import Player
from game.physics import apply_player_controls


def handle_player_input(player: Player, dt: float) -> None:
    keys = pygame.key.get_pressed()
    turn = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    thrust = bool(keys[pygame.K_w] or keys[pygame.K_UP])
    reverse = bool(keys[pygame.K_s] or keys[pygame.K_DOWN])
    apply_player_controls(player, float(turn), thrust, reverse, dt)
