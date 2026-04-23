import Phaser from "phaser";

import { COLORS, GAME_HEIGHT, GAME_WIDTH } from "../constants/settings";
import { CARD_COLORS, type UpgradeDefinition, type UpgradeId, type UpgradeRuntime } from "../data/upgrades";

export type Hud = {
  title: Phaser.GameObjects.Text;
  timer: Phaser.GameObjects.Text;
  level: Phaser.GameObjects.Text;
  xpBarBack: Phaser.GameObjects.Rectangle;
  xpBarFill: Phaser.GameObjects.Rectangle;
  kills: Phaser.GameObjects.Text;
  healthBarBack: Phaser.GameObjects.Rectangle;
  healthBarFill: Phaser.GameObjects.Rectangle;
  shieldBarBack: Phaser.GameObjects.Rectangle;
  shieldBarFill: Phaser.GameObjects.Rectangle;
  railGunLabel: Phaser.GameObjects.Text;
  railGunChargeBack: Phaser.GameObjects.Graphics;
  railGunChargeFill: Phaser.GameObjects.Graphics;
  rocketLabel: Phaser.GameObjects.Text;
  rocketChargeBack: Phaser.GameObjects.Graphics;
  rocketChargeFill: Phaser.GameObjects.Graphics;
  prompt: Phaser.GameObjects.Text;
};

export type UpgradeCard = {
  container: Phaser.GameObjects.Container;
  background: Phaser.GameObjects.Rectangle;
  number: Phaser.GameObjects.Text;
  title: Phaser.GameObjects.Text;
  detail: Phaser.GameObjects.Text;
  hint: Phaser.GameObjects.Text;
  bounds: Phaser.Geom.Rectangle;
};

export type Overlay = {
  container: Phaser.GameObjects.Container;
  backdrop: Phaser.GameObjects.Rectangle;
  title: Phaser.GameObjects.Text;
  subtitle: Phaser.GameObjects.Text;
  cards: UpgradeCard[];
  footer: Phaser.GameObjects.Text;
};

function setCardVisible(card: UpgradeCard, visible: boolean): void {
  card.container.setVisible(visible);
  card.background.setVisible(visible);
  card.number.setVisible(visible);
  card.title.setVisible(visible);
  card.detail.setVisible(visible);
  card.hint.setVisible(visible);
}

export function createHud(scene: Phaser.Scene): Hud {
  const title = scene.add
    .text(24, 14, "GEOMETRY SURVIVORS", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "28px",
      color: "#00ffff",
    })
    .setShadow(0, 0, "#00ffff", 12, true, true)
    .setScrollFactor(0);

  const timer = scene.add
    .text(GAME_WIDTH / 2, 18, "15:00", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "32px",
      color: "#ffff00",
    })
    .setOrigin(0.5, 0)
    .setShadow(0, 0, "#ffff00", 10, true, true)
    .setScrollFactor(0);

  const level = scene.add
    .text(24, 24, "LEVEL: 1", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "18px",
      color: "#f0f0f0",
    })
    .setScrollFactor(0);

  const xpBarBack = scene.add
    .rectangle(32, 52, 14, 112, 0x0b1722, 0.75)
    .setOrigin(0, 0)
    .setStrokeStyle(2, 0x6be48d, 0.55)
    .setScrollFactor(0);

  const xpBarFill = scene.add
    .rectangle(35, 161, 8, 0, 0x8ef5a8, 0.92)
    .setOrigin(0, 1)
    .setScrollFactor(0);

  const barY = 28;
  const barWidth = 250;
  const barHeight = 14;
  const barGap = 74;
  const timerGap = 70;

  const healthBarBack = scene.add
    .rectangle(GAME_WIDTH / 2 - timerGap - barWidth, barY, barWidth, barHeight, 0x3b1010, 0.55)
    .setOrigin(0, 0)
    .setStrokeStyle(1, 0xff8f8f, 0.55)
    .setScrollFactor(0);

  const healthBarFill = scene.add
    .rectangle(GAME_WIDTH / 2 - timerGap - barWidth + 2, barY + 2, barWidth - 4, barHeight - 4, 0xff4e4e, 0.9)
    .setOrigin(0, 0)
    .setScrollFactor(0);

  const kills = scene.add
    .text(GAME_WIDTH - 24, 24, "Targets Eliminated: 0", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "16px",
      color: "#ff3c3c",
    })
    .setOrigin(1, 0)
    .setScrollFactor(0);

  const shieldBarBack = scene.add
    .rectangle(GAME_WIDTH / 2 + timerGap, barY, barWidth, barHeight, 0x10233d, 0.22)
    .setOrigin(0, 0)
    .setStrokeStyle(1, 0x86bdff, 0.4)
    .setScrollFactor(0);

  const shieldBarFill = scene.add
    .rectangle(GAME_WIDTH / 2 + timerGap + 2, barY + 2, barWidth - 4, barHeight - 4, 0x7fc1ff, 0.2)
    .setOrigin(0, 0)
    .setScrollFactor(0);

  const railGunLabel = scene.add
    .text(GAME_WIDTH / 2 - 34, GAME_HEIGHT / 2 - 28, "RG", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "16px",
      color: "#5cf2ff",
    })
    .setOrigin(0.5, 1)
    .setAlpha(0.5);

  const railGunChargeBack = scene.add.graphics().setPosition(GAME_WIDTH / 2, GAME_HEIGHT / 2);
  const railGunChargeFill = scene.add.graphics().setPosition(GAME_WIDTH / 2, GAME_HEIGHT / 2);

  const rocketLabel = scene.add
    .text(GAME_WIDTH / 2 + 34, GAME_HEIGHT / 2 - 28, "R", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "16px",
      color: "#ffb35a",
    })
    .setOrigin(0.5, 1)
    .setAlpha(0.5);

  const rocketChargeBack = scene.add.graphics().setPosition(GAME_WIDTH / 2, GAME_HEIGHT / 2);
  const rocketChargeFill = scene.add.graphics().setPosition(GAME_WIDTH / 2, GAME_HEIGHT / 2);

  const prompt = scene.add
    .text(24, GAME_HEIGHT - 34, "W/S thrust   A/D rotate   Mouse guides rockets", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "16px",
      color: "#00ff78",
    })
    .setAlpha(0.85)
    .setScrollFactor(0);

  return {
    title,
    timer,
    level,
    xpBarBack,
    xpBarFill,
    kills,
    healthBarBack,
    healthBarFill,
    shieldBarBack,
    shieldBarFill,
    railGunLabel,
    railGunChargeBack,
    railGunChargeFill,
    rocketLabel,
    rocketChargeBack,
    rocketChargeFill,
    prompt,
  };
}

export function createOverlay(scene: Phaser.Scene): Overlay {
  const backdrop = scene.add
    .rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x000000, 0.76)
    .setVisible(false);

  const title = scene.add
    .text(GAME_WIDTH / 2, 116, "", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "40px",
      color: "#ffff00",
      align: "center",
    })
    .setOrigin(0.5, 0)
    .setVisible(false);

  const subtitle = scene.add
    .text(GAME_WIDTH / 2, 168, "", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "18px",
      color: "#f0f0f0",
      align: "center",
      wordWrap: { width: 820 },
    })
    .setOrigin(0.5, 0)
    .setVisible(false);

  const footer = scene.add
    .text(GAME_WIDTH / 2, GAME_HEIGHT - 78, "", {
      fontFamily: "Trebuchet MS, sans-serif",
      fontSize: "16px",
      color: "#00ff78",
      align: "center",
    })
    .setOrigin(0.5, 0)
    .setVisible(false);

  const cards: UpgradeCard[] = [];
  const cardWidth = 280;
  const cardHeight = 190;
  const gap = 26;
  const startX = (GAME_WIDTH - (cardWidth * 3 + gap * 2)) / 2;

  for (let i = 0; i < 3; i += 1) {
    const x = startX + i * (cardWidth + gap);
    const y = 250;
    const bounds = new Phaser.Geom.Rectangle(x, y, cardWidth, cardHeight);
    const background = scene.add
      .rectangle(x + cardWidth / 2, y + cardHeight / 2, cardWidth, cardHeight, 0x1a1f2a, 0.95)
      .setStrokeStyle(2, CARD_COLORS[i], 0.9)
      .setVisible(false);
    const number = scene.add
      .text(x + 18, y + 14, `${i + 1}`, {
        fontFamily: "Trebuchet MS, sans-serif",
        fontSize: "30px",
        color: Phaser.Display.Color.IntegerToColor(CARD_COLORS[i]).rgba,
      })
      .setVisible(false);
    const titleText = scene.add
      .text(x + 62, y + 18, "", {
        fontFamily: "Trebuchet MS, sans-serif",
        fontSize: "20px",
        color: "#ffffff",
        wordWrap: { width: cardWidth - 78 },
      })
      .setVisible(false);
    const detail = scene.add
      .text(x + 18, y + 62, "", {
        fontFamily: "Trebuchet MS, sans-serif",
        fontSize: "15px",
        color: "#d0d7de",
        wordWrap: { width: cardWidth - 36 },
        lineSpacing: 6,
      })
      .setVisible(false);
    const hint = scene.add
      .text(x + 18, y + cardHeight - 34, `Press ${i + 1} or click`, {
        fontFamily: "Trebuchet MS, sans-serif",
        fontSize: "14px",
        color: "#88ffb0",
      })
      .setVisible(false);

    const container = scene.add
      .container(0, 0, [background, number, titleText, detail, hint])
      .setVisible(false);
    cards.push({ container, background, number, title: titleText, detail, hint, bounds });
  }

  const container = scene.add.container(0, 0, [
    backdrop,
    title,
    subtitle,
    footer,
    ...cards.map((card) => card.container),
  ]);
  container.setDepth(20);
  container.setScrollFactor(0);
  container.setVisible(false);

  return { container, backdrop, title, subtitle, cards, footer };
}

export function showMenuOverlay(overlay: Overlay): void {
  overlay.container.setVisible(true);
  overlay.backdrop.setFillStyle(0x000000, 0.72);
  overlay.title.setText("GEOMETRY SURVIVORS").setColor("#00ffff").setVisible(true);
  overlay.subtitle
    .setText(
      "Browser migration build\nFight off the swarm and survive 15 minutes.\n\nPress Enter or Space to deploy.",
    )
    .setVisible(true);
  overlay.footer
    .setText("Current web slice: core combat, full weapon kit, and survival upgrades")
    .setVisible(true);
  for (const card of overlay.cards) {
    setCardVisible(card, false);
  }
}

export function showLevelUpOverlay<TScene extends UpgradeRuntime>(
  overlay: Overlay,
  scene: TScene,
  options: UpgradeId[],
  definitions: Record<UpgradeId, UpgradeDefinition<TScene>>,
  getUpgradeState: (id: UpgradeId) => { level: number },
): void {
  overlay.container.setVisible(true);
  overlay.backdrop.setFillStyle(0x000000, 0.82);
  overlay.title.setText("LEVEL UP!").setColor("#ffff00").setVisible(true);
  overlay.subtitle.setText("Choose an upgrade to keep the run alive.").setVisible(true);
  overlay.footer.setText("Select with 1, 2, 3 or click a card").setVisible(true);

  for (let i = 0; i < overlay.cards.length; i += 1) {
    const card = overlay.cards[i];
    const id = options[i];
    if (!id) {
      setCardVisible(card, false);
      continue;
    }

    const definition = definitions[id];
    const nextLevel = getUpgradeState(id).level + 1;
    card.title.setText(definition.name);
    card.detail.setText(
      [
        definition.category,
        `Current: ${definition.currentDescription(scene)}`,
        `Next: ${definition.nextDescription(scene, nextLevel)}`,
      ].join("\n"),
    );
    setCardVisible(card, true);
  }
}

export function showEndOverlay(
  overlay: Overlay,
  title: string,
  subtitle: string,
  isWin: boolean,
): void {
  overlay.container.setVisible(true);
  overlay.backdrop.setFillStyle(0x000000, 0.78);
  overlay.title.setText(title).setColor(isWin ? "#00ff78" : "#ff5c5c").setVisible(true);
  overlay.subtitle.setText(subtitle).setVisible(true);
  overlay.footer.setText("Enter or R to restart").setVisible(true);
  for (const card of overlay.cards) {
    setCardVisible(card, false);
  }
}

export function showPauseOverlay(overlay: Overlay): void {
  overlay.container.setVisible(true);
  overlay.backdrop.setFillStyle(0x000000, 0.7);
  overlay.title.setText("PAUSED").setColor("#ffff00").setVisible(true);
  overlay.subtitle.setText("Press Esc to resume.").setVisible(true);
  overlay.footer.setText("").setVisible(false);
  for (const card of overlay.cards) {
    setCardVisible(card, false);
  }
}
