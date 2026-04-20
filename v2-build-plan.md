# CLONE PROTOCOL - V2 BUILD PLAN
## From Survivor to Tactical: The Transition

---

## Overview

This document maps the path from the current v1 prototype (Vampire Survivors-style horde game) to the v2 design (tactical depletion combat with ship fitting). The existing codebase has strong foundations - physics, rendering, entity systems - that carry forward. The core loop, progression, and combat philosophy need to change.

---

## What We Have (v1 Prototype Audit)

### Carries Forward (Keep)
| System | Files | Notes |
|--------|-------|-------|
| Pymunk physics engine | `physics.py` | Core of the game. Newtonian movement works. |
| Pygame rendering | `world.py`, entities | Drawing, particles, screen shake - all good |
| Ship controls | `entities/player.py` | Throttle, rotation, strafe, boost, hurdle |
| Entity architecture | `entities/` | Player, Enemy, Bullet, Particle base classes |
| Collision system | `systems/collisions.py` | Pymunk collision handlers, needs modification |
| Background/stars | `world.py` | Procedural starfield, nebulae, grid |
| Debug overlay | `debug_overlay.py` | F3 tuning tools - invaluable for balancing |
| Settings framework | `settings.py` | Resolution, FPS, tuning values |
| Intro sequence | Existing | Can be repurposed for deployment briefing |

### Needs Rework (Modify Heavily)
| System | Files | What Changes |
|--------|-------|-------------|
| Enemy spawning | `systems/spawner.py` | From horde waves to multi-vector timed approaches |
| Combat system | `systems/combat.py` | From auto-fire to manual, add ammo tracking |
| Weapon entities | `entities/bullet.py`, etc. | Add ammo counts, remove infinite firing |
| Player entity | `entities/player.py` | Add fuel consumption, ammo state, fitting data |
| HUD | `world.py` (rendering) | From XP/level to ammo/fuel/threat board |
| Enemy AI | `entities/enemy.py` | From "home toward player" to tactical behaviors |

### Remove Entirely
| System | Files | Why |
|--------|-------|-----|
| XP/leveling | `systems/xp.py` | No in-run progression |
| Upgrade system | `systems/upgrades.py` | Replaced by ship fitting |
| XP gems/pickups | `entities/xp_gem.py` | No pickups during runs |
| Mining laser auto-lock | `systems/combat.py` | Manual weapons only |
| Shield regeneration | Player entity | Hull only, no regen |
| Tractor beam | Upgrade system | No pickups to attract |

### Build New
| System | Priority | Description |
|--------|----------|-------------|
| Ship Fitting Screen | P0 | Pre-run loadout selection |
| Ammo System | P0 | Finite ammo per weapon, depletion tracking |
| Fuel System | P0 | Fuel consumption on thrust, empty = ballistic |
| Threat Timeline | P0 | Enemy approach ETAs, bearing indicators |
| Weapon Arcs | P1 | Forward/side/rear mounting, gimbal ranges |
| Module Database | P1 | JSON-defined weapons, systems, stats |
| Meta Progression | P1 | Data (GB) tracking, module unlocks, persistence |
| Debrief Screen | P1 | Post-run stats, resource expenditure breakdown |
| Threat Board HUD | P1 | Tab-toggle tactical overlay |
| Save System | P2 | JSON save/load for unlocks and narrative |
| Terminal/Logs | P2 | Narrative progression system |
| AI Dialogue | P2 | Context-sensitive callouts |

---

## Build Phases

### PHASE 0: Foundation Strip (Days 1-3)
**Goal:** Remove v1 systems cleanly without breaking what we keep.

**Tasks:**
- [ ] Create `v2` branch from current main
- [ ] Remove XP gem entity and spawning
- [ ] Remove upgrade selection system and UI
- [ ] Remove auto-fire from all weapons
- [ ] Remove mining laser auto-lock behavior
- [ ] Remove shield regeneration (keep hull damage)
- [ ] Remove tractor beam system
- [ ] Remove level-up pause/selection flow
- [ ] Strip XP bar and level counter from HUD
- [ ] Verify: Ship still flies, enemies still spawn, collisions still work
- [ ] Verify: No crashes from removed systems

**End State:** A stripped-down game where you fly a ship, enemies approach, you can collide with them, but there's no shooting, no progression, no pickups. A blank canvas with working physics.

---

### PHASE 1: Core Combat Rework (Week 1)

#### 1A: Manual Weapons with Ammo (Days 1-2)

**Implement finite ammo system:**
```python
class WeaponState:
    def __init__(self, weapon_data):
        self.name = weapon_data['name']
        self.ammo_max = weapon_data['ammo']
        self.ammo_current = weapon_data['ammo']
        self.damage = weapon_data['damage']
        self.fire_rate = weapon_data['fire_rate']
        self.cooldown_timer = 0
        self.mounting = weapon_data['mounting']  # 'forward', 'side', 'rear'

    @property
    def is_empty(self):
        return self.ammo_current <= 0

    def fire(self):
        if self.is_empty or self.cooldown_timer > 0:
            return False
        self.ammo_current -= 1
        self.cooldown_timer = 1.0 / self.fire_rate
        return True
```

**Tasks:**
- [ ] Create `WeaponState` class with ammo tracking
- [ ] Implement manual fire (left click = primary, right click = secondary)
- [ ] Weapons only fire when player clicks (remove auto-fire loop)
- [ ] Add ammo counter to HUD for each equipped weapon
- [ ] PDC fires in ship's forward direction with +-15° gimbal
- [ ] Play distinct "empty click" sound when ammo depleted
- [ ] Weapon selection with number keys (1-5)

#### 1B: Fuel System (Days 2-3)

**Tasks:**
- [ ] Add `fuel` property to player entity
- [ ] Main thrust consumes fuel proportional to throttle
- [ ] RCS (strafe) consumes fuel at reduced rate (0.3x)
- [ ] Boost consumes fuel at high rate (10x)
- [ ] When fuel = 0: no thrust, no RCS, no boost. Player drifts on current vector.
- [ ] Fuel gauge on HUD (prominent, always visible)
- [ ] Warning sound at 25% fuel
- [ ] Engine audio cuts out at 0% fuel (silence = dread)
- [ ] Heavier ship mass = higher fuel consumption rate

#### 1C: Enemy Rework - Phase 1 (Days 3-5)

**Change spawner from horde to tactical:**
- [ ] Max 8-10 enemies on screen simultaneously
- [ ] Enemies spawn from screen edges at specific bearings (not just random)
- [ ] Each enemy has an approach time (30-120 seconds from spawn to contact range)
- [ ] Enemies approach from randomized vectors (not all toward player)
- [ ] Remove time-based HP/speed scaling (each enemy type has fixed stats)
- [ ] Spawn schedule based on elapsed time:
  - 0-3 min: 1 enemy every 30s, single direction
  - 3-7 min: 1 enemy every 20s, two directions
  - 7-12 min: 1 enemy every 15s, three+ directions, mixed types
  - 12-15 min: 1 enemy every 10s, all directions, heavy types appear

#### 1D: Threat Visibility (Days 4-5)

**Players must be able to see what's coming:**
- [ ] Bearing indicators on screen edges (arrows showing direction of off-screen threats)
- [ ] Distance/ETA display next to each bearing indicator
- [ ] Threat type icon (triangle for fighter, pentagon for frigate, etc.)
- [ ] Color coding: white (distant), yellow (approaching), red (imminent)
- [ ] Tab-toggle threat board (text list of all active threats with ETAs)

**Week 1 Milestone:** You can fly, manually shoot enemies with finite ammo, run out of fuel and drift helplessly, and see threats approaching from multiple vectors with visible timelines. The core "numbers go down" feel should be testable.

---

### PHASE 2: Ship Fitting (Week 2)

#### 2A: Module Data System (Days 1-2)

**Define all modules in JSON:**
```json
{
  "modules": {
    "pdc_array": {
      "name": "PDC Array",
      "type": "weapon",
      "slot_size": "S",
      "mounting": "forward",
      "mass": 120,
      "stats": {
        "damage": 5,
        "fire_rate": 10,
        "ammo": 1200
      },
      "unlock_cost": 0,
      "tier": 1
    },
    "railgun_mk1": {
      "name": "Railgun Mk-I",
      "type": "weapon",
      "slot_size": "M",
      "mounting": "forward",
      "mass": 200,
      "stats": {
        "damage": 150,
        "fire_rate": 0.5,
        "ammo": 8,
        "charge_time": 1.5
      },
      "unlock_cost": 10,
      "tier": 1
    },
    "light_armor": {
      "name": "Light Armor",
      "type": "system",
      "slot_size": "S",
      "mass": 400,
      "stats": {
        "hull_bonus": 200
      },
      "unlock_cost": 5,
      "tier": 1
    }
  }
}
```

**Tasks:**
- [ ] Create `modules.json` with initial module definitions (5 weapons, 4 systems)
- [ ] Create `ships.json` with ship definitions (slot layouts, base stats)
- [ ] Module loader that reads JSON and creates module objects
- [ ] Ship loader that reads JSON and creates ship templates

#### 2B: Fitting Screen (Days 2-4)

**Tasks:**
- [ ] New game state: FITTING (between MENU and GAMEPLAY)
- [ ] Display current ship with slot layout
- [ ] Show available modules (unlocked only) that fit each slot
- [ ] Click slot -> show compatible modules -> click module to equip
- [ ] Mass budget display (current / max) with warning when near limit
- [ ] Calculated stats display (total hull, total fuel, weapon summary)
- [ ] "Deploy" button that starts the run with fitted loadout
- [ ] Ship swap button (if multiple ships unlocked)
- [ ] Start with: 1 ship (Prospector), PDC Array, Light Armor, Standard Fuel Tank

#### 2C: Deploy with Loadout (Days 4-5)

**Connect fitting to gameplay:**
- [ ] Player entity reads loadout from fitting data
- [ ] Weapons initialized with ammo from module stats
- [ ] Fuel initialized from ship base + fuel tank modules
- [ ] Hull initialized from ship base + armor modules
- [ ] Ship mass calculated from base mass + all module masses
- [ ] Mass affects fuel consumption rate (heavier = thirstier)
- [ ] Mass affects acceleration (heavier = slower to change vector)

**Week 2 Milestone:** You can select modules in a fitting screen, deploy with that loadout, and the loadout determines your in-run capabilities. The hangar-to-combat pipeline works.

---

### PHASE 3: Meta Progression (Week 3)

#### 3A: Data (GB) Economy (Days 1-2)

**Tasks:**
- [ ] Track elapsed time during run (existing timer)
- [ ] Calculate data earned: 1 GB/minute survival + kill bonuses + extraction bonus
- [ ] Debrief screen after death/extraction showing:
  - Survival time
  - Threats neutralized
  - Resource expenditure (ammo used, fuel consumed, hull damaged)
  - Data earned breakdown
- [ ] Persistent data storage (save to file between sessions)

#### 3B: Module Unlocks (Days 2-3)

**Tasks:**
- [ ] Data archive screen showing all modules (locked and unlocked)
- [ ] Spend GB to unlock modules
- [ ] Unlocked modules appear in fitting screen
- [ ] Tier gating: Tier 2 modules visible but locked until enough GB accumulated
- [ ] Initial unlock tree (10-15 modules across tiers 1-2)

#### 3C: Run Tracking (Days 3-4)

**Tasks:**
- [ ] Track total runs (clone number)
- [ ] Track cumulative stats (total kills, total time, total fuel burned, etc.)
- [ ] Clone number displayed in HUD and debrief
- [ ] Save/load player progress between sessions

#### 3D: Extraction Mechanic (Days 4-5)

**Tasks:**
- [ ] At 15:00, extraction becomes available
- [ ] UI indicator: "EXTRACTION AVAILABLE - Press [key] to extract"
- [ ] Extracting takes 5 seconds (charging animation, vulnerable)
- [ ] Successful extraction grants bonus data (3 GB)
- [ ] Can choose to stay past 15:00 (more data per minute, but resources are gone)

**Week 3 Milestone:** Complete loop: fit ship -> deploy -> fight -> extract/die -> earn data -> unlock modules -> fit better ship -> repeat. The roguelite meta-loop is functional.

---

### PHASE 4: Combat Polish & Enemy Variety (Week 4)

#### 4A: Weapon Mounting System (Days 1-2)

**Tasks:**
- [ ] Forward weapons: fire in ship facing direction, +-15° gimbal
- [ ] Side weapons: fire perpendicular to facing, +-30° gimbal
- [ ] Rear weapons: fire behind ship
- [ ] Turret weapons: track mouse cursor independently, slow rotation
- [ ] Visual: weapon fire originates from mount position on ship sprite

#### 4B: Enemy Type Variety (Days 2-3)

**Implement 4 enemy types with distinct behaviors:**
- [ ] **Scout (Triangle):** Fast, direct approach, low HP, rams or close-range fire
- [ ] **Skirmisher (Pentagon):** Medium speed, maintains distance, fires projectiles
- [ ] **Heavy (Hexagon):** Slow approach, high HP, spawns escort fighters
- [ ] **Cruiser (Octagon):** Very slow, area denial, multiple weapon systems

**Each enemy needs:**
- [ ] Unique movement AI (not just "move toward player")
- [ ] Appropriate HP/damage values
- [ ] Correct resource cost to kill (PDC rounds, railgun slugs, etc.)
- [ ] Visual distinction (shape, color, size)

#### 4C: Weapon Variety (Days 3-4)

**Implement remaining weapon types:**
- [ ] Railgun: Forward-only, charge time, high damage, pierces first target
- [ ] Missile Launcher: Side-mounted, seeking projectile, can be shot down
- [ ] Beam Laser: Forward, sustained damage while held, drains ammo per second
- [ ] (Torpedoes and advanced variants saved for later phases)

#### 4D: Feel Pass (Day 5)

**The most important day of development:**
- [ ] Tune ammo counts: Are players making interesting decisions about when to shoot?
- [ ] Tune fuel rates: Are burns meaningful decisions without being frustrating?
- [ ] Tune enemy HP: Do enemies feel like problems to solve, not bags to empty?
- [ ] Tune spawn timing: Does pressure cascade naturally?
- [ ] Tune threat board: Is information clear and useful?
- [ ] Screen shake on weapon fire (satisfying)
- [ ] Screen shake on hull hits (impactful)
- [ ] Particle effects on weapon fire and impacts
- [ ] Empty magazine click sound (dread)
- [ ] Fuel empty engine cutout (terrifying silence)

**Week 4 Milestone:** The game FEELS right. Combat is tense, tactical, and satisfying. Resources create meaningful decisions. Multiple enemy types create overlapping tactical problems. This is the "is this game fun?" checkpoint.

---

## Post-Phase 4: Content & Polish Plan

### Weeks 5-8: Content Expansion
- Additional ships (Cutter, Ironclad)
- Ship handling differences
- Weapon variants (Mk-II versions)
- Defensive systems (armor, countermeasures, fuel tanks)
- First boss (The Behemoth)
- Saved loadout presets
- More modules for fitting variety

### Weeks 9-12: Narrative & Factions
- Terminal log system
- AI dialogue (context-sensitive: ammo warnings, fuel warnings, threat callouts)
- UN faction unlock at Run 30
- UN ships and faction-specific modules
- Second boss (The Bastion)
- Secret ending framework (18-22 minute sequence)

### Weeks 13-16: Mars & Polish
- Mars faction unlock at Run 100
- Mars ships and experimental modules
- Third boss (The Sovereign)
- New Game+ mode
- Full audio pass
- UI polish pass

### Weeks 17-20: Audio, Balance & Ship
- Music composition and adaptive system
- Sound effects pass (especially resource warning sounds)
- Full balance pass
- Playtest and iterate
- Steam/itch.io page, trailer, launch

---

## Key Decision Points

### Decision 1: Does the core loop feel right? (End of Week 1)
**Test:** Play for 15 minutes with manual weapons, finite ammo, finite fuel.
**Ask:** "Am I making interesting decisions, or am I just frustrated?"
**If no:** Adjust ammo/fuel generosity. The problem is tuning, not design.

### Decision 2: Does the fitting screen add value? (End of Week 2)
**Test:** Fit two different loadouts. Play runs with each.
**Ask:** "Did the loadout choice change how I played?"
**If no:** Loadout options need more differentiation. More extreme tradeoffs.

### Decision 3: Is the meta progression compelling? (End of Week 3)
**Test:** Play 5 runs. Unlock 2-3 new modules.
**Ask:** "Am I excited to try my new modules? Do I want to do another run?"
**If no:** Unlock pacing too slow, or new modules aren't exciting enough.

### Decision 4: Does cascading pressure work? (End of Week 4)
**Test:** Play to minute 12-15. Multiple threat vectors active.
**Ask:** "Do I feel 'slow but rushed'? Am I triaging, not twitching?"
**If no:** Enemy approach times need tuning. Possibly too fast or too many at once.

---

## Technical Notes

### Architecture Changes

**New game states:**
```
MENU -> FITTING -> GAMEPLAY -> DEBRIEF -> FITTING (loop)
                                      -> DATA_ARCHIVE (unlock modules)
                                      -> TERMINAL (read logs)
```

**New data flow:**
```
modules.json ──→ Fitting Screen ──→ Player Loadout ──→ Gameplay
                      ↑                                    │
                      │                                    ↓
                 Data Archive ←── Save File ←──── Debrief Screen
                      │                              │
                      └─── Unlock Modules ←──── Data (GB) Earned
```

**New entity relationships:**
```
Player
├── WeaponState[] (one per equipped weapon)
│   ├── ammo_current / ammo_max
│   ├── cooldown_timer
│   └── mounting (forward/side/rear)
├── fuel (float, depletes with thrust)
├── hull (float, no regen)
└── fitting_data (reference to loadout config)

Enemy
├── approach_vector (bearing from player)
├── approach_speed
├── eta (calculated distance / speed)
├── behavior_state (approaching / engaging / repositioning)
└── threat_level (calculated from type + distance)

ThreatBoard
├── active_threats[] (sorted by ETA)
├── bearing_indicators[] (screen-edge arrows)
└── threat_timeline_display
```

### File Structure (New/Modified)

```
src/game/
├── data/
│   ├── modules.json          # NEW: All module definitions
│   ├── ships.json             # NEW: All ship definitions
│   └── save_data.json         # NEW: Player progress (generated)
├── entities/
│   ├── player.py              # MODIFY: Add fuel, ammo, fitting
│   ├── enemy.py               # MODIFY: Tactical AI, approach vectors
│   ├── bullet.py              # MODIFY: Weapon-specific projectiles
│   └── ...
├── systems/
│   ├── combat.py              # MODIFY: Manual fire, weapon mounting
│   ├── spawner.py             # MODIFY: Multi-vector timed spawning
│   ├── collisions.py          # MODIFY: Remove XP drops, adjust damage
│   ├── threat_board.py        # NEW: Threat tracking and display
│   ├── fitting.py             # NEW: Ship fitting logic
│   ├── progression.py         # MODIFY: Data earning, extraction
│   └── save_system.py         # NEW: Save/load
├── screens/
│   ├── fitting_screen.py      # NEW: Pre-run fitting UI
│   ├── debrief_screen.py      # NEW: Post-run stats
│   ├── data_archive_screen.py # NEW: Module unlock shop
│   └── terminal_screen.py     # NEW: Narrative logs (later phase)
├── world.py                   # MODIFY: New game state flow
├── settings.py                # MODIFY: New tuning values
└── debug_overlay.py           # MODIFY: Add ammo/fuel debug tools
```

---

## Risk Mitigation

### Risk: "Numbers going down feels bad"
**Mitigation:** Generous starting resources. The first 5 minutes should feel powerful. Depletion pressure builds gradually. Early runs should end with 20-30% resources remaining. Only experienced players push to the edge.

### Risk: "Fitting screen is overwhelming"
**Mitigation:** Start with only 3-4 modules available. Unlock more gradually. First ship has obvious default loadout. Tooltip everything. Show mass budget prominently.

### Risk: "Manual aiming is too hard"
**Mitigation:** PDCs have forgiving gimbal range (+-15°). Fire rate is high enough that missing individual rounds doesn't matter. Gimbal auto-tracks within range. Only railgun requires precise aim.

### Risk: "Not enough enemies feels empty"
**Mitigation:** Each enemy is visually prominent and mechanically interesting. Threat board creates tension even when enemies are far away. The pressure is anticipatory - you see what's coming and worry about it.

### Risk: "Fuel anxiety prevents fun"
**Mitigation:** Fuel is generous enough for 15+ minutes of moderate flying. Only aggressive burning (constant thrust, lots of boosting) depletes quickly. Running out of fuel is a late-game consequence of earlier decisions, not an early-game punishment.

---

## Success Criteria

**Week 1 (Core Combat):**
"I manually shot an enemy, watched my ammo counter go down, and felt the weight of that decision."

**Week 2 (Ship Fitting):**
"I agonized over whether to bring the railgun or extra PDC ammo, and the choice mattered."

**Week 3 (Meta Progression):**
"I unlocked a new weapon, immediately went to the fitting screen to try it, and started a new run."

**Week 4 (Full Loop):**
"At minute 12, I had 3 threats from different directions, 30% ammo, 15% fuel, and I said 'I have time... I have time...' and then I didn't."

---

**Let's build it.**
