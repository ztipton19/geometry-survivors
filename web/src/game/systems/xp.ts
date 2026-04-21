import Phaser from "phaser";

import { COLORS, XP_GEM } from "../constants/settings";
import type { XpGemModel } from "../types/gameplay";

export function spawnXpGem(
  scene: Phaser.Scene,
  x: number,
  y: number,
  value: number,
): XpGemModel {
  const graphic = scene.add.circle(x, y, 6, COLORS.neonGreen, 0.95);
  graphic.setStrokeStyle(2, COLORS.neonCyan, 0.75);
  return { graphic, x, y, value, lifetime: XP_GEM.lifetime };
}

export function updateXpGems(
  xpgems: XpGemModel[],
  playerX: number,
  playerY: number,
  tractorRange: number,
  dt: number,
  onCollect: (value: number) => void,
): XpGemModel[] {
  const remainingGems: XpGemModel[] = [];

  for (const gem of xpgems) {
    gem.lifetime -= dt;
    const dx = playerX - gem.x;
    const dy = playerY - gem.y;
    const distanceSquared = dx * dx + dy * dy;

    if (tractorRange > 0 && distanceSquared < tractorRange * tractorRange) {
      const distance = Math.max(0.001, Math.sqrt(distanceSquared));
      gem.x += (dx / distance) * XP_GEM.magnetSpeed * dt;
      gem.y += (dy / distance) * XP_GEM.magnetSpeed * dt;
    }

    gem.graphic.setPosition(gem.x, gem.y);
    if (distanceSquared <= XP_GEM.pickupRadius * XP_GEM.pickupRadius) {
      gem.graphic.destroy();
      onCollect(gem.value);
      continue;
    }

    if (gem.lifetime > 0) {
      remainingGems.push(gem);
    } else {
      gem.graphic.destroy();
    }
  }

  return remainingGems;
}
