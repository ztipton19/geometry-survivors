# Geometry Survivors Web Migration Plan

## Goal

Move the game from Python (`pygame` + `pymunk`) to a browser-native stack that:

- runs as an HTML5 game on itch.io
- is easier to collaborate on with non-Python contributors
- becomes the main development path going forward
- preserves the current gameplay feel as closely as practical

The recommended target is:

- `TypeScript`
- `Phaser`
- browser-first HTML5 build
- itch.io upload as a zipped web build with an `index.html` entry point

This plan assumes we are not doing a literal automated conversion. We are doing a controlled port.

## Current Status

Migration status as of this checkpoint:

- Python remains the reference implementation under `src/`
- the web port is scaffolded and builds successfully under `web/`
- the browser version already supports a full playable combat loop
- the main remaining work has shifted from raw feature porting to tuning, UX parity, and codebase cleanup

What is already working in the web version:

- Vite + TypeScript + Phaser app scaffold
- browser entry point and production build
- neon playfield and player ship rendering
- player movement and mouse-facing
- enemy spawning, chase behavior, and scaling
- minigun auto-fire
- rockets
- laser
- EMP pulse
- XP gem drops and collection
- shield absorption and regen
- level-ups with upgrade choices
- win/lose overlays and restart flow
- extracted data/helper modules for enemy tables, upgrades, and geometry math

What is not done yet:

- balance and feel matching against the Python version
- pause/options/cutscene parity
- broader UI cleanup and scene/module decomposition
- itch.io packaging polish
- formal cutover to web as the default contributor workflow

## Why This Direction

The current game is structured well for a port:

- one clear entry point in `src/main.py`
- a central game loop in `src/game/world.py`
- entity modules in `src/game/entities/`
- gameplay systems in `src/game/systems/`
- shared tuning in `src/game/settings.py`
- UI drawing isolated in `src/game/ui.py`

That makes this a good candidate for a staged rewrite instead of a chaotic restart.

## Target End State

By the end of migration, the repo should support:

- local web development with hot reload
- a clean TypeScript codebase
- one Phaser scene stack for menus, gameplay, pause, cutscene, and game over
- an HTML5 production build suitable for itch.io
- the Python version retained only as a reference or archived legacy build

## Core Decision

We will port to `TypeScript + Phaser`, not Java.

Why:

- it is the most natural fit for HTML5 and itch.io embeds
- it lowers friction for browser-native iteration
- it makes collaboration easier for teammates comfortable with web tooling
- it avoids maintaining a Python-in-browser workaround

## Migration Principles

1. Keep the current Python build playable while the web version is being built.
2. Port systems in vertical slices, not all at once.
3. Reuse gameplay rules and tuning where possible before rebalancing.
4. Prefer simple browser-native systems over forcing one-to-one engine parity.
5. Treat the Python version as the gameplay reference, not as the long-term runtime.
6. Do not block forward progress on perfect feature parity if the web version becomes cleaner.

## Proposed Repo Shape

Recommended structure after scaffolding:

```text
geometry-survivors/
  src/                  # existing Python game kept as reference during migration
  web/
    index.html
    package.json
    tsconfig.json
    vite.config.ts
    public/
    src/
      main.ts
      game/
        config/
        constants/
        scenes/
        entities/
        systems/
        ui/
        data/
        utils/
  docs/
  MIGRATION.md
```

Notes:

- Keep the current Python code in place until the web build is clearly ahead.
- Put the new game under `web/` so the migration stays isolated and low-risk.
- Once the port is stable, we can decide whether to keep `src/` or archive it.

## Technology Stack

Recommended web stack:

- `Phaser` for rendering, scenes, input, timing, and optional physics helpers
- `TypeScript` for maintainability and onboarding
- `Vite` for fast local dev and production builds
- plain Phaser UI first, with lightweight DOM overlays only if needed

Optional later:

- `eslint` + `prettier`
- `vitest` for utility and progression logic tests
- `zustand` or another state helper only if state management becomes messy

## Python-to-Web Mapping

### Entry Point

Current:

- `src/main.py`

Target:

- `web/src/main.ts`
- boot Phaser game config
- register scenes
- mount into browser canvas

### Main Game Loop

Current:

- `src/game/world.py`

Target:

- `web/src/game/scenes/GameScene.ts`

Responsibilities to move:

- session state
- timers
- spawning
- entity lifecycle
- gameplay update loop
- state transitions for play, pause, win, lose, level-up

### Entities

Current:

- `src/game/entities/player.py`
- `src/game/entities/enemy.py`
- `src/game/entities/bullet.py`
- `src/game/entities/rocket.py`
- `src/game/entities/laser.py`
- `src/game/entities/emp_pulse.py`
- `src/game/entities/xpgem.py`
- `src/game/entities/particle.py`

Target:

- `web/src/game/entities/*.ts`

Approach:

- keep entity data lean
- use Phaser game objects where convenient
- use plain data models where rendering and simulation are better separated

### Systems

Current:

- `src/game/systems/combat.py`
- `src/game/systems/collisions.py`
- `src/game/systems/progression.py`
- `src/game/systems/spawner.py`
- `src/game/systems/upgrades.py`
- `src/game/systems/xp.py`

Target:

- `web/src/game/systems/*.ts`

Approach:

- preserve system boundaries
- move deterministic logic first
- keep rendering details out of system modules

### Settings and Tuning

Current:

- `src/game/settings.py`

Target:

- `web/src/game/constants/settings.ts`

Approach:

- port numeric tuning directly first
- rebalance only after parity checkpoints

### UI

Current:

- `src/game/ui.py`
- `src/game/cutscene.py`

Target:

- `web/src/game/ui/*.ts`
- scene-specific UI containers or overlays

Approach:

- start with canvas text and simple UI boxes
- avoid overengineering menu systems early

## Physics Strategy

This is the biggest technical fork in the road.

Current:

- `pymunk` is used, but much of the game logic is still simple enough that a full physics engine may not be necessary in the browser

Recommended target:

- do not chase exact `pymunk` parity by default
- use custom movement and collision math for most systems
- optionally use Phaser Arcade Physics only where it clearly helps

Why:

- the gameplay appears to be primarily top-down movement, homing, projectiles, overlaps, pickup attraction, and timed effects
- custom collision/math is often simpler and easier to tune than porting physics behavior exactly
- fewer moving parts means easier onboarding for your teammate

Decision:

- start with custom movement + overlap/circle math
- only introduce Phaser physics helpers if the code gets more complicated, not by default

## Rendering Strategy

Recommended first pass:

- use Phaser `Graphics` for neon primitives
- keep the current geometric look
- avoid introducing an art pipeline until the port is stable

Benefits:

- faster parity with the Python prototype
- easier single-source visual style
- fewer asset-loading complications for itch.io

## State Model

Primary game states to preserve:

- start menu
- options
- intro cutscene
- active play
- paused
- level-up choice
- win
- lose

Recommended scene layout:

- `BootScene`
- `MenuScene`
- `GameScene`
- `OverlayScene`

Alternative:

- one `GameScene` plus internal substates

Recommendation:

- use a small number of scenes and keep gameplay in one main scene
- handle overlay states with a lightweight overlay scene or modal containers

## Milestone Plan

### Phase 0: Freeze the Reference Build

Status:

- Mostly complete for practical purposes

Goal:

- lock down the Python version as the gameplay reference

Tasks:

- confirm the current Python build runs reliably
- document controls, expected flow, and important tuning values
- record short gameplay clips or screenshots for comparison
- note known rough edges that do not need to be preserved

Deliverable:

- stable reference branch and shared understanding of what we are porting

Checkpoint notes:

- the existing Python project structure has been used successfully as the migration reference
- additional capture work like gameplay clips would still help later tuning

### Phase 1: Scaffold the Web Project

Status:

- Complete

Goal:

- create a clean TypeScript + Phaser app inside `web/`

Tasks:

- initialize Vite + TypeScript
- add Phaser
- create a fixed game config matching the current aspect ratio
- add a basic boot path and empty scene structure
- set up a production build that outputs static web files

Deliverable:

- browser window opens the game shell successfully

Completed:

- `web/` app created with Vite, TypeScript, and Phaser
- local dev/build scripts are in place
- production build succeeds

### Phase 2: Recreate the Visual Baseline

Status:

- Complete

Goal:

- get a black neon geometric stage on screen with the same feel as the prototype

Tasks:

- port screen dimensions and palette from `src/game/settings.py`
- reproduce the background treatment
- render player shape
- render placeholder enemy shapes
- verify camera and coordinate assumptions

Deliverable:

- an empty but recognizable Geometry Survivors visual shell in the browser

Completed:

- current dimensions and palette were ported into `web/src/game/constants/settings.ts`
- black neon background, grid, stars, and player ship are in place
- the browser version is visually recognizable as the same game family

### Phase 3: Port the Core Playable Slice

Status:

- Complete

Goal:

- make the web build fun as quickly as possible

Scope for the first vertical slice:

- player movement
- enemy chase behavior
- auto-fire minigun
- enemy death
- XP gem drops
- XP pickup
- basic HUD
- game timer

Tasks:

- port player data model and input handling
- port nearest-enemy targeting
- port bullet spawning and bullet lifetime
- port enemy spawn timing and off-screen spawn logic
- port simple damage and death resolution
- port XP accumulation and leveling

Deliverable:

- playable browser loop with real progression

Completed:

- player movement and input
- off-screen enemy spawn and chase
- minigun targeting and bullets
- enemy death and XP drops
- XP pickup and leveling
- HUD timer, XP, kills, and HP

### Phase 4: Port Menus and Flow

Status:

- Partially complete

Goal:

- make the game feel complete, not just technically functional

Tasks:

- start menu
- options menu
- intro cutscene
- pause menu
- win/lose states
- restart flow

Deliverable:

- full session flow from launch to end

Completed:

- menu/start overlay
- win/lose states
- restart flow
- level-up modal flow

Still pending in this phase:

- options menu
- intro cutscene
- pause menu

### Phase 5: Port the Upgrade System

Status:

- Complete for first-pass gameplay parity

Goal:

- recover the run-building depth of the prototype

Tasks:

- move upgrade definitions into TypeScript data
- port available-upgrade selection logic
- port application of each upgrade path
- recreate the level-up choice screen

Upgrade paths to port:

- minigun
- rockets
- laser
- EMP
- health
- shield
- tractor beam
- speed

Deliverable:

- level-ups work and the main build paths are playable

Completed:

- upgrade definitions moved into TypeScript data
- upgrade choice generation works
- application logic works in the browser build
- all eight current upgrade paths exist in the web version

### Phase 6: Port Secondary Combat Systems

Status:

- Complete for first-pass gameplay parity

Goal:

- restore the signature weapons and utility systems

Tasks:

- rockets aimed toward pointer location
- laser line effect and hit resolution
- EMP radius damage pulse
- shield behavior and UI
- tractor beam gem attraction
- particle effects and feedback

Deliverable:

- the web version contains the complete core combat kit

Completed:

- rockets aimed at pointer position
- laser line attack and hit resolution
- EMP pulse behavior
- shield absorption and regeneration
- tractor beam gem attraction

Still worth improving later:

- polish effects and feedback depth
- exact timing/feel parity with Python

### Phase 7: Feel Matching and Rebalance

Status:

- Not started in a disciplined pass

Goal:

- make the web version feel intentionally good, not just equivalent on paper

Tasks:

- compare movement feel to the Python build
- retune spawn intensity
- retune weapon cadence
- retune XP curve
- verify game length pacing
- adjust for browser frame timing differences

Deliverable:

- web version is as fun or better than the Python prototype

Current focus for this phase:

- compare cooldowns and damage curves against Python
- retune movement feel
- retune spawn pressure and XP pacing

### Phase 8: Production Readiness

Status:

- Not started

Goal:

- prepare for public or semi-public sharing

Tasks:

- add page title, favicon, and version display
- test production build locally
- validate resize/fullscreen behavior
- make sure all paths are relative for itch.io
- keep output size reasonable
- prepare upload instructions

Deliverable:

- an itch.io-ready HTML5 build

### Phase 9: Default Development Cutover

Status:

- Not started

Goal:

- make the web project the main version moving forward

Tasks:

- update README to center the web workflow
- mark Python build as legacy/reference
- decide whether to archive or retain Python code
- move all new feature work to the web version

Deliverable:

- clear team alignment on the new mainline codebase

## Current Repo Snapshot

Important web files at this stage:

- `web/src/main.ts`
- `web/src/game/constants/settings.ts`
- `web/src/game/scenes/GameScene.ts`
- `web/src/game/data/enemies.ts`
- `web/src/game/data/upgrades.ts`
- `web/src/game/utils/geometry.ts`

Interpretation:

- the browser port is already beyond a bare prototype
- the scene is still doing too much, but the refactor has started
- the next work should prioritize tuning and further modularization rather than adding random new features

## Detailed Work Breakdown

### Workstream A: Project Setup

- create `web/`
- install `phaser`
- install TypeScript tooling
- configure Vite dev/build scripts
- add `.gitignore` coverage if needed
- document `npm install` and `npm run dev`

### Workstream B: Shared Data Definitions

- create TypeScript interfaces for player, enemy, bullet, rocket, laser, XP gem, upgrades
- port constants from `settings.py`
- port upgrade tables from `src/game/upgrades.py`
- centralize numeric tuning in one place

### Workstream C: Input and Motion

- WASD/arrow support
- mouse position support
- player movement model
- pause input
- menu navigation

### Workstream D: Combat

- target selection
- projectile creation
- hit checks
- death cleanup
- AoE and line-based effects

### Workstream E: Progression

- timer
- XP thresholds
- level-ups
- upgrade choices
- stat recalculation

### Workstream F: UI and Presentation

- HUD
- level-up modal
- menus
- end screen
- cutscene text
- polish effects

### Workstream G: Distribution

- production build
- itch.io zip packaging
- upload checklist

## Suggested Implementation Order

If we are executing this in a way that keeps momentum high, do it in this order:

1. Scaffold `web/` with Phaser and Vite.
2. Draw the player and enemies on a black field.
3. Add movement and spawning.
4. Add bullets and enemy deaths.
5. Add XP, leveling, and HUD.
6. Add menus and restart flow.
7. Add upgrade selection UI.
8. Add rockets, laser, EMP, shield, and tractor beam.
9. Rebalance and polish.
10. Build and upload to itch.io.

This order gets a fun browser loop in place as early as possible.

## What Not To Port Literally

We should avoid spending time on strict one-to-one recreation of:

- engine-specific `pygame` drawing patterns
- exact `pymunk` integration details unless they materially affect feel
- temporary Python-only implementation shortcuts that do not improve the web version

We should preserve:

- game feel
- progression arc
- weapon identity
- visual style
- control scheme

## Risks and Mitigations

### Risk: Physics Feel Changes During Port

Mitigation:

- use recorded reference gameplay
- compare movement in small checkpoints
- prefer simpler motion math before adding framework physics

### Risk: Migration Stalls in a Half-Ported State

Mitigation:

- work in vertical slices
- keep each milestone independently playable
- define a clear cutoff where all new features go to web only

### Risk: Browser Performance Regressions

Mitigation:

- use primitive rendering first
- keep entity update loops tight
- avoid needless object churn in hot paths
- test production builds early, not just dev mode

### Risk: Team Confusion About Which Version Is Canon

Mitigation:

- explicitly treat Python as reference during migration
- explicitly switch to web as primary after cutover
- keep README and branch naming aligned with reality

### Risk: Scope Expansion During Rewrite

Mitigation:

- do not redesign the whole game during the initial port
- only improve things when the change is clearly net-positive and low-risk
- log nice-to-haves separately

## Definition of Done for the Migration

The migration is complete when all of the following are true:

- the web version supports a full run from menu to win/lose
- the main upgrade paths work
- the game is clearly fun and stable in browser
- the project builds into an itch.io-compatible HTML5 package
- a teammate unfamiliar with Python can contribute through the web toolchain
- the README points new contributors to the web version first

## Nice-to-Haves After Migration

These are intentionally out of scope for the core migration:

- audio pass
- richer shaders and post-processing
- mobile-first controls
- save data and meta progression
- achievements
- localization
- asset pipeline expansion

## Team Workflow Recommendation

During migration:

- Python branch or folder remains reference-only except for critical fixes
- all migration work lands under `web/`
- compare behavior against the Python build at milestone boundaries

After migration:

- all new features go to the web version
- Python becomes archival or support-only

## Itch.io Release Target

Target artifact:

- zipped HTML5 build

Expected upload contents:

- `index.html`
- bundled JavaScript
- bundled CSS if applicable
- any runtime assets

Important constraints from itch.io:

- use relative paths
- make sure the build works from a static file host or static preview
- keep the production bundle compact
- test in a clean browser session before upload

Reference:

- [itch.io HTML5 upload docs](https://itch.io/docs/creators/html5)

## First Execution Step

The first concrete build step should be:

- create `web/`
- scaffold a Phaser + TypeScript + Vite app
- render a player triangle on the current playfield size

That gives us a real starting point instead of a theoretical plan.

## Final Note

This migration should be treated as a strategic move, not just a packaging exercise.

We are not only making the game playable on itch.io. We are moving the project onto a stack that is easier to share, easier to collaborate on, and better aligned with browser-first distribution.
