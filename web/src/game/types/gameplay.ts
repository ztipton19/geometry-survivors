import Phaser from "phaser";

export type EnemyModel = {
  graphic: Phaser.GameObjects.Shape;
  x: number;
  y: number;
  hp: number;
  speed: number;
  damage: number;
  xpValue: number;
  radius: number;
  isBoss: boolean;
  touchCooldown: number;
};

export type BulletModel = {
  graphic: Phaser.GameObjects.Arc;
  x: number;
  y: number;
  vx: number;
  vy: number;
  ttl: number;
  damage: number;
};

export type RocketModel = {
  graphic: Phaser.GameObjects.Arc;
  trail: Phaser.GameObjects.Graphics;
  x: number;
  y: number;
  vx: number;
  vy: number;
  targetX: number;
  targetY: number;
  ttl: number;
  damage: number;
  splashRadius: number;
};

export type LaserModel = {
  graphic: Phaser.GameObjects.Line;
  ttl: number;
};

export type EmpPulseModel = {
  graphic: Phaser.GameObjects.Arc;
  ttl: number;
};

export type XpGemModel = {
  graphic: Phaser.GameObjects.Arc;
  x: number;
  y: number;
  value: number;
  kind: "normal" | "overflow";
};
