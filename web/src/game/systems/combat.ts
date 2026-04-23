import Phaser from "phaser";

import {
  BULLET,
  COLORS,
  EMP,
  GAME_HEIGHT,
  GAME_WIDTH,
  RAIL_GUN,
  ROCKET,
} from "../constants/settings";
import type {
  BulletModel,
  EmpPulseModel,
  EnemyModel,
  RailGunShotModel,
  RocketModel,
} from "../types/gameplay";
import { distanceToSegmentSquared } from "../utils/geometry";

type HitCallback = (x: number, y: number) => void;
type EnemyDeathCallback = (enemy: EnemyModel) => void;

export function findNearestEnemy(
  enemies: EnemyModel[],
  playerX: number,
  playerY: number,
  camX: number = Number.NEGATIVE_INFINITY,
  camY: number = Number.NEGATIVE_INFINITY,
  camW: number = Number.POSITIVE_INFINITY,
  camH: number = Number.POSITIVE_INFINITY,
): EnemyModel | null {
  let best: EnemyModel | null = null;
  let bestDistanceSquared = Number.POSITIVE_INFINITY;

  for (const enemy of enemies) {
    const visible =
      enemy.x + enemy.radius >= camX &&
      enemy.x - enemy.radius <= camX + camW &&
      enemy.y + enemy.radius >= camY &&
      enemy.y - enemy.radius <= camY + camH;
    if (!visible) {
      continue;
    }

    const dx = enemy.x - playerX;
    const dy = enemy.y - playerY;
    const distanceSquared = dx * dx + dy * dy;
    if (distanceSquared < bestDistanceSquared) {
      bestDistanceSquared = distanceSquared;
      best = enemy;
    }
  }

  return best;
}

export function spawnBullet(
  scene: Phaser.Scene,
  playerX: number,
  playerY: number,
  target: EnemyModel,
  damage: number,
): BulletModel {
  const dx = target.x - playerX;
  const dy = target.y - playerY;
  const baseAngle = Math.atan2(dy, dx);
  const angle = baseAngle + Phaser.Math.FloatBetween(-BULLET.spread, BULLET.spread);
  const graphic = scene.add.circle(playerX, playerY, BULLET.radius, COLORS.neonYellow, 1);
  graphic.setStrokeStyle(1, 0xffffff, 0.65);

  return {
    graphic,
    x: playerX,
    y: playerY,
    vx: Math.cos(angle) * BULLET.speed,
    vy: Math.sin(angle) * BULLET.speed,
    ttl: BULLET.lifetime,
    damage,
  };
}

export function updateBullets(
  bullets: BulletModel[],
  enemies: EnemyModel[],
  dt: number,
  onHit: HitCallback,
  camX: number = 0,
  camY: number = 0,
  camW: number = GAME_WIDTH,
  camH: number = GAME_HEIGHT,
): BulletModel[] {
  const remainingBullets: BulletModel[] = [];

  for (const bullet of bullets) {
    bullet.x += bullet.vx * dt;
    bullet.y += bullet.vy * dt;
    bullet.ttl -= dt;
    bullet.graphic.setPosition(bullet.x, bullet.y);

    let hitEnemy: EnemyModel | null = null;
    for (const enemy of enemies) {
      const dx = enemy.x - bullet.x;
      const dy = enemy.y - bullet.y;
      const hitRadius = enemy.radius + BULLET.radius + 1;
      if (dx * dx + dy * dy <= hitRadius * hitRadius) {
        hitEnemy = enemy;
        break;
      }
    }

    if (hitEnemy) {
      hitEnemy.hp -= bullet.damage;
      bullet.graphic.destroy();
      onHit(hitEnemy.x, hitEnemy.y);
      continue;
    }

    const insideBounds =
      bullet.x >= camX - 80 &&
      bullet.x <= camX + camW + 80 &&
      bullet.y >= camY - 80 &&
      bullet.y <= camY + camH + 80;
    if (bullet.ttl > 0 && insideBounds) {
      remainingBullets.push(bullet);
    } else {
      bullet.graphic.destroy();
    }
  }

  return remainingBullets;
}

export function spawnRocket(
  scene: Phaser.Scene,
  playerX: number,
  playerY: number,
  targetX: number,
  targetY: number,
  damage: number,
  splashRadius: number,
): RocketModel {
  const dx = targetX - playerX;
  const dy = targetY - playerY;
  const distance = Math.max(0.001, Math.hypot(dx, dy));
  const trail = scene.add.graphics();
  const graphic = scene.add.circle(playerX, playerY, ROCKET.radius, 0xff9600, 1);
  graphic.setStrokeStyle(1, 0xffefbf, 0.9);

  return {
    graphic,
    trail,
    x: playerX,
    y: playerY,
    vx: (dx / distance) * ROCKET.speed,
    vy: (dy / distance) * ROCKET.speed,
    targetX,
    targetY,
    ttl: ROCKET.lifetime,
    damage,
    splashRadius,
  };
}

export function updateRockets(
  rockets: RocketModel[],
  enemies: EnemyModel[],
  dt: number,
  onHit: HitCallback,
  onExplodeVisual: (rocket: RocketModel) => void,
): RocketModel[] {
  const remaining: RocketModel[] = [];

  for (const rocket of rockets) {
    const prevX = rocket.x;
    const prevY = rocket.y;
    rocket.x += rocket.vx * dt;
    rocket.y += rocket.vy * dt;
    rocket.ttl -= dt;
    rocket.graphic.setPosition(rocket.x, rocket.y);
    rocket.trail.clear();
    rocket.trail.lineStyle(3, 0xff9600, 0.8);
    rocket.trail.lineBetween(prevX, prevY, rocket.x, rocket.y);

    let exploded = false;
    for (const enemy of enemies) {
      const dx = enemy.x - rocket.x;
      const dy = enemy.y - rocket.y;
      if (dx * dx + dy * dy <= (enemy.radius + ROCKET.radius) ** 2) {
        exploded = true;
        break;
      }
    }

    const tx = rocket.targetX - rocket.x;
    const ty = rocket.targetY - rocket.y;
    if (!exploded && tx * tx + ty * ty <= 16 ** 2) {
      exploded = true;
    }

    if (!exploded && rocket.ttl > 0) {
      remaining.push(rocket);
      continue;
    }

    rocket.graphic.destroy();
    rocket.trail.destroy();
    for (const enemy of enemies) {
      const dx = enemy.x - rocket.x;
      const dy = enemy.y - rocket.y;
      const splashHitRadius = rocket.splashRadius + enemy.radius;
      if (dx * dx + dy * dy <= splashHitRadius * splashHitRadius) {
        enemy.hp -= rocket.damage;
        onHit(enemy.x, enemy.y);
      }
    }
    onExplodeVisual(rocket);
  }

  return remaining;
}

export function fireRailGun(
  scene: Phaser.Scene,
  playerX: number,
  playerY: number,
  headingX: number,
  headingY: number,
  damage: number,
  enemies: EnemyModel[],
  onHit: HitCallback,
): RailGunShotModel {
  const length = Math.max(GAME_WIDTH, GAME_HEIGHT) * 1.25;
  const directionLength = Math.max(0.001, Math.hypot(headingX, headingY));
  const nx = headingX / directionLength;
  const ny = headingY / directionLength;
  const endX = playerX + nx * length;
  const endY = playerY + ny * length;

  for (const enemy of enemies) {
    if (
      distanceToSegmentSquared(enemy.x, enemy.y, playerX, playerY, endX, endY) <=
      (enemy.radius + RAIL_GUN.width) ** 2
    ) {
      enemy.hp -= damage;
      onHit(enemy.x, enemy.y);
    }
  }

  const graphic = scene.add.line(0, 0, playerX, playerY, endX, endY, COLORS.neonCyan, 0.85);
  graphic.setOrigin(0, 0);
  graphic.setLineWidth(RAIL_GUN.width, RAIL_GUN.width);

  return { graphic, ttl: RAIL_GUN.lifetime };
}

export function updateRailGunShots(shots: RailGunShotModel[], dt: number): RailGunShotModel[] {
  const remaining: RailGunShotModel[] = [];
  for (const shot of shots) {
    shot.ttl -= dt;
    if (shot.ttl > 0) {
      shot.graphic.setAlpha(shot.ttl / RAIL_GUN.lifetime);
      remaining.push(shot);
    } else {
      shot.graphic.destroy();
    }
  }
  return remaining;
}

export function fireEmpPulse(
  scene: Phaser.Scene,
  playerX: number,
  playerY: number,
  radius: number,
  damage: number,
  enemies: EnemyModel[],
  onHit: HitCallback,
): EmpPulseModel {
  const graphic = scene.add.circle(playerX, playerY, radius, COLORS.neonMagenta, 0.08);
  graphic.setStrokeStyle(3, COLORS.neonMagenta, 0.7);

  for (const enemy of enemies) {
    const dx = enemy.x - playerX;
    const dy = enemy.y - playerY;
    if (dx * dx + dy * dy <= radius ** 2) {
      enemy.hp -= damage;
      onHit(enemy.x, enemy.y);
    }
  }

  return { graphic, ttl: EMP.pulseLifetime };
}

export function updateEmpPulses(pulses: EmpPulseModel[], dt: number): EmpPulseModel[] {
  const remaining: EmpPulseModel[] = [];
  for (const pulse of pulses) {
    pulse.ttl -= dt;
    if (pulse.ttl > 0) {
      pulse.graphic.setAlpha(0.7 * (pulse.ttl / EMP.pulseLifetime));
      remaining.push(pulse);
    } else {
      pulse.graphic.destroy();
    }
  }
  return remaining;
}

export function cleanupDeadEnemies(
  enemies: EnemyModel[],
  onEnemyDeath: EnemyDeathCallback,
): EnemyModel[] {
  const survivors: EnemyModel[] = [];
  for (const enemy of enemies) {
    if (enemy.hp > 0) {
      survivors.push(enemy);
      continue;
    }
    enemy.graphic.destroy();
    onEnemyDeath(enemy);
  }
  return survivors;
}
