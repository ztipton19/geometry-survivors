"""Narrative cutscene support."""

from __future__ import annotations

import pygame


class Cutscene:
    def __init__(
        self,
        text: str,
        typing_speed: float = 40.0,
        skippable: bool = True,
        padding: int = 100,
        line_spacing: int = 6,
    ) -> None:
        self.full_text = text.strip("\n")
        self.displayed_text = ""
        self.typing_speed = typing_speed
        self.char_index = 0
        self.time_accumulator = 0.0
        self.finished = False
        self.skippable = skippable
        self.padding = padding
        self.line_spacing = line_spacing

    def update(self, dt: float) -> None:
        if self.finished:
            return
        self.time_accumulator += dt
        chars_to_add = int(self.time_accumulator * self.typing_speed)
        if chars_to_add <= 0:
            return
        self.time_accumulator -= chars_to_add / self.typing_speed
        self.char_index = min(self.char_index + chars_to_add, len(self.full_text))
        self.displayed_text = self.full_text[: self.char_index]
        if self.char_index >= len(self.full_text):
            self.finished = True

    def skip(self) -> None:
        if not self.skippable:
            return
        self.displayed_text = self.full_text
        self.char_index = len(self.full_text)
        self.finished = True

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        color: tuple[int, int, int] = (200, 200, 200),
        prompt_color: tuple[int, int, int] = (150, 150, 150),
    ) -> None:
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        max_width = width - self.padding * 2
        paragraphs = self.displayed_text.split("\n")
        lines: list[str] = []
        for para in paragraphs:
            if not para.strip():
                lines.append("")
                continue
            lines.extend(_wrap_text(font, para, max_width))

        total_height = len(lines) * (font.get_height() + self.line_spacing)
        y_offset = max(self.padding, height // 3 - total_height // 2)

        for line in lines:
            if not line:
                y_offset += font.get_height() + self.line_spacing
                continue
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(width // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += font.get_height() + self.line_spacing

        prompt_text = "Press SPACE to continue" if self.finished else "Press SPACE to skip"
        prompt = font.render(prompt_text, True, prompt_color)
        prompt_rect = prompt.get_rect(center=(width // 2, height - self.padding // 2))
        screen.blit(prompt, prompt_rect)


def _wrap_text(font: pygame.font.Font, text: str, max_width: int) -> list[str]:
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
