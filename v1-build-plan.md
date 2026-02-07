# Create the project plan markdown file
plan_content = """# Neon Survivors - Development Plan

## Project Overview
A Geometry Wars + Vampire Survivors hybrid where you pilot a drone into an enemy stronghold with 15 minutes to cause maximum damage.

**Story Hook:** "We've gotten your drone into the enemy stronghold. You only have 15 minutes to take them out. Get moving!"

---

## PHASE 1: Core Loop Completion
**Goal:** Get it playable end-to-end

- [x] XP gem drops on enemy death (green/cyan colored)
- [x] XP collection + level counter
- [x] Basic level-up screen (pause, show 3 options, resume)
- [x] Upgrade data structure (weapon levels, stats per level)
- [x] Apply upgrade logic (increase fire rate, unlock new weapon, etc)
- [x] Win condition at 0:00 (basic "Mission Complete" screen with stats)

**Deliverable:** You can play a full 15min run, level up, get stronger, and see an end screen.

---

## PHASE 2: Visual Polish
**Goal:** Make it feel good

- [x] Change player to triangle (blue)
- [x] Change enemies to red
- [x] Infinite scrolling background (grid lines or particle field that wraps)
- [x] Enemy spawn off-screen (check player position, spawn outside view radius)
- [x] Particle effects on death (both player and enemy)
- [x] Enemies fragment/explode instead of vanishing
- [x] Muzzle flash / bullet trails
- [x] Screen shake on big hits

**Deliverable:** Game feels juicy and satisfying to play.

---

## PHASE 3: Enemy Variety
**Goal:** Progression depth

### Polygon-based Enemy Scaling
- [x] Circle (1) = weakest, fastest
- [x] Triangle (3) = medium
- [x] Square (4) = tougher
- [x] Pentagon (5) = mini-boss tier
- [x] Hexagon+ (6-8) = rare heavy units

### Progression
- [x] Enemy stats scale with shape (HP, speed, damage, XP value)
- [x] Spawn rate increases over time
- [x] Wave composition changes (more complex shapes in late game)
- [ ] Optional: Boss variants (different color, special behavior)

**Deliverable:** Enemy encounters feel varied and escalate naturally.

---

## PHASE 4: Weapon Systems
**Goal:** Implement all 7 upgrade paths

### Minigun (refine existing)
- [ ] Slow down base fire rate (0.4s start?)
- [ ] Auto-targets nearest enemy
- [ ] Levels: fire rate + damage increases

### Rockets
- [ ] Slower fire (2-3s cooldown)
- [ ] Aims at mouse position
- [ ] Splash damage radius on impact
- [ ] Levels: damage, splash radius, fire rate

### Laser
- [ ] Very slow recharge (5-8s)
- [ ] Pierces all enemies in line
- [ ] Aims at mouse
- [ ] Levels: damage, pierce depth, cooldown reduction

### AoE EMP Field
- [ ] Constant pulse around player
- [ ] Damage tick rate (every 0.5s?)
- [ ] Visual ring/pulse effect
- [ ] Levels: damage, radius, tick rate

### Health Upgrades
- [ ] Increase max HP (100 → 125 → 150, etc)
- [ ] Instant heal on pickup
- [ ] Multi-level (5-6 tiers)

### Shield System
- [ ] Separate shield bar (recharges over time)
- [ ] Absorbs damage before HP
- [ ] Ignores collision damage (only blocks projectiles if enemies shoot)
- [ ] Levels: max shield, regen rate, regen delay
- [ ] Visual indicator (blue ring around player when active?)

### Tractor Beam (Utility)
- [ ] Starts at level 0: 0 pickup radius (must collide with XP gems)
- [ ] Level 1+: Magnetic pull on XP gems within radius
- [ ] Each level increases pickup radius progressively
- [ ] Levels: pickup radius expansion (e.g., 0 → 50 → 100 → 150 → 200 → 250 pixels)
- [ ] Visual indicator: subtle circular pulse when active (level 1+)
- [ ] Quality of life upgrade that becomes more valuable in chaotic late game

**Deliverable:** All 7 upgrade paths functional with 5 levels each.

---

## PHASE 5: Menus & UX
**Goal:** Polish the experience

- [ ] Start menu (Title, Start, Options, Quit)
- [ ] Options: Window size (720p, 1080p, fullscreen toggle)
- [ ] Intro lore text on Start press
- [ ] Pause menu (ESC to pause mid-game)
- [ ] End screen improvements (stats breakdown, retry button)
- [ ] Level-up UI polish (show current vs next level stats)

**Deliverable:** Game has proper flow from launch to completion.

---

## PHASE 6: Balance & Tuning
**Goal:** Make it fun

### Playtest & Adjust
- [ ] Enemy HP scaling
- [ ] Spawn rates (early game too easy/hard?)
- [ ] XP curve (leveling too fast/slow?)
- [ ] Weapon damage values
- [ ] Shield recharge timing
- [ ] 15min game length feel (not too grindy, not too short)

**Deliverable:** Game is balanced and feels good for a full run.

---

## PHASE 7: Ship It
**Goal:** Package for friends

- [ ] Add credits/version number
- [ ] Create standalone executable (PyInstaller or similar)
- [ ] Write simple README (controls, goal, lore)
- [ ] Test on another machine
- [ ] Send to friends!
- [ ] Collect feedback for v2

**Deliverable:** Playable game file + instructions ready to share.

---

## Nice-to-haves (If Time/Interest)
- Sound effects (pew pew, explosions, level-up chime)
- Background music
- Leaderboard (local high scores)
- Multiple difficulty modes
- Unlockable color schemes
- Boss rush mode after 15min
- Replay system

---

## Design Notes

### Visual Style
- Neon geometric shapes on black background
- Player: Blue triangle
- Enemies: Red polygons (circle/triangle/square/pentagon/hexagon)
- XP gems: Green/cyan
- Bullets: Yellow (minigun), Orange (rockets), Cyan (laser)

### Controls
- WASD/Arrow keys: Movement
- Mouse position: Aiming for rockets/laser
- ESC: Pause

### Core Stats to Track
- Enemies destroyed
- Max level reached
- Upgrades collected
- Time survived
- Damage dealt
"""
