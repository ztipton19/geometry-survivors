export type EnemyProfileKey = 1 | 3 | 4 | 5 | 6 | 7 | 8 | "boss";

export const ENEMY_WEIGHTS: Array<[number, Array<[number, number]>]> = [
  [2.0, [[1, 1.0]]],
  [5.0, [[1, 0.45], [3, 0.35], [4, 0.2]]],
  [8.0, [[1, 0.3], [3, 0.35], [4, 0.25], [5, 0.1]]],
  [11.0, [[1, 0.2], [3, 0.3], [4, 0.25], [5, 0.15], [6, 0.1]]],
  [60.0, [[1, 0.15], [3, 0.25], [4, 0.25], [5, 0.18], [6, 0.12], [7, 0.03], [8, 0.02]]],
];

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
  boss: { speed: 0.68, hp: 2.9, damage: 2.4, xp: 3.0, radius: 1.6 },
};

export function shouldSpawnBoss(minutes: number): boolean {
  if (minutes < 6) {
    return false;
  }

  return Math.random() < Math.min(0.12, 0.02 + (minutes - 6) * 0.01);
}

export function chooseEnemySides(minutes: number): number {
  for (const [maxMinutes, weights] of ENEMY_WEIGHTS) {
    if (minutes <= maxMinutes) {
      return weightedChoice(weights);
    }
  }

  return weightedChoice(ENEMY_WEIGHTS[ENEMY_WEIGHTS.length - 1][1]);
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
