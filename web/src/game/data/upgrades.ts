import { COLORS, PLAYER } from "../constants/settings";

export type UpgradeId =
  | "minigun"
  | "rockets"
  | "laser"
  | "emp"
  | "health"
  | "shield"
  | "tractor"
  | "speed";

export type UpgradeState = {
  level: number;
  maxLevel: number;
};

export type UpgradeRuntime = {
  fireCooldown: number;
  bulletDamage: number;
  rocketsLevel: number;
  rocketDamage: number;
  rocketSplashRadius: number;
  rocketCooldown: number;
  laserLevel: number;
  laserDamage: number;
  laserCooldown: number;
  empLevel: number;
  empDamage: number;
  empRadius: number;
  playerHp: number;
  playerMaxHp: number;
  healthLevel: number;
  shieldLevel: number;
  shieldHp: number;
  shieldMax: number;
  shieldRegenRate: number;
  shieldRegenDelayMax: number;
  tractorRange: number;
  tractorLevel: number;
  maxSpeed: number;
  speedLevel: number;
  minigunLevel: number;
};

export type UpgradeDefinition<TScene extends UpgradeRuntime> = {
  id: UpgradeId;
  name: string;
  category: string;
  maxLevel: number;
  nextDescription: (scene: TScene, nextLevel: number) => string;
  currentDescription: (scene: TScene) => string;
  apply: (scene: TScene, nextLevel: number) => void;
};

export const CARD_COLORS = [COLORS.neonCyan, COLORS.neonMagenta, COLORS.neonGreen];

const MINIGUN_LEVELS = [
  { fireCooldown: 0.4, bulletDamage: 10 },
  { fireCooldown: 0.35, bulletDamage: 12 },
  { fireCooldown: 0.3, bulletDamage: 14 },
  { fireCooldown: 0.26, bulletDamage: 16 },
  { fireCooldown: 0.22, bulletDamage: 18 },
  { fireCooldown: 0.18, bulletDamage: 20 },
];
const ROCKET_LEVELS = [
  { damage: 30, splashRadius: 40, fireCooldown: 3.0 },
  { damage: 35, splashRadius: 45, fireCooldown: 2.8 },
  { damage: 40, splashRadius: 50, fireCooldown: 2.6 },
  { damage: 45, splashRadius: 55, fireCooldown: 2.4 },
  { damage: 50, splashRadius: 60, fireCooldown: 2.2 },
  { damage: 55, splashRadius: 65, fireCooldown: 2.0 },
];
const LASER_LEVELS = [
  { damage: 15, fireCooldown: 5.0 },
  { damage: 20, fireCooldown: 4.5 },
  { damage: 25, fireCooldown: 4.0 },
  { damage: 30, fireCooldown: 3.5 },
  { damage: 35, fireCooldown: 3.0 },
  { damage: 40, fireCooldown: 2.5 },
];
const EMP_LEVELS = [
  { damage: 5, radius: 100 },
  { damage: 7, radius: 120 },
  { damage: 10, radius: 140 },
  { damage: 15, radius: 160 },
  { damage: 20, radius: 180 },
  { damage: 25, radius: 200 },
];
const SHIELD_LEVELS = [
  { shieldMax: 50, regenRate: 5.0, regenDelay: 3.0 },
  { shieldMax: 62, regenRate: 6.0, regenDelay: 2.8 },
  { shieldMax: 75, regenRate: 7.0, regenDelay: 2.6 },
  { shieldMax: 87, regenRate: 8.0, regenDelay: 2.4 },
  { shieldMax: 100, regenRate: 9.0, regenDelay: 2.2 },
  { shieldMax: 112, regenRate: 10.0, regenDelay: 2.0 },
];
const TRACTOR_LEVELS = [0, 50, 100, 150, 200, 250];
const SPEED_LEVELS = [220, 245, 270, 295, 320, 345];
const HEALTH_BONUS_PER_LEVEL = 25;

export const UPGRADE_DEFINITIONS: Record<UpgradeId, UpgradeDefinition<UpgradeRuntime>> = {
  minigun: {
    id: "minigun",
    name: "Minigun Upgrade",
    category: "WEAPON",
    maxLevel: 5,
    currentDescription: (scene) =>
      `${scene.fireCooldown.toFixed(2)}s cadence, ${Math.round(scene.bulletDamage)} damage`,
    nextDescription: (_scene, nextLevel) => {
      const stats = MINIGUN_LEVELS[nextLevel];
      return `${stats.fireCooldown.toFixed(2)}s cadence, ${stats.bulletDamage} damage`;
    },
    apply: (scene, nextLevel) => {
      const stats = MINIGUN_LEVELS[nextLevel];
      scene.minigunLevel = nextLevel;
      scene.fireCooldown = stats.fireCooldown;
      scene.bulletDamage = stats.bulletDamage;
    },
  },
  rockets: {
    id: "rockets",
    name: "Rockets",
    category: "WEAPON",
    maxLevel: 5,
    currentDescription: (scene) =>
      scene.rocketsLevel < 0
        ? "Unlock mouse-fired splash rockets"
        : `${Math.round(scene.rocketDamage)} damage, ${Math.round(scene.rocketSplashRadius)}px splash, ${scene.rocketCooldown.toFixed(1)}s`,
    nextDescription: (_scene, nextLevel) => {
      const stats = ROCKET_LEVELS[nextLevel];
      return `${stats.damage} damage, ${stats.splashRadius}px splash, ${stats.fireCooldown.toFixed(1)}s`;
    },
    apply: (scene, nextLevel) => {
      const stats = ROCKET_LEVELS[nextLevel];
      scene.rocketsLevel = nextLevel;
      scene.rocketDamage = stats.damage;
      scene.rocketSplashRadius = stats.splashRadius;
      scene.rocketCooldown = stats.fireCooldown;
    },
  },
  laser: {
    id: "laser",
    name: "Laser",
    category: "WEAPON",
    maxLevel: 5,
    currentDescription: (scene) =>
      scene.laserLevel < 0
        ? "Unlock a piercing beam"
        : `${Math.round(scene.laserDamage)} damage, ${scene.laserCooldown.toFixed(1)}s cooldown`,
    nextDescription: (_scene, nextLevel) => {
      const stats = LASER_LEVELS[nextLevel];
      return `${stats.damage} damage, ${stats.fireCooldown.toFixed(1)}s cooldown`;
    },
    apply: (scene, nextLevel) => {
      const stats = LASER_LEVELS[nextLevel];
      scene.laserLevel = nextLevel;
      scene.laserDamage = stats.damage;
      scene.laserCooldown = stats.fireCooldown;
    },
  },
  emp: {
    id: "emp",
    name: "EMP Field",
    category: "WEAPON",
    maxLevel: 5,
    currentDescription: (scene) =>
      scene.empLevel < 0
        ? "Unlock a pulse field"
        : `${Math.round(scene.empDamage)} damage, ${Math.round(scene.empRadius)}px radius`,
    nextDescription: (_scene, nextLevel) => {
      const stats = EMP_LEVELS[nextLevel];
      return `${stats.damage} damage, ${stats.radius}px radius`;
    },
    apply: (scene, nextLevel) => {
      const stats = EMP_LEVELS[nextLevel];
      scene.empLevel = nextLevel;
      scene.empDamage = stats.damage;
      scene.empRadius = stats.radius;
    },
  },
  health: {
    id: "health",
    name: "Health Boost",
    category: "SURVIVAL",
    maxLevel: 5,
    currentDescription: (scene) =>
      `${Math.round(scene.playerHp)} / ${Math.round(scene.playerMaxHp)} HP`,
    nextDescription: () => `+${HEALTH_BONUS_PER_LEVEL} max HP, immediate repair`,
    apply: (scene, nextLevel) => {
      scene.healthLevel = nextLevel;
      scene.playerMaxHp = PLAYER.maxHp + nextLevel * HEALTH_BONUS_PER_LEVEL;
      scene.playerHp = Math.min(scene.playerMaxHp, scene.playerHp + HEALTH_BONUS_PER_LEVEL);
    },
  },
  shield: {
    id: "shield",
    name: "Shield System",
    category: "SURVIVAL",
    maxLevel: 5,
    currentDescription: (scene) =>
      scene.shieldLevel < 0
        ? "Unlock shield protection"
        : `${Math.round(scene.shieldHp)} / ${Math.round(scene.shieldMax)} shield`,
    nextDescription: (_scene, nextLevel) => {
      const stats = SHIELD_LEVELS[nextLevel];
      return `${Math.round(stats.shieldMax)} shield, ${stats.regenRate.toFixed(0)}/s regen`;
    },
    apply: (scene, nextLevel) => {
      const stats = SHIELD_LEVELS[nextLevel];
      scene.shieldLevel = nextLevel;
      scene.shieldMax = stats.shieldMax;
      scene.shieldRegenRate = stats.regenRate;
      scene.shieldRegenDelayMax = stats.regenDelay;
      scene.shieldHp =
        nextLevel === 0 ? stats.shieldMax : Math.min(stats.shieldMax, scene.shieldHp + 15);
    },
  },
  tractor: {
    id: "tractor",
    name: "Tractor Beam",
    category: "UTILITY",
    maxLevel: 5,
    currentDescription: (scene) => `${Math.round(scene.tractorRange)}px pickup radius`,
    nextDescription: (_scene, nextLevel) => `${TRACTOR_LEVELS[nextLevel]}px pickup radius`,
    apply: (scene, nextLevel) => {
      scene.tractorLevel = nextLevel;
      scene.tractorRange = TRACTOR_LEVELS[nextLevel];
    },
  },
  speed: {
    id: "speed",
    name: "Thruster Tuning",
    category: "UTILITY",
    maxLevel: 5,
    currentDescription: (scene) => `${Math.round(scene.maxSpeed)} max speed`,
    nextDescription: (_scene, nextLevel) => `${SPEED_LEVELS[nextLevel]} max speed`,
    apply: (scene, nextLevel) => {
      scene.speedLevel = nextLevel;
      scene.maxSpeed = SPEED_LEVELS[nextLevel];
    },
  },
};
