"""Input handling."""

import pygame

from game.entities.player import Player
from game.physics import apply_player_controls


def handle_player_input(player: Player, dt: float) -> None:
    keys = pygame.key.get_pressed()
    rotate = float(
        (keys[pygame.K_e] or keys[pygame.K_RIGHT]) - (keys[pygame.K_q] or keys[pygame.K_LEFT])
    )
    strafe = float((keys[pygame.K_d]) - (keys[pygame.K_a]))

    # Incremental throttle control
    throttle_increment = bool(keys[pygame.K_w] or keys[pygame.K_UP])
    throttle_decrement = bool(keys[pygame.K_s] or keys[pygame.K_DOWN])

    # Instant throttle override
    max_thrust = bool(keys[pygame.K_LSHIFT])
    cut_engines = bool(keys[pygame.K_LCTRL])

    boost_pressed = bool(keys[pygame.K_SPACE])

    player.tap_clock += dt
    left_down = bool(keys[pygame.K_a])
    right_down = bool(keys[pygame.K_d])
    hurdle_direction = 0.0

    if left_down and not player.left_was_down:
        if player.tap_clock - player.last_left_tap <= 0.25:
            hurdle_direction = -1.0
        player.last_left_tap = player.tap_clock
    if right_down and not player.right_was_down:
        if player.tap_clock - player.last_right_tap <= 0.25:
            hurdle_direction = 1.0
        player.last_right_tap = player.tap_clock
    player.left_was_down = left_down
    player.right_was_down = right_down

    apply_player_controls(
        player,
        rotate,
        strafe,
        throttle_increment,
        throttle_decrement,
        max_thrust,
        cut_engines,
        boost_pressed,
        hurdle_direction,
        dt,
    )
