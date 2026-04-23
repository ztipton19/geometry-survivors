import Phaser from "phaser";

import { COLORS, XP_GEM } from "../constants/settings";
import type { XpGemModel } from "../types/gameplay";

function createNormalGem(scene: Phaser.Scene, x: number, y: number, value: number): XpGemModel {
  const graphic = scene.add.circle(x, y, XP_GEM.normalRadius, COLORS.neonGreen, 0.95);
  graphic.setStrokeStyle(2, COLORS.neonCyan, 0.75);
  return { graphic, x, y, value, kind: "normal" };
}

function createOverflowGem(scene: Phaser.Scene, x: number, y: number, value: number): XpGemModel {
  const graphic = scene.add.circle(x, y, XP_GEM.overflowRadius, COLORS.enemyRed, 0.95);
  graphic.setStrokeStyle(3, 0xffd2d2, 0.9);
  return { graphic, x, y, value, kind: "overflow" };
}

function findNearbyOverflowGem(
  xpgems: XpGemModel[],
  playerX: number,
  playerY: number,
): XpGemModel | null {
  let best: XpGemModel | null = null;
  let bestDistanceSquared = XP_GEM.overflowMergeRadius * XP_GEM.overflowMergeRadius;

  for (const gem of xpgems) {
    if (gem.kind !== "overflow") {
      continue;
    }

    const dx = gem.x - playerX;
    const dy = gem.y - playerY;
    const distanceSquared = dx * dx + dy * dy;
    if (distanceSquared <= bestDistanceSquared) {
      bestDistanceSquared = distanceSquared;
      best = gem;
    }
  }

  return best;
}

function spawnOverflowPosition(playerX: number, playerY: number): Phaser.Math.Vector2 {
  const angle = Phaser.Math.FloatBetween(0, Math.PI * 2);
  const distance = Phaser.Math.FloatBetween(
    XP_GEM.overflowSpawnMinRadius,
    XP_GEM.overflowSpawnMaxRadius,
  );

  return new Phaser.Math.Vector2(
    playerX + Math.cos(angle) * distance,
    playerY + Math.sin(angle) * distance,
  );
}

export function spawnXpGem(
  scene: Phaser.Scene,
  xpgems: XpGemModel[],
  playerX: number,
  playerY: number,
  x: number,
  y: number,
  value: number,
): XpGemModel[] {
  const looseGemCount = xpgems.filter((gem) => gem.kind === "normal").length;
  if (looseGemCount < XP_GEM.maxLooseGems) {
    return [...xpgems, createNormalGem(scene, x, y, value)];
  }

  const overflowGem = findNearbyOverflowGem(xpgems, playerX, playerY);
  if (overflowGem) {
    overflowGem.value += value;
    return xpgems;
  }

  const position = spawnOverflowPosition(playerX, playerY);
  return [...xpgems, createOverflowGem(scene, position.x, position.y, value)];
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

    remainingGems.push(gem);
  }

  return remainingGems;
}
