import Phaser from "phaser";

import { COLORS, ENEMY, GAME_HEIGHT, GAME_WIDTH } from "../constants/settings";
import {
  chooseEnemySides,
  ENEMY_SCALING,
  getBossSides,
  type EnemyProfileKey,
  shouldSpawnBoss,
} from "../data/enemies";
import { regularPolygonPoints } from "../utils/geometry";
import type { EnemyModel } from "../types/gameplay";

export function computeSpawnInterval(elapsed: number): number {
  return Math.max(
    ENEMY.spawnIntervalMin,
    ENEMY.spawnIntervalStart - elapsed * ENEMY.spawnIntervalDecay,
  );
}

export function spawnEnemy(
  scene: Phaser.Scene,
  elapsed: number,
  playerX: number,
  playerY: number,
): EnemyModel {
  const viewRadius = Math.max(GAME_WIDTH, GAME_HEIGHT) * 0.65;
  const margin = 140;
  const distance = viewRadius + margin;
  const angle = Phaser.Math.FloatBetween(0, Math.PI * 2);
  const x = playerX + Math.cos(angle) * distance;
  const y = playerY + Math.sin(angle) * distance;

  const minutes = elapsed / 60;
  const isBoss = shouldSpawnBoss(minutes);
  const sides = isBoss ? getBossSides(minutes) : chooseEnemySides(minutes);
  const scaling = ENEMY_SCALING[isBoss ? "boss" : (sides as EnemyProfileKey)];

  const baseSpeed = ENEMY.baseSpeed;
  const baseHp = ENEMY.baseHp;
  const baseDamage = ENEMY.baseDamage;
  const radius = ENEMY.radius * scaling.radius;

  return {
    graphic: createEnemyGraphic(scene, x, y, sides, radius, isBoss),
    x,
    y,
    hp: baseHp * scaling.hp,
    speed: baseSpeed * scaling.speed,
    damage: baseDamage * scaling.damage,
    xpValue: Math.round(ENEMY.baseXp + baseHp * scaling.xp * ENEMY.xpPerHp),
    radius,
    isBoss,
    touchCooldown: 0,
  };
}

function createEnemyGraphic(
  scene: Phaser.Scene,
  x: number,
  y: number,
  sides: number,
  radius: number,
  isBoss: boolean,
): Phaser.GameObjects.Shape {
  if (sides <= 1) {
    return scene.add
      .circle(x, y, radius, isBoss ? 0xff834d : COLORS.enemyRed, 0.88)
      .setStrokeStyle(2, 0xffd2bf, isBoss ? 0.85 : 0.35);
  }

  return scene.add
    .polygon(
      x,
      y,
      regularPolygonPoints(sides, radius),
      isBoss ? 0xff834d : COLORS.enemyRed,
      0.85,
    )
    .setStrokeStyle(2, isBoss ? 0xfff0cf : 0xff9898, isBoss ? 0.8 : 0.5);
}
