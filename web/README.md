# Geometry Survivors Web

Initial browser migration scaffold for the Phaser + TypeScript version of the game.

## Scripts

```bash
npm install
npm run dev
```

## Current State

- Vite + TypeScript app scaffolded
- Phaser boot path in place
- Browser game canvas sized to `1100x700`
- Playable scene with:
- controllable player movement
- enemy spawning and chase behavior
- nearest-enemy auto-fire
- enemy kills with XP gem drops
- HUD for timer, level, XP, kills, and HP
- start screen, win/lose overlays, and restart flow
- first-pass level-up choices for:
- minigun
- rockets
- laser
- EMP
- health
- shield
- tractor beam
- speed
- combat support for rockets, laser beam, EMP pulse, and shield absorption

## Next Steps

- tune damage, cooldowns, and pacing against the Python build
- split menu/gameplay/overlay concerns into cleaner modules now that the scene is bigger
- add pause/options/cutscene flow after core combat parity is stronger
