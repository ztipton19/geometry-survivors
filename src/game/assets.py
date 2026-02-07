"""Asset helpers."""

import pygame


def load_fonts() -> tuple[pygame.font.Font, pygame.font.Font]:
    return (
        pygame.font.SysFont("consolas", 20),
        pygame.font.SysFont("consolas", 48),
    )
