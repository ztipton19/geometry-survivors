"""Threat collection and lightweight tactical overlay rendering."""

from __future__ import annotations

import math

import pygame

from game.entities.enemy import Enemy
from game.settings import WHITE


def collect_threats(
    enemies: list[Enemy],
    player_pos: tuple[float, float],
) -> list[dict[str, float | Enemy]]:
    px, py = player_pos
    threats: list[dict[str, float | Enemy]] = []
    for enemy in enemies:
        dx = enemy.x - px
        dy = enemy.y - py
        distance = math.hypot(dx, dy)
        eta = distance / max(1.0, enemy.speed)
        bearing = math.degrees(math.atan2(dy, dx))
        threats.append(
            {"enemy": enemy, "distance": distance, "eta": eta, "bearing": bearing}
        )
    threats.sort(key=lambda threat: float(threat["eta"]))
    return threats


def draw_edge_indicators(
    screen: pygame.Surface,
    threats: list[dict[str, float | Enemy]],
    world_to_screen: callable,
    cam_x: float,
    cam_y: float,
    shake_x: float,
    shake_y: float,
) -> None:
    width, height = screen.get_size()
    margin = 24
    for threat in threats:
        enemy = threat["enemy"]
        ex, ey = world_to_screen(enemy.x, enemy.y, cam_x, cam_y, shake_x, shake_y)
        if 0 <= ex <= width and 0 <= ey <= height:
            continue
        cx = min(width - margin, max(margin, ex))
        cy = min(height - margin, max(margin, ey))
        eta = float(threat["eta"])
        if eta < 8:
            color = (255, 80, 80)
        elif eta < 16:
            color = (255, 220, 80)
        else:
            color = WHITE
        enemy = threat["enemy"]
        sides = max(3, int(getattr(enemy, "sides", 3)))
        radius = 7
        points = []
        for i in range(sides):
            ang = (math.tau / sides) * i - math.pi / 2.0
            points.append((int(cx + math.cos(ang) * radius), int(cy + math.sin(ang) * radius)))
        pygame.draw.polygon(screen, color, points, 2)
        eta_font = pygame.font.SysFont("consolas", 13)
        eta_text = eta_font.render(f"{eta:0.0f}s", True, color)
        screen.blit(eta_text, (int(cx + 10), int(cy - 8)))


def draw_threat_board(
    screen: pygame.Surface,
    font: pygame.font.Font,
    threats: list[dict[str, float | Enemy]],
) -> None:
    width, _ = screen.get_size()
    panel = pygame.Surface((360, 240), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 160))
    screen.blit(panel, (width - 380, 80))
    title = font.render("THREAT BOARD", True, (255, 255, 255))
    screen.blit(title, (width - 368, 92))
    for i, threat in enumerate(threats[:8]):
        eta = float(threat["eta"])
        bearing = float(threat["bearing"])
        text = font.render(f"{i+1}. ETA {eta:4.1f}s  BRG {bearing:6.1f}", True, (220, 220, 220))
        screen.blit(text, (width - 368, 118 + i * 22))
