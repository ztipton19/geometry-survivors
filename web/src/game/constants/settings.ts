export const GAME_WIDTH = 1100;
export const GAME_HEIGHT = 700;
export const ROUND_SECONDS = 15 * 60;

export const COLORS = {
  background: 0x05070a,
  neonCyan: 0x00ffff,
  neonYellow: 0xffff00,
  neonMagenta: 0xff00ff,
  neonGreen: 0x00ff78,
  white: 0xf0f0f0,
  enemyRed: 0xff3c3c,
  grid: 0x10324a,
} as const;

export const PLAYER = {
  radius: 12,
  thrust: 540,
  reverseThrust: 320,
  turnSpeed: 2.8,
  damping: 0.992,
  maxSpeed: 320,
  maxHp: 100,
  fireCooldown: 0.4,
  bulletDamage: 10,
  xpBase: 90,
  xpGrowth: 1.22,
  xpLinearBonus: 12,
  tractorRange: 0,
} as const;

export const BULLET = {
  speed: 900,
  radius: 3,
  lifetime: 1.2,
  spread: 0.08,
} as const;

export const ROCKET = {
  speed: 520,
  radius: 6,
  lifetime: 2.2,
} as const;

export const RAIL_GUN = {
  lifetime: 0.12,
  width: 6,
} as const;

export const EMP = {
  pulseInterval: 0.5,
  pulseLifetime: 0.25,
} as const;

export const ENEMY = {
  baseSpeed: 10.5,
  baseHp: 22,
  baseDamage: 22,
  baseXp: 7,
  xpPerHp: 0.32,
  radius: 12,
  spawnIntervalStart: 0.75,
  spawnIntervalMin: 0.18,
  spawnIntervalDecay: 0.0028,
  contactDamageCooldown: 0.45,
  contactDamageRate: 18,
} as const;

export const XP_GEM = {
  maxLooseGems: 400,
  magnetSpeed: 600,
  pickupRadius: 20,
  normalRadius: 6,
  overflowRadius: 10,
  overflowMergeRadius: 850,
  overflowSpawnMinRadius: 300,
  overflowSpawnMaxRadius: 650,
} as const;
