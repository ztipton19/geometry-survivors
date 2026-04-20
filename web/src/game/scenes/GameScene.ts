import Phaser from "phaser";

import {
  BULLET,
  EMP,
  ENEMY,
  GAME_HEIGHT,
  GAME_WIDTH,
  LASER,
  PLAYER,
  ROCKET,
  ROUND_SECONDS,
  XP_GEM,
  COLORS,
} from "../constants/settings";
import {
  chooseEnemySides,
  ENEMY_SCALING,
  type EnemyProfileKey,
  shouldSpawnBoss,
} from "../data/enemies";
import {
  CARD_COLORS,
  UPGRADE_DEFINITIONS,
  type UpgradeId,
  type UpgradeRuntime,
  type UpgradeState,
} from "../data/upgrades";
import {
  createHud,
  createOverlay,
  type Hud,
  type Overlay,
  showEndOverlay,
  showLevelUpOverlay,
  showMenuOverlay,
} from "../ui/gameUi";
import { distanceToSegmentSquared, regularPolygonPoints } from "../utils/geometry";

type GameMode = "menu" | "play" | "levelup" | "win" | "lose";

type EnemyModel = {
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

type BulletModel = {
  graphic: Phaser.GameObjects.Arc;
  x: number;
  y: number;
  vx: number;
  vy: number;
  ttl: number;
  damage: number;
};

type RocketModel = {
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

type LaserModel = {
  graphic: Phaser.GameObjects.Line;
  ttl: number;
};

type EmpPulseModel = {
  graphic: Phaser.GameObjects.Arc;
  ttl: number;
};

type XpGemModel = {
  graphic: Phaser.GameObjects.Arc;
  x: number;
  y: number;
  value: number;
  lifetime: number;
};

export class GameScene extends Phaser.Scene implements UpgradeRuntime {
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private wasd!: Record<"W" | "A" | "S" | "D", Phaser.Input.Keyboard.Key>;
  private actionKeys!: Record<
    "ENTER" | "SPACE" | "R" | "ONE" | "TWO" | "THREE",
    Phaser.Input.Keyboard.Key
  >;

  private player!: Phaser.GameObjects.Container;
  private shieldRing!: Phaser.GameObjects.Arc;
  private hud!: Hud;
  private overlay!: Overlay;
  private mode: GameMode = "menu";
  private velocity = new Phaser.Math.Vector2();

  private enemies: EnemyModel[] = [];
  private bullets: BulletModel[] = [];
  private rockets: RocketModel[] = [];
  private lasers: LaserModel[] = [];
  private empPulses: EmpPulseModel[] = [];
  private xpGems: XpGemModel[] = [];
  private upgradeOptions: UpgradeId[] = [];

  private elapsed = 0;
  private remaining = ROUND_SECONDS;
  private spawnTimer = 0;
  private fireTimer = 0;
  private rocketTimer = 0;
  private laserTimer = 0;
  private empTimer = 0;

  public playerHp: number = PLAYER.maxHp;
  public playerMaxHp: number = PLAYER.maxHp;
  private playerLevel = 1;
  private playerXp = 0;
  private xpToNext: number = PLAYER.xpBase;
  private enemiesKilled = 0;

  public fireCooldown: number = PLAYER.fireCooldown;
  public bulletDamage: number = PLAYER.bulletDamage;
  public rocketDamage = 0;
  public rocketSplashRadius = 0;
  public rocketCooldown = 999;
  public laserDamage = 0;
  public laserCooldown = 999;
  public empDamage = 0;
  public empRadius = 0;
  public maxSpeed: number = PLAYER.maxSpeed;
  public tractorRange: number = PLAYER.tractorRange;
  public shieldHp = 0;
  public shieldMax = 0;
  public shieldRegenRate = 0;
  public shieldRegenDelay = 0;
  public shieldRegenDelayMax = 0;

  public minigunLevel = 0;
  public rocketsLevel = -1;
  public laserLevel = -1;
  public empLevel = -1;
  public healthLevel = 0;
  public shieldLevel = -1;
  public tractorLevel = 0;
  public speedLevel = 0;

  private readonly playerPosition = new Phaser.Math.Vector2(GAME_WIDTH / 2, GAME_HEIGHT / 2);

  constructor() {
    super("game");
  }

  create(): void {
    this.drawBackdrop();
    this.hud = createHud(this);
    this.createPlayer();
    this.overlay = createOverlay(this);

    this.cursors = this.input.keyboard!.createCursorKeys();
    this.wasd = this.input.keyboard!.addKeys("W,A,S,D") as Record<
      "W" | "A" | "S" | "D",
      Phaser.Input.Keyboard.Key
    >;
    this.actionKeys = this.input.keyboard!.addKeys(
      "ENTER,SPACE,R,ONE,TWO,THREE",
    ) as Record<"ENTER" | "SPACE" | "R" | "ONE" | "TWO" | "THREE", Phaser.Input.Keyboard.Key>;

    this.input.on("pointerdown", (pointer: Phaser.Input.Pointer) => {
      if (this.mode !== "levelup") {
        return;
      }
      for (let i = 0; i < this.upgradeOptions.length; i += 1) {
        const card = this.overlay.cards[i];
        if (card.bounds.contains(pointer.x, pointer.y)) {
          this.selectUpgrade(i);
          return;
        }
      }
    });

    showMenuOverlay(this.overlay);
    this.updateHud();
  }

  update(_: number, deltaMs: number): void {
    this.handleModeInput();
    if (this.mode !== "play") {
      return;
    }

    const dt = deltaMs / 1000;
    this.elapsed += dt;
    this.remaining = Math.max(0, ROUND_SECONDS - this.elapsed);

    this.updateMovement(dt);
    this.updateSpawning(dt);
    this.updateEnemies(dt);
    this.updateAutoFire(dt);
    this.updateBullets(dt);
    this.updateRockets(dt);
    this.updateLasers(dt);
    this.updateEmp(dt);
    this.updateXpGems(dt);
    this.updateShield(dt);

    if (this.playerHp <= 0) {
      this.playerHp = 0;
      this.mode = "lose";
      showEndOverlay(this.overlay, "SYSTEM FAILURE", "Press R or Enter to restart", false);
    } else if (this.remaining <= 0) {
      this.mode = "win";
      showEndOverlay(this.overlay, "MISSION COMPLETE", "Press R or Enter to run again", true);
    }

    this.updateHud();
  }

  private handleModeInput(): void {
    if (
      (Phaser.Input.Keyboard.JustDown(this.actionKeys.ENTER) ||
        Phaser.Input.Keyboard.JustDown(this.actionKeys.SPACE)) &&
      this.mode === "menu"
    ) {
      this.startRun();
      return;
    }

    if (
      (Phaser.Input.Keyboard.JustDown(this.actionKeys.R) ||
        Phaser.Input.Keyboard.JustDown(this.actionKeys.ENTER)) &&
      (this.mode === "win" || this.mode === "lose")
    ) {
      this.startRun();
      return;
    }

    if (this.mode === "levelup") {
      if (Phaser.Input.Keyboard.JustDown(this.actionKeys.ONE)) {
        this.selectUpgrade(0);
      } else if (Phaser.Input.Keyboard.JustDown(this.actionKeys.TWO)) {
        this.selectUpgrade(1);
      } else if (Phaser.Input.Keyboard.JustDown(this.actionKeys.THREE)) {
        this.selectUpgrade(2);
      }
    }
  }

  private updateMovement(dt: number): void {
    const move = new Phaser.Math.Vector2(
      Number(this.cursors.right.isDown || this.wasd.D.isDown) -
        Number(this.cursors.left.isDown || this.wasd.A.isDown),
      Number(this.cursors.down.isDown || this.wasd.S.isDown) -
        Number(this.cursors.up.isDown || this.wasd.W.isDown),
    );

    if (move.lengthSq() > 0) {
      move.normalize();
      this.velocity.add(move.scale(PLAYER.thrust * dt));
    }

    this.velocity.scale(Math.pow(PLAYER.damping, dt * 60));
    this.velocity.limit(this.maxSpeed);
    this.playerPosition.add(this.velocity.clone().scale(dt));
    this.playerPosition.x = Phaser.Math.Clamp(
      this.playerPosition.x,
      PLAYER.radius * 2,
      GAME_WIDTH - PLAYER.radius * 2,
    );
    this.playerPosition.y = Phaser.Math.Clamp(
      this.playerPosition.y,
      PLAYER.radius * 2,
      GAME_HEIGHT - PLAYER.radius * 2,
    );

    const pointer = this.input.activePointer.positionToCamera(this.cameras.main) as Phaser.Math.Vector2;
    const angle = Phaser.Math.Angle.Between(
      this.playerPosition.x,
      this.playerPosition.y,
      pointer.x,
      pointer.y,
    );

    this.player.setPosition(this.playerPosition.x, this.playerPosition.y);
    this.player.rotation = angle + Math.PI / 2;
    this.shieldRing.setPosition(this.playerPosition.x, this.playerPosition.y);
  }

  private createPlayer(): void {
    const body = this.add.graphics();
    body.lineStyle(3, COLORS.neonYellow, 1);
    body.fillStyle(0x1c2740, 1);
    body.beginPath();
    body.moveTo(0, -18);
    body.lineTo(14, 16);
    body.lineTo(0, 8);
    body.lineTo(-14, 16);
    body.closePath();
    body.fillPath();
    body.strokePath();

    const glow = this.add.graphics();
    glow.lineStyle(2, COLORS.neonCyan, 0.45);
    glow.strokeCircle(0, 8, 16);

    this.player = this.add.container(this.playerPosition.x, this.playerPosition.y, [glow, body]);
    this.shieldRing = this.add.circle(this.playerPosition.x, this.playerPosition.y, 24);
    this.shieldRing.setStrokeStyle(3, 0x6fb3ff, 0);
    this.shieldRing.setFillStyle(0x6fb3ff, 0);
  }

  private drawBackdrop(): void {
    const backdrop = this.add.graphics();
    backdrop.fillGradientStyle(0x08121b, 0x08121b, COLORS.background, COLORS.background, 1);
    backdrop.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

    const grid = this.add.graphics();
    grid.lineStyle(1, COLORS.grid, 0.34);
    for (let x = 0; x <= GAME_WIDTH; x += 40) {
      grid.lineBetween(x, 0, x, GAME_HEIGHT);
    }
    for (let y = 0; y <= GAME_HEIGHT; y += 40) {
      grid.lineBetween(0, y, GAME_WIDTH, y);
    }

    const stars = this.add.graphics();
    stars.fillStyle(COLORS.white, 0.8);
    for (let i = 0; i < 120; i += 1) {
      stars.fillCircle(
        Phaser.Math.Between(0, GAME_WIDTH),
        Phaser.Math.Between(0, GAME_HEIGHT),
        Phaser.Math.FloatBetween(0.5, 1.6),
      );
    }
  }

  private startRun(): void {
    this.clearWorld();
    this.mode = "play";
    this.overlay.container.setVisible(false);
    this.elapsed = 0;
    this.remaining = ROUND_SECONDS;
    this.spawnTimer = 0;
    this.fireTimer = 0;
    this.rocketTimer = 0;
    this.laserTimer = 0;
    this.empTimer = 0;
    this.playerPosition.set(GAME_WIDTH / 2, GAME_HEIGHT / 2);
    this.player.setPosition(this.playerPosition.x, this.playerPosition.y);
    this.velocity.set(0, 0);

    this.playerHp = PLAYER.maxHp;
    this.playerMaxHp = PLAYER.maxHp;
    this.playerLevel = 1;
    this.playerXp = 0;
    this.xpToNext = PLAYER.xpBase;
    this.enemiesKilled = 0;

    this.minigunLevel = 0;
    this.rocketsLevel = -1;
    this.laserLevel = -1;
    this.empLevel = -1;
    this.healthLevel = 0;
    this.shieldLevel = -1;
    this.tractorLevel = 0;
    this.speedLevel = 0;

    this.fireCooldown = PLAYER.fireCooldown;
    this.bulletDamage = PLAYER.bulletDamage;
    this.rocketDamage = 0;
    this.rocketSplashRadius = 0;
    this.rocketCooldown = 999;
    this.laserDamage = 0;
    this.laserCooldown = 999;
    this.empDamage = 0;
    this.empRadius = 0;
    this.maxSpeed = PLAYER.maxSpeed;
    this.tractorRange = PLAYER.tractorRange;
    this.shieldHp = 0;
    this.shieldMax = 0;
    this.shieldRegenRate = 0;
    this.shieldRegenDelay = 0;
    this.shieldRegenDelayMax = 0;
    this.shieldRing.setStrokeStyle(3, 0x6fb3ff, 0);

    this.hud.prompt.setText("WASD / Arrows to move   Mouse to aim   Survive 15 minutes");
    this.updateHud();
  }

  private clearWorld(): void {
    for (const enemy of this.enemies) {
      enemy.graphic.destroy();
    }
    for (const bullet of this.bullets) {
      bullet.graphic.destroy();
    }
    for (const rocket of this.rockets) {
      rocket.graphic.destroy();
      rocket.trail.destroy();
    }
    for (const laser of this.lasers) {
      laser.graphic.destroy();
    }
    for (const pulse of this.empPulses) {
      pulse.graphic.destroy();
    }
    for (const gem of this.xpGems) {
      gem.graphic.destroy();
    }

    this.enemies = [];
    this.bullets = [];
    this.rockets = [];
    this.lasers = [];
    this.empPulses = [];
    this.xpGems = [];
    this.upgradeOptions = [];
  }

  private updateSpawning(dt: number): void {
    this.spawnTimer += dt;
    const spawnInterval = Math.max(
      ENEMY.spawnIntervalMin,
      ENEMY.spawnIntervalStart - this.elapsed * ENEMY.spawnIntervalDecay,
    );

    while (this.spawnTimer >= spawnInterval) {
      this.spawnTimer -= spawnInterval;
      this.enemies.push(this.spawnEnemy());
    }
  }

  private spawnEnemy(): EnemyModel {
    const viewRadius = Math.max(GAME_WIDTH, GAME_HEIGHT) * 0.65;
    const margin = 140;
    const distance = viewRadius + margin;
    const angle = Phaser.Math.FloatBetween(0, Math.PI * 2);
    const x = this.playerPosition.x + Math.cos(angle) * distance;
    const y = this.playerPosition.y + Math.sin(angle) * distance;

    const minutes = this.elapsed / 60;
    const isBoss = shouldSpawnBoss(minutes);
    const sides = isBoss ? 8 : chooseEnemySides(minutes);
    const scaling = ENEMY_SCALING[isBoss ? "boss" : (sides as EnemyProfileKey)];

    const baseSpeed =
      ENEMY.baseSpeed + Math.min(ENEMY.speedMaxBonus, this.elapsed * ENEMY.speedPerSecond);
    const baseHp = ENEMY.baseHp + Math.min(ENEMY.hpMaxBonus, this.elapsed * ENEMY.hpPerSecond);
    const baseDamage =
      ENEMY.baseDamage + Math.min(ENEMY.damageMaxBonus, this.elapsed * ENEMY.damagePerSecond);
    const radius = ENEMY.radius * scaling.radius;

    return {
      graphic: this.createEnemyGraphic(x, y, sides, radius, isBoss),
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

  private createEnemyGraphic(
    x: number,
    y: number,
    sides: number,
    radius: number,
    isBoss: boolean,
  ): Phaser.GameObjects.Shape {
    if (sides <= 1) {
      return this.add
        .circle(x, y, radius, isBoss ? 0xff834d : COLORS.enemyRed, 0.88)
        .setStrokeStyle(2, 0xffd2bf, isBoss ? 0.85 : 0.35);
    }

    return this.add
      .polygon(
        x,
        y,
        regularPolygonPoints(sides, radius),
        isBoss ? 0xff834d : COLORS.enemyRed,
        0.85,
      )
      .setStrokeStyle(2, isBoss ? 0xfff0cf : 0xff9898, isBoss ? 0.8 : 0.5);
  }

  private updateEnemies(dt: number): void {
    for (const enemy of this.enemies) {
      const dx = this.playerPosition.x - enemy.x;
      const dy = this.playerPosition.y - enemy.y;
      const distance = Math.max(0.001, Math.hypot(dx, dy));
      enemy.x += (dx / distance) * enemy.speed * dt * 12;
      enemy.y += (dy / distance) * enemy.speed * dt * 12;
      enemy.touchCooldown = Math.max(0, enemy.touchCooldown - dt);

      if (distance < enemy.radius + PLAYER.radius + 6 && enemy.touchCooldown <= 0) {
        enemy.touchCooldown = ENEMY.contactDamageCooldown;
        this.applyPlayerDamage(enemy.damage * 0.3);
        this.spawnHitFlash(this.playerPosition.x, this.playerPosition.y);
      }

      enemy.graphic.setPosition(enemy.x, enemy.y);
      enemy.graphic.rotation += dt * (enemy.isBoss ? 0.9 : 0.45);
    }
  }

  private updateAutoFire(dt: number): void {
    this.fireTimer += dt;
    const nearest = this.findNearestEnemy();
    while (nearest && this.fireTimer >= this.fireCooldown) {
      this.fireTimer -= this.fireCooldown;
      this.spawnBullet(nearest);
    }
  }

  private findNearestEnemy(): EnemyModel | null {
    let best: EnemyModel | null = null;
    let bestDistanceSquared = Number.POSITIVE_INFINITY;
    for (const enemy of this.enemies) {
      const dx = enemy.x - this.playerPosition.x;
      const dy = enemy.y - this.playerPosition.y;
      const distanceSquared = dx * dx + dy * dy;
      if (distanceSquared < bestDistanceSquared) {
        bestDistanceSquared = distanceSquared;
        best = enemy;
      }
    }
    return best;
  }

  private spawnBullet(target: EnemyModel): void {
    const dx = target.x - this.playerPosition.x;
    const dy = target.y - this.playerPosition.y;
    const baseAngle = Math.atan2(dy, dx);
    const angle = baseAngle + Phaser.Math.FloatBetween(-BULLET.spread, BULLET.spread);
    const graphic = this.add.circle(
      this.playerPosition.x,
      this.playerPosition.y,
      BULLET.radius,
      COLORS.neonYellow,
      1,
    );
    graphic.setStrokeStyle(1, 0xffffff, 0.65);

    this.bullets.push({
      graphic,
      x: this.playerPosition.x,
      y: this.playerPosition.y,
      vx: Math.cos(angle) * BULLET.speed,
      vy: Math.sin(angle) * BULLET.speed,
      ttl: BULLET.lifetime,
      damage: this.bulletDamage,
    });
  }

  private updateBullets(dt: number): void {
    const remainingBullets: BulletModel[] = [];
    for (const bullet of this.bullets) {
      bullet.x += bullet.vx * dt;
      bullet.y += bullet.vy * dt;
      bullet.ttl -= dt;
      bullet.graphic.setPosition(bullet.x, bullet.y);

      let hitEnemy: EnemyModel | null = null;
      for (const enemy of this.enemies) {
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
        this.spawnHitFlash(hitEnemy.x, hitEnemy.y);
        continue;
      }

      const insideBounds =
        bullet.x >= -80 &&
        bullet.x <= GAME_WIDTH + 80 &&
        bullet.y >= -80 &&
        bullet.y <= GAME_HEIGHT + 80;
      if (bullet.ttl > 0 && insideBounds) {
        remainingBullets.push(bullet);
      } else {
        bullet.graphic.destroy();
      }
    }

    this.bullets = remainingBullets;
    this.cleanupDeadEnemies();
  }

  private updateRockets(dt: number): void {
    if (this.rocketsLevel >= 0) {
      this.rocketTimer += dt;
      while (this.rocketTimer >= this.rocketCooldown) {
        this.rocketTimer -= this.rocketCooldown;
        this.spawnRocket();
      }
    }

    const remaining: RocketModel[] = [];
    for (const rocket of this.rockets) {
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
      for (const enemy of this.enemies) {
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

      this.explodeRocket(rocket);
    }
    this.rockets = remaining;
    this.cleanupDeadEnemies();
  }

  private updateLasers(dt: number): void {
    if (this.laserLevel >= 0) {
      this.laserTimer += dt;
      while (this.laserTimer >= this.laserCooldown) {
        this.laserTimer -= this.laserCooldown;
        this.fireLaser();
      }
    }

    const remaining: LaserModel[] = [];
    for (const laser of this.lasers) {
      laser.ttl -= dt;
      if (laser.ttl > 0) {
        laser.graphic.setAlpha(laser.ttl / LASER.lifetime);
        remaining.push(laser);
      } else {
        laser.graphic.destroy();
      }
    }
    this.lasers = remaining;
  }

  private updateEmp(dt: number): void {
    if (this.empLevel >= 0) {
      this.empTimer += dt;
      while (this.empTimer >= EMP.pulseInterval) {
        this.empTimer -= EMP.pulseInterval;
        this.fireEmpPulse();
      }
    }

    const remaining: EmpPulseModel[] = [];
    for (const pulse of this.empPulses) {
      pulse.ttl -= dt;
      if (pulse.ttl > 0) {
        pulse.graphic.setAlpha(0.7 * (pulse.ttl / EMP.pulseLifetime));
        remaining.push(pulse);
      } else {
        pulse.graphic.destroy();
      }
    }
    this.empPulses = remaining;
    this.cleanupDeadEnemies();
  }

  private updateShield(dt: number): void {
    if (this.shieldLevel < 0) {
      return;
    }

    const ratio = this.shieldMax > 0 ? this.shieldHp / this.shieldMax : 0;
    this.shieldRing.setStrokeStyle(3, 0x6fb3ff, ratio > 0 ? 0.2 + ratio * 0.55 : 0);

    if (this.shieldHp >= this.shieldMax) {
      return;
    }
    if (this.shieldRegenDelay > 0) {
      this.shieldRegenDelay = Math.max(0, this.shieldRegenDelay - dt);
      return;
    }
    this.shieldHp = Math.min(this.shieldMax, this.shieldHp + this.shieldRegenRate * dt);
  }

  private cleanupDeadEnemies(): void {
    const survivors: EnemyModel[] = [];
    for (const enemy of this.enemies) {
      if (enemy.hp > 0) {
        survivors.push(enemy);
        continue;
      }
      enemy.graphic.destroy();
      this.enemiesKilled += 1;
      this.spawnXpGem(enemy.x, enemy.y, enemy.xpValue);
      this.spawnDeathBurst(enemy.x, enemy.y, enemy.isBoss);
    }
    this.enemies = survivors;
  }

  private spawnXpGem(x: number, y: number, value: number): void {
    const graphic = this.add.circle(x, y, 6, COLORS.neonGreen, 0.95);
    graphic.setStrokeStyle(2, COLORS.neonCyan, 0.75);
    this.xpGems.push({ graphic, x, y, value, lifetime: XP_GEM.lifetime });
  }

  private updateXpGems(dt: number): void {
    const remainingGems: XpGemModel[] = [];
    for (const gem of this.xpGems) {
      gem.lifetime -= dt;
      const dx = this.playerPosition.x - gem.x;
      const dy = this.playerPosition.y - gem.y;
      const distanceSquared = dx * dx + dy * dy;

      if (this.tractorRange > 0 && distanceSquared < this.tractorRange * this.tractorRange) {
        const distance = Math.max(0.001, Math.sqrt(distanceSquared));
        gem.x += (dx / distance) * XP_GEM.magnetSpeed * dt;
        gem.y += (dy / distance) * XP_GEM.magnetSpeed * dt;
      }

      gem.graphic.setPosition(gem.x, gem.y);
      if (distanceSquared <= XP_GEM.pickupRadius * XP_GEM.pickupRadius) {
        gem.graphic.destroy();
        this.addXp(gem.value);
        continue;
      }

      if (gem.lifetime > 0) {
        remainingGems.push(gem);
      } else {
        gem.graphic.destroy();
      }
    }
    this.xpGems = remainingGems;
  }

  private addXp(amount: number): void {
    this.playerXp += amount;
    while (this.playerXp >= this.xpToNext) {
      this.playerXp -= this.xpToNext;
      this.playerLevel += 1;
      this.xpToNext = Math.round(
        PLAYER.xpBase * PLAYER.xpGrowth ** (this.playerLevel - 1) +
          PLAYER.xpLinearBonus * (this.playerLevel - 1),
      );
      this.upgradeOptions = this.generateUpgradeOptions();
      if (this.upgradeOptions.length > 0) {
        this.mode = "levelup";
        showLevelUpOverlay(
          this.overlay,
          this,
          this.upgradeOptions,
          UPGRADE_DEFINITIONS,
          (id) => this.getUpgradeState(id),
        );
        return;
      }
    }
  }

  private generateUpgradeOptions(): UpgradeId[] {
    const allOptions = (Object.keys(UPGRADE_DEFINITIONS) as UpgradeId[]).filter((id) => {
      const state = this.getUpgradeState(id);
      return state.level < state.maxLevel;
    });
    Phaser.Utils.Array.Shuffle(allOptions);
    return allOptions.slice(0, Math.min(3, allOptions.length));
  }

  private getUpgradeState(id: UpgradeId): UpgradeState {
    switch (id) {
      case "minigun":
        return { level: this.minigunLevel, maxLevel: UPGRADE_DEFINITIONS.minigun.maxLevel };
      case "rockets":
        return { level: this.rocketsLevel, maxLevel: UPGRADE_DEFINITIONS.rockets.maxLevel };
      case "laser":
        return { level: this.laserLevel, maxLevel: UPGRADE_DEFINITIONS.laser.maxLevel };
      case "emp":
        return { level: this.empLevel, maxLevel: UPGRADE_DEFINITIONS.emp.maxLevel };
      case "health":
        return { level: this.healthLevel, maxLevel: UPGRADE_DEFINITIONS.health.maxLevel };
      case "shield":
        return { level: this.shieldLevel, maxLevel: UPGRADE_DEFINITIONS.shield.maxLevel };
      case "tractor":
        return { level: this.tractorLevel, maxLevel: UPGRADE_DEFINITIONS.tractor.maxLevel };
      case "speed":
        return { level: this.speedLevel, maxLevel: UPGRADE_DEFINITIONS.speed.maxLevel };
    }
  }

  private selectUpgrade(index: number): void {
    const id = this.upgradeOptions[index];
    if (!id) {
      return;
    }

    const definition = UPGRADE_DEFINITIONS[id];
    const nextLevel = this.getUpgradeState(id).level + 1;
    definition.apply(this, nextLevel);
    this.mode = "play";
    this.overlay.container.setVisible(false);
    this.hud.prompt.setText(`${definition.name} acquired   Survive 15 minutes`);
    this.updateHud();
  }

  private updateHud(): void {
    const minutes = Math.floor(this.remaining / 60);
    const seconds = Math.floor(this.remaining % 60);
    this.hud.timer.setText(`${minutes}:${seconds.toString().padStart(2, "0")}`);
    this.hud.level.setText(`LVL ${this.playerLevel}`);
    this.hud.xp.setText(`XP ${Math.floor(this.playerXp)} / ${this.xpToNext}`);
    this.hud.kills.setText(`KILLS ${this.enemiesKilled}`);
    this.hud.hp.setText(`HP ${Math.ceil(this.playerHp)} / ${Math.ceil(this.playerMaxHp)}`);
    this.hud.status.setText(this.buildStatusText());
  }

  private formatElapsed(): string {
    const total = Math.floor(this.elapsed);
    const minutes = Math.floor(total / 60);
    const seconds = total % 60;
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  }

  private spawnHitFlash(x: number, y: number): void {
    const flash = this.add.circle(x, y, 8, COLORS.neonYellow, 0.55);
    this.tweens.add({
      targets: flash,
      alpha: 0,
      scale: 2.2,
      duration: 90,
      onComplete: () => flash.destroy(),
    });
  }

  private spawnDeathBurst(x: number, y: number, isBoss: boolean): void {
    const burst = this.add.circle(x, y, isBoss ? 20 : 14, isBoss ? 0xff834d : COLORS.enemyRed, 0.35);
    burst.setStrokeStyle(2, isBoss ? 0xfff0cf : 0xff9999, 0.8);
    this.tweens.add({
      targets: burst,
      alpha: 0,
      scale: 2.6,
      duration: isBoss ? 260 : 180,
      onComplete: () => burst.destroy(),
    });
  }

  private spawnRocket(): void {
    const pointer = this.input.activePointer.positionToCamera(this.cameras.main) as Phaser.Math.Vector2;
    const dx = pointer.x - this.playerPosition.x;
    const dy = pointer.y - this.playerPosition.y;
    const distance = Math.max(0.001, Math.hypot(dx, dy));
    const trail = this.add.graphics();
    const graphic = this.add.circle(this.playerPosition.x, this.playerPosition.y, ROCKET.radius, 0xff9600, 1);
    graphic.setStrokeStyle(1, 0xffefbf, 0.9);

    this.rockets.push({
      graphic,
      trail,
      x: this.playerPosition.x,
      y: this.playerPosition.y,
      vx: (dx / distance) * ROCKET.speed,
      vy: (dy / distance) * ROCKET.speed,
      targetX: pointer.x,
      targetY: pointer.y,
      ttl: ROCKET.lifetime,
      damage: this.rocketDamage,
      splashRadius: this.rocketSplashRadius,
    });
  }

  private explodeRocket(rocket: RocketModel): void {
    rocket.graphic.destroy();
    rocket.trail.destroy();

    for (const enemy of this.enemies) {
      const dx = enemy.x - rocket.x;
      const dy = enemy.y - rocket.y;
      if (dx * dx + dy * dy <= rocket.splashRadius ** 2) {
        enemy.hp -= rocket.damage;
        this.spawnHitFlash(enemy.x, enemy.y);
      }
    }

    const burst = this.add.circle(rocket.x, rocket.y, rocket.splashRadius * 0.55, 0xff9600, 0.25);
    burst.setStrokeStyle(2, 0xffefbf, 0.8);
    this.tweens.add({
      targets: burst,
      alpha: 0,
      scale: 1.8,
      duration: 180,
      onComplete: () => burst.destroy(),
    });
  }

  private fireLaser(): void {
    const pointer = this.input.activePointer.positionToCamera(this.cameras.main) as Phaser.Math.Vector2;
    const dx = pointer.x - this.playerPosition.x;
    const dy = pointer.y - this.playerPosition.y;
    const distance = Math.max(0.001, Math.hypot(dx, dy));
    const nx = dx / distance;
    const ny = dy / distance;
    const length = Math.max(GAME_WIDTH, GAME_HEIGHT) * 1.25;
    const endX = this.playerPosition.x + nx * length;
    const endY = this.playerPosition.y + ny * length;

    for (const enemy of this.enemies) {
      if (
        distanceToSegmentSquared(
          enemy.x,
          enemy.y,
          this.playerPosition.x,
          this.playerPosition.y,
          endX,
          endY,
        ) <=
        (enemy.radius + LASER.width) ** 2
      ) {
        enemy.hp -= this.laserDamage;
        this.spawnHitFlash(enemy.x, enemy.y);
      }
    }

    const graphic = this.add.line(
      0,
      0,
      this.playerPosition.x,
      this.playerPosition.y,
      endX,
      endY,
      COLORS.neonCyan,
      0.85,
    );
    graphic.setOrigin(0, 0);
    graphic.setLineWidth(LASER.width, LASER.width);
    this.lasers.push({ graphic, ttl: LASER.lifetime });
    this.cleanupDeadEnemies();
  }

  private fireEmpPulse(): void {
    const graphic = this.add.circle(
      this.playerPosition.x,
      this.playerPosition.y,
      this.empRadius,
      COLORS.neonMagenta,
      0.08,
    );
    graphic.setStrokeStyle(3, COLORS.neonMagenta, 0.7);
    this.empPulses.push({ graphic, ttl: EMP.pulseLifetime });

    for (const enemy of this.enemies) {
      const dx = enemy.x - this.playerPosition.x;
      const dy = enemy.y - this.playerPosition.y;
      if (dx * dx + dy * dy <= this.empRadius ** 2) {
        enemy.hp -= this.empDamage;
        this.spawnHitFlash(enemy.x, enemy.y);
      }
    }
  }

  private applyPlayerDamage(amount: number): void {
    if (this.shieldLevel >= 0 && this.shieldHp > 0) {
      if (this.shieldHp >= amount) {
        this.shieldHp -= amount;
      } else {
        const remaining = amount - this.shieldHp;
        this.shieldHp = 0;
        this.playerHp = Math.max(0, this.playerHp - remaining);
      }
      this.shieldRegenDelay = this.shieldRegenDelayMax;
      return;
    }
    this.playerHp = Math.max(0, this.playerHp - amount);
  }

  private buildStatusText(): string {
    return [
      `Minigun L${this.minigunLevel + 1}`,
      this.rocketsLevel >= 0 ? `Rockets L${this.rocketsLevel + 1}` : "Rockets locked",
      this.laserLevel >= 0 ? `Laser L${this.laserLevel + 1}` : "Laser locked",
      this.empLevel >= 0 ? `EMP L${this.empLevel + 1}` : "EMP locked",
      this.shieldLevel >= 0
        ? `Shield ${Math.ceil(this.shieldHp)}/${Math.ceil(this.shieldMax)}`
        : "Shield offline",
    ].join("\n");
  }

}
