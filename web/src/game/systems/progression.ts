import { PLAYER } from "../constants/settings";
import { UPGRADE_DEFINITIONS, type UpgradeId, type UpgradeRuntime, type UpgradeState } from "../data/upgrades";

export type ProgressionRuntime = UpgradeRuntime & {
  playerLevel: number;
  playerXp: number;
  xpToNext: number;
  enemiesKilled: number;
};

export function resetProgression(runtime: ProgressionRuntime): void {
  runtime.playerHp = PLAYER.maxHp;
  runtime.playerMaxHp = PLAYER.maxHp;
  runtime.playerLevel = 1;
  runtime.playerXp = 0;
  runtime.xpToNext = PLAYER.xpBase;
  runtime.enemiesKilled = 0;

  runtime.minigunLevel = 0;
  runtime.rocketsLevel = -1;
  runtime.laserLevel = -1;
  runtime.empLevel = -1;
  runtime.healthLevel = 0;
  runtime.shieldLevel = -1;
  runtime.tractorLevel = 0;
  runtime.speedLevel = 0;

  runtime.fireCooldown = PLAYER.fireCooldown;
  runtime.bulletDamage = PLAYER.bulletDamage;
  runtime.rocketDamage = 0;
  runtime.rocketSplashRadius = 0;
  runtime.rocketCooldown = 999;
  runtime.laserDamage = 0;
  runtime.laserCooldown = 999;
  runtime.empDamage = 0;
  runtime.empRadius = 0;
  runtime.maxSpeed = PLAYER.maxSpeed;
  runtime.tractorRange = PLAYER.tractorRange;
  runtime.shieldHp = 0;
  runtime.shieldMax = 0;
  runtime.shieldRegenRate = 0;
  runtime.shieldRegenDelay = 0;
  runtime.shieldRegenDelayMax = 0;
}

export function awardXp(runtime: ProgressionRuntime, amount: number): boolean {
  runtime.playerXp += amount;
  let leveled = false;

  while (runtime.playerXp >= runtime.xpToNext) {
    runtime.playerXp -= runtime.xpToNext;
    runtime.playerLevel += 1;
    runtime.xpToNext = Math.round(
      PLAYER.xpBase * PLAYER.xpGrowth ** (runtime.playerLevel - 1) +
        PLAYER.xpLinearBonus * (runtime.playerLevel - 1),
    );
    leveled = true;
  }

  return leveled;
}

export function getUpgradeState(runtime: ProgressionRuntime, id: UpgradeId): UpgradeState {
  switch (id) {
    case "minigun":
      return { level: runtime.minigunLevel, maxLevel: UPGRADE_DEFINITIONS.minigun.maxLevel };
    case "rockets":
      return { level: runtime.rocketsLevel, maxLevel: UPGRADE_DEFINITIONS.rockets.maxLevel };
    case "laser":
      return { level: runtime.laserLevel, maxLevel: UPGRADE_DEFINITIONS.laser.maxLevel };
    case "emp":
      return { level: runtime.empLevel, maxLevel: UPGRADE_DEFINITIONS.emp.maxLevel };
    case "health":
      return { level: runtime.healthLevel, maxLevel: UPGRADE_DEFINITIONS.health.maxLevel };
    case "shield":
      return { level: runtime.shieldLevel, maxLevel: UPGRADE_DEFINITIONS.shield.maxLevel };
    case "tractor":
      return { level: runtime.tractorLevel, maxLevel: UPGRADE_DEFINITIONS.tractor.maxLevel };
    case "speed":
      return { level: runtime.speedLevel, maxLevel: UPGRADE_DEFINITIONS.speed.maxLevel };
  }
}

export function generateUpgradeOptions(runtime: ProgressionRuntime): UpgradeId[] {
  const allOptions = (Object.keys(UPGRADE_DEFINITIONS) as UpgradeId[]).filter((id) => {
    const state = getUpgradeState(runtime, id);
    return state.level < state.maxLevel;
  });

  for (let i = allOptions.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [allOptions[i], allOptions[j]] = [allOptions[j], allOptions[i]];
  }

  return allOptions.slice(0, Math.min(3, allOptions.length));
}

export function applyPlayerDamage(runtime: ProgressionRuntime, amount: number): void {
  if (runtime.shieldLevel >= 0 && runtime.shieldHp > 0) {
    if (runtime.shieldHp >= amount) {
      runtime.shieldHp -= amount;
    } else {
      const remaining = amount - runtime.shieldHp;
      runtime.shieldHp = 0;
      runtime.playerHp = Math.max(0, runtime.playerHp - remaining);
    }
    runtime.shieldRegenDelay = runtime.shieldRegenDelayMax;
    return;
  }

  runtime.playerHp = Math.max(0, runtime.playerHp - amount);
}

export function updateShield(runtime: ProgressionRuntime, dt: number): number {
  if (runtime.shieldLevel < 0) {
    return 0;
  }

  const ratio = runtime.shieldMax > 0 ? runtime.shieldHp / runtime.shieldMax : 0;
  if (runtime.shieldHp < runtime.shieldMax) {
    if (runtime.shieldRegenDelay > 0) {
      runtime.shieldRegenDelay = Math.max(0, runtime.shieldRegenDelay - dt);
    } else {
      runtime.shieldHp = Math.min(runtime.shieldMax, runtime.shieldHp + runtime.shieldRegenRate * dt);
    }
  }

  return ratio > 0 ? 0.2 + ratio * 0.55 : 0;
}

export function buildStatusText(runtime: ProgressionRuntime): string {
  return [
    `Minigun L${runtime.minigunLevel + 1}`,
    runtime.rocketsLevel >= 0 ? `Rockets L${runtime.rocketsLevel + 1}` : "Rockets locked",
    runtime.laserLevel >= 0 ? `Laser L${runtime.laserLevel + 1}` : "Laser locked",
    runtime.empLevel >= 0 ? `EMP L${runtime.empLevel + 1}` : "EMP locked",
    runtime.shieldLevel >= 0
      ? `Shield ${Math.ceil(runtime.shieldHp)}/${Math.ceil(runtime.shieldMax)}`
      : "Shield offline",
  ].join("\n");
}
