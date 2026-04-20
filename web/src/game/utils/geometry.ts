import Phaser from "phaser";

export function regularPolygonPoints(sides: number, radius: number): number[] {
  const points: number[] = [];
  for (let i = 0; i < sides; i += 1) {
    const angle = -Math.PI / 2 + (Math.PI * 2 * i) / sides;
    points.push(Math.cos(angle) * radius, Math.sin(angle) * radius);
  }
  return points;
}

export function distanceToSegmentSquared(
  px: number,
  py: number,
  ax: number,
  ay: number,
  bx: number,
  by: number,
): number {
  const abx = bx - ax;
  const aby = by - ay;
  const apx = px - ax;
  const apy = py - ay;
  const abLenSq = abx * abx + aby * aby;
  if (abLenSq === 0) {
    const dx = px - ax;
    const dy = py - ay;
    return dx * dx + dy * dy;
  }

  const t = Phaser.Math.Clamp((apx * abx + apy * aby) / abLenSq, 0, 1);
  const closestX = ax + abx * t;
  const closestY = ay + aby * t;
  const dx = px - closestX;
  const dy = py - closestY;
  return dx * dx + dy * dy;
}
