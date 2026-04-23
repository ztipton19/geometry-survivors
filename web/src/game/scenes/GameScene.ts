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
import { distanceToSegmentSquared } from "../utils/geometry";
import type {
  BulletModel,
  EmpPulseModel,
  EnemyModel,
  LaserModel,
  RocketModel,
  XpGemModel,
} from "../types/gameplay";
import { computeSpawnInterval, spawnEnemy } from "../systems/enemies";
import {
  cleanupDeadEnemies,
  fireEmpPulse,
  fireLaser,
  findNearestEnemy,
  spawnBullet,
  spawnRocket,
  updateBullets,
  updateEmpPulses,
  updateLasers,
  updateRockets,
} from "../systems/combat";
import {
  applyPlayerDamage,
  awardXp,
  generateUpgradeOptions,
  getUpgradeState,
  resetProgression,
  updateShield,
} from "../systems/progression";
import { spawnXpGem, updateXpGems } from "../systems/xp";

type GameMode = "menu" | "play" | "levelup" | "win" | "lose";

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
  public playerLevel = 1;
  public playerXp = 0;
  public xpToNext: number = PLAYER.xpBase;
  public enemiesKilled = 0;

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

  private gridTile!: Phaser.GameObjects.TileSprite;
  private starLayers: { tile: Phaser.GameObjects.TileSprite; parallax: number }[] = [];

  constructor() {
    super("game");
  }

  private setRunHudVisible(visible: boolean): void {
    this.hud.timer.setVisible(visible);
    this.hud.level.setVisible(visible);
    this.hud.xpBarBack.setVisible(visible);
    this.hud.xpBarFill.setVisible(visible);
    this.hud.kills.setVisible(visible);
    this.hud.healthBarBack.setVisible(visible);
    this.hud.healthBarFill.setVisible(visible);
    this.hud.shieldBarBack.setVisible(visible);
    this.hud.shieldBarFill.setVisible(visible);
  }

  create(): void {
    this.createInfiniteBackground();
    this.hud = createHud(this);
    this.setRunHudVisible(false);
    this.hud.title.setVisible(false);
    this.createPlayer();
    this.cameras.main.startFollow(this.player, false, 1, 1);
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
    this.updateBackground();

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
    const pointer = this.input.activePointer.positionToCamera(this.cameras.main) as Phaser.Math.Vector2;
    const angle = Phaser.Math.Angle.Between(
      this.playerPosition.x,
      this.playerPosition.y,
      pointer.x,
      pointer.y,
    );
    const forward = new Phaser.Math.Vector2(Math.cos(angle), Math.sin(angle));
    const lateral = new Phaser.Math.Vector2(-forward.y, forward.x);

    if (this.cursors.up.isDown || this.wasd.W.isDown) {
      this.velocity.add(forward.clone().scale(PLAYER.thrust * dt));
    }

    if (this.cursors.down.isDown || this.wasd.S.isDown) {
      this.velocity.add(forward.clone().scale(-PLAYER.reverseThrust * dt));
    }

    if (Phaser.Input.Keyboard.JustDown(this.wasd.A)) {
      this.velocity.add(lateral.clone().scale(-PLAYER.lateralNudgeImpulse));
    }

    if (Phaser.Input.Keyboard.JustDown(this.wasd.D)) {
      this.velocity.add(lateral.clone().scale(PLAYER.lateralNudgeImpulse));
    }

    this.velocity.scale(Math.pow(PLAYER.damping, dt * 60));
    this.velocity.limit(this.maxSpeed);
    this.playerPosition.add(this.velocity.clone().scale(dt));

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

    this.player = this.add.container(this.playerPosition.x, this.playerPosition.y, [body]);
    this.shieldRing = this.add.circle(this.playerPosition.x, this.playerPosition.y, 24);
    this.shieldRing.setStrokeStyle(3, 0x6fb3ff, 0);
    this.shieldRing.setFillStyle(0x6fb3ff, 0);
  }

  private createInfiniteBackground(): void {
    // Create grid tile texture
    const gridSize = 40;
    const gridKey = "__grid_tile";
    if (!this.textures.exists(gridKey)) {
      const canvas = this.textures.createCanvas(gridKey, gridSize, gridSize)!;
      const ctx = canvas.getContext();
      ctx.fillStyle = "#05070a";
      ctx.fillRect(0, 0, gridSize, gridSize);
      ctx.strokeStyle = "rgba(16,50,74,0.34)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(gridSize, 0);
      ctx.lineTo(gridSize, gridSize);
      ctx.moveTo(0, gridSize);
      ctx.lineTo(gridSize, gridSize);
      ctx.stroke();
      canvas.refresh();
    }
    this.gridTile = this.add.tileSprite(0, 0, GAME_WIDTH, GAME_HEIGHT, gridKey);
    this.gridTile.setOrigin(0, 0);
    this.gridTile.setDepth(-100);
    this.gridTile.setScrollFactor(0);

    // Create parallax star layers
    this.starLayers = [];
    this.createStarLayer("__stars_far", 512, 200, 0.4, 0.8, 0.25, -90, 0.3);
    this.createStarLayer("__stars_mid", 512, 80, 0.7, 1.2, 0.45, -80, 0.6);
    this.createStarLayer("__stars_near", 512, 30, 1.0, 1.8, 0.65, -70, 1.0);
  }

  private createStarLayer(
    key: string,
    tileSize: number,
    count: number,
    minRadius: number,
    maxRadius: number,
    alpha: number,
    depth: number,
    parallax: number,
  ): void {
    if (!this.textures.exists(key)) {
      const canvas = this.textures.createCanvas(key, tileSize, tileSize)!;
      const ctx = canvas.getContext();
      ctx.clearRect(0, 0, tileSize, tileSize);
      for (let i = 0; i < count; i += 1) {
        const x = Math.random() * tileSize;
        const y = Math.random() * tileSize;
        const r = minRadius + Math.random() * (maxRadius - minRadius);
        const brightness = 150 + Math.floor(Math.random() * 105);
        ctx.fillStyle = `rgba(${brightness}, ${brightness}, ${brightness}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      }
      canvas.refresh();
    }
    const tile = this.add.tileSprite(0, 0, GAME_WIDTH, GAME_HEIGHT, key);
    tile.setOrigin(0, 0);
    tile.setDepth(depth);
    tile.setScrollFactor(0);
    this.starLayers.push({ tile, parallax });
  }

  private updateBackground(): void {
    const scrollX = this.cameras.main.scrollX;
    const scrollY = this.cameras.main.scrollY;
    this.gridTile.tilePositionX = scrollX;
    this.gridTile.tilePositionY = scrollY;
    for (const { tile, parallax } of this.starLayers) {
      tile.tilePositionX = scrollX * parallax;
      tile.tilePositionY = scrollY * parallax;
    }
  }

  private startRun(): void {
    this.clearWorld();
    this.mode = "play";
    this.overlay.container.setVisible(false);
    this.setRunHudVisible(true);
    this.hud.title.setVisible(false);
    this.hud.prompt.setVisible(false);
    this.elapsed = 0;
    this.remaining = ROUND_SECONDS;
    this.spawnTimer = 0;
    this.fireTimer = 0;
    this.rocketTimer = 0;
    this.laserTimer = 0;
    this.empTimer = 0;
    this.playerPosition.set(GAME_WIDTH / 2, GAME_HEIGHT / 2);
    this.player.setPosition(this.playerPosition.x, this.playerPosition.y);
    this.cameras.main.centerOn(this.playerPosition.x, this.playerPosition.y);
    this.velocity.set(0, 0);

    resetProgression(this);
    this.shieldRing.setStrokeStyle(3, 0x6fb3ff, 0);
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
    const spawnInterval = computeSpawnInterval(this.elapsed);

    while (this.spawnTimer >= spawnInterval) {
      this.spawnTimer -= spawnInterval;
      this.enemies.push(
        spawnEnemy(this, this.elapsed, this.playerPosition.x, this.playerPosition.y),
      );
    }
  }

  private updateEnemies(dt: number): void {
    for (const enemy of this.enemies) {
      const dx = this.playerPosition.x - enemy.x;
      const dy = this.playerPosition.y - enemy.y;
      const distance = Math.max(0.001, Math.hypot(dx, dy));
      enemy.x += (dx / distance) * enemy.speed * dt * 7;
      enemy.y += (dy / distance) * enemy.speed * dt * 7;
      enemy.touchCooldown = Math.max(0, enemy.touchCooldown - dt);

      if (distance < enemy.radius + PLAYER.radius + 6 && enemy.touchCooldown <= 0) {
        enemy.touchCooldown = ENEMY.contactDamageCooldown;
        applyPlayerDamage(this, enemy.damage * 0.3);
        this.spawnHitFlash(this.playerPosition.x, this.playerPosition.y);
      }

      enemy.graphic.setPosition(enemy.x, enemy.y);
      enemy.graphic.rotation += dt * (enemy.isBoss ? 0.9 : 0.45);
    }
  }

  private updateAutoFire(dt: number): void {
    const cam = this.cameras.main;
    const nearest = findNearestEnemy(
      this.enemies,
      this.playerPosition.x,
      this.playerPosition.y,
      cam.scrollX,
      cam.scrollY,
      cam.width,
      cam.height,
    );
    if (!nearest) {
      this.fireTimer = 0;
      return;
    }

    this.fireTimer += dt;
    while (nearest && this.fireTimer >= this.fireCooldown) {
      this.fireTimer -= this.fireCooldown;
      this.bullets.push(
        spawnBullet(
          this,
          this.playerPosition.x,
          this.playerPosition.y,
          nearest,
          this.bulletDamage,
        ),
      );
    }
  }

  private updateBullets(dt: number): void {
    const cam = this.cameras.main;
    this.bullets = updateBullets(
      this.bullets,
      this.enemies,
      dt,
      (x, y) => this.spawnHitFlash(x, y),
      cam.scrollX,
      cam.scrollY,
      cam.width,
      cam.height,
    );
    this.cleanupDeadEnemies();
  }

  private updateRockets(dt: number): void {
    if (this.rocketsLevel >= 0) {
      this.rocketTimer += dt;
      while (this.rocketTimer >= this.rocketCooldown) {
        this.rocketTimer -= this.rocketCooldown;
        const pointer = this.input.activePointer.positionToCamera(this.cameras.main) as Phaser.Math.Vector2;
        this.rockets.push(
          spawnRocket(
            this,
            this.playerPosition.x,
            this.playerPosition.y,
            pointer.x,
            pointer.y,
            this.rocketDamage,
            this.rocketSplashRadius,
          ),
        );
      }
    }
    this.rockets = updateRockets(
      this.rockets,
      this.enemies,
      dt,
      (x, y) => this.spawnHitFlash(x, y),
      (rocket) => this.explodeRocketVisual(rocket),
    );
    this.cleanupDeadEnemies();
  }

  private updateLasers(dt: number): void {
    if (this.laserLevel >= 0) {
      this.laserTimer += dt;
      while (this.laserTimer >= this.laserCooldown) {
        this.laserTimer -= this.laserCooldown;
        const pointer = this.input.activePointer.positionToCamera(this.cameras.main) as Phaser.Math.Vector2;
        this.lasers.push(
          fireLaser(
            this,
            this.playerPosition.x,
            this.playerPosition.y,
            pointer.x,
            pointer.y,
            this.laserDamage,
            this.enemies,
            (x, y) => this.spawnHitFlash(x, y),
          ),
        );
        this.cleanupDeadEnemies();
      }
    }
    this.lasers = updateLasers(this.lasers, dt);
  }

  private updateEmp(dt: number): void {
    if (this.empLevel >= 0) {
      this.empTimer += dt;
      while (this.empTimer >= EMP.pulseInterval) {
        this.empTimer -= EMP.pulseInterval;
        this.empPulses.push(
          fireEmpPulse(
            this,
            this.playerPosition.x,
            this.playerPosition.y,
            this.empRadius,
            this.empDamage,
            this.enemies,
            (x, y) => this.spawnHitFlash(x, y),
          ),
        );
      }
    }
    this.empPulses = updateEmpPulses(this.empPulses, dt);
    this.cleanupDeadEnemies();
  }

  private updateShield(dt: number): void {
    const alpha = updateShield(this, dt);
    this.shieldRing.setStrokeStyle(3, 0x6fb3ff, alpha);
  }

  private cleanupDeadEnemies(): void {
    this.enemies = cleanupDeadEnemies(this.enemies, (enemy) => {
      this.enemiesKilled += 1;
      this.xpGems = spawnXpGem(
        this,
        this.xpGems,
        this.playerPosition.x,
        this.playerPosition.y,
        enemy.x,
        enemy.y,
        enemy.xpValue,
      );
      this.spawnDeathBurst(enemy.x, enemy.y, enemy.isBoss);
    });
  }

  private updateXpGems(dt: number): void {
    this.xpGems = updateXpGems(
      this.xpGems,
      this.playerPosition.x,
      this.playerPosition.y,
      this.tractorRange,
      dt,
      (value) => this.addXp(value),
    );
  }

  private addXp(amount: number): void {
    if (awardXp(this, amount)) {
      this.upgradeOptions = generateUpgradeOptions(this);
      if (this.upgradeOptions.length > 0) {
        this.mode = "levelup";
        showLevelUpOverlay(this.overlay, this, this.upgradeOptions, UPGRADE_DEFINITIONS, (id) =>
          this.getUpgradeState(id),
        );
        return;
      }
    }
  }

  private getUpgradeState(id: UpgradeId): UpgradeState {
    return getUpgradeState(this, id);
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
    this.hud.level.setText(`LEVEL: ${this.playerLevel}`);
    this.hud.kills.setText(`Targets Eliminated: ${this.enemiesKilled}`);

    const xpRatio = this.xpToNext > 0 ? Phaser.Math.Clamp(this.playerXp / this.xpToNext, 0, 1) : 0;
    const xpFillHeight = 108 * xpRatio;
    this.hud.xpBarFill.setSize(8, Math.max(0, xpFillHeight));
    this.hud.xpBarFill.setPosition(35, 160);

    const healthRatio =
      this.playerMaxHp > 0 ? Phaser.Math.Clamp(this.playerHp / this.playerMaxHp, 0, 1) : 0;
    this.hud.healthBarFill.setScale(healthRatio, 1);
    this.hud.healthBarFill.setAlpha(healthRatio > 0 ? 0.95 : 0.25);

    const shieldUnlocked = this.shieldLevel >= 0 && this.shieldMax > 0;
    const shieldRatio =
      shieldUnlocked ? Phaser.Math.Clamp(this.shieldHp / this.shieldMax, 0, 1) : 1;
    this.hud.shieldBarBack.setFillStyle(0x10233d, shieldUnlocked ? 0.45 : 0.14);
    this.hud.shieldBarBack.setStrokeStyle(1, 0x86bdff, shieldUnlocked ? 0.65 : 0.22);
    this.hud.shieldBarFill.setScale(shieldRatio, 1);
    this.hud.shieldBarFill.setFillStyle(0x7fc1ff, shieldUnlocked ? 0.95 : 0.16);
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

  private explodeRocketVisual(rocket: RocketModel): void {
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

}
