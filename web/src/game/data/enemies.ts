export const ENEMY_SIDE_SEQUENCE = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] as const;

export type EnemySide = (typeof ENEMY_SIDE_SEQUENCE)[number];
export type EnemyProfileKey = EnemySide | "boss";

export const ENEMY_SCALING: Record<
  EnemyProfileKey,
  { speed: number; hp: number; damage: number; xp: number; radius: number }
> = {
  1: { speed: 1.28, hp: 0.7, damage: 0.8, xp: 0.7, radius: 0.9 },
  3: { speed: 1.12, hp: 0.9, damage: 0.9, xp: 0.95, radius: 1.0 },
  4: { speed: 0.98, hp: 1.15, damage: 1.1, xp: 1.15, radius: 1.05 },
  5: { speed: 0.88, hp: 1.45, damage: 1.3, xp: 1.45, radius: 1.15 },
  6: { speed: 0.8, hp: 1.8, damage: 1.55, xp: 1.75, radius: 1.25 },
  7: { speed: 0.74, hp: 2.05, damage: 1.7, xp: 2.05, radius: 1.32 },
  8: { speed: 0.7, hp: 2.3, damage: 1.9, xp: 2.3, radius: 1.4 },
  9: { speed: 0.67, hp: 2.6, damage: 2.05, xp: 2.55, radius: 1.48 },
  10: { speed: 0.64, hp: 2.9, damage: 2.2, xp: 2.85, radius: 1.56 },
  11: { speed: 0.61, hp: 3.2, damage: 2.35, xp: 3.15, radius: 1.64 },
  12: { speed: 0.58, hp: 3.55, damage: 2.5, xp: 3.45, radius: 1.72 },
  13: { speed: 0.55, hp: 3.9, damage: 2.7, xp: 3.8, radius: 1.8 },
  14: { speed: 0.52, hp: 4.3, damage: 2.9, xp: 4.15, radius: 1.88 },
  boss: { speed: 0.48, hp: 5.8, damage: 3.35, xp: 5.25, radius: 2.15 },
};

export function shouldSpawnBoss(minutes: number): boolean {
  if (minutes < 6) {
    return false;
  }

  return Math.random() < Math.min(0.12, 0.02 + (minutes - 6) * 0.01);
}

export function getBossSides(minutes: number): EnemySide {
  return getUnlockedEnemySides(minutes)[getUnlockedEnemySides(minutes).length - 1];
}

export function chooseEnemySides(minutes: number): EnemySide {
  const unlockedSides = getUnlockedEnemySides(minutes);
  const newestIndex = unlockedSides.length - 1;
  const weights = unlockedSides.map((sides, index) => {
    const distanceFromNewest = newestIndex - index;
    return [sides, 1 / (1 + distanceFromNewest * 0.55)] as [EnemySide, number];
  });

  return weightedChoice(weights) as EnemySide;
}

function getUnlockedEnemySides(minutes: number): readonly EnemySide[] {
  const unlockedCount = Math.max(
    1,
    Math.min(ENEMY_SIDE_SEQUENCE.length, Math.floor(minutes) + 1),
  );
  return ENEMY_SIDE_SEQUENCE.slice(0, unlockedCount);
}

function weightedChoice(weights: Array<[number, number]>): number {
  let roll = Math.random() * weights.reduce((sum, [, weight]) => sum + weight, 0);
  for (const [value, weight] of weights) {
    roll -= weight;
    if (roll <= 0) {
      return value;
    }
  }
  return weights[weights.length - 1][0];
}
