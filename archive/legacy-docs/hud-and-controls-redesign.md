# HUD and Controls Redesign

## Overview
Redesigning the game's HUD and control scheme to support momentum-based spacecraft combat with a focus on tactical piloting and loadout management. Inspired by Kerbal Space Program's instrumentation-focused UI design.

## Design Philosophy
- **Instrumentation over decoration**: HUD provides critical flight data for skilled piloting
- **Momentum-based space combat**: Real physics with inertia, thrust management, and tactical positioning
- **Visual clarity during combat**: Players focus on dodging enemies, not reading UI
- **Progressive complexity**: Core systems simple, utilities/weapons unlock over time

---

## HUD Layout

### Visual Style
- **Color**: Neon blue (#00D4FF or similar)
- **Opacity**: ~65% to avoid visual clutter
- **Style**: Clean, technical readout aesthetic matching neon game visuals
- **Icons**: Colored squares initially, sprite designs later

### Top Bar
```
[XP Bar]              [TIME - Large]              [Kill Count]
 (left)                 (center)                    (right)
```

- **XP Bar** (Top Left): Passive indicator, not critical during combat
- **Time** (Top Center): PRIMARY metric - larger than other HUD elements, shows survival time
- **Kill Count** (Top Right): Enemy elimination counter

### Bottom Left - Weapon Slots (6 slots)
```
[W1] [W2] [W3]
[W4] [W5] [W6]
```

Each weapon slot displays:
- Weapon icon (colored square for now, sprites later)
- Fire rate loading bar (visual cooldown indicator)
- Weapon type indicator (see Weapon System section)

### Bottom Center - Flight Instruments
```
[Boost Bar] [Thrust Control] [Mini Map]
[Health Bar] [Shield Bar]
```

- **Boost Bar**: Visual indicator for boost ability charge (utility unlock)
- **Thrust Control**: Shows current throttle level (sticky cruise control)
- **Mini Map**: Small overhead tactical view (future feature)
- **Health Bar**: Current HP
- **Shield Bar**: Current shield value with visual indicator

### Bottom Right - Utility Slots (6 slots)
```
[U1] [U2] [U3]
[U4] [U5] [U6]
```

Utility abilities, unlocks, passive bonuses displayed here.

---

## Control Scheme

### Core Movement (Momentum-Based)
- **W**: Throttle up (increases forward thrust)
- **S**: Throttle down (decreases forward thrust)
- **A**: Strafe left
- **D**: Strafe right
- **Q**: Rotate counter-clockwise
- **E**: Rotate clockwise

**Throttle System**: W/S adjust thrust level which persists (cruise control/KSP style). Ship maintains velocity based on physics/inertia.

### Utility Abilities (Meta-Progression Unlocks)
- **Space**: Boost forward (temporary speed burst)
- **A/D Double-Tap**: Hurdle/sideways jump (dodge maneuver)

### Combat
- **Mouse**: Aim for mouse-aimed weapons
- **Mouse Click**: Fire weapons (automatic for auto-target, mouse-aimed, and forward-facing)

---

## Weapon System

### Weapon Types

#### 1. Forward-Shooting Weapons
- **Behavior**: Fire in direction ship is facing
- **Control**: Requires Q/E rotation to aim
- **Balance**: High damage/fire rate to reward piloting skill
- **HUD Icon**: Directional arrow (→)
- **Examples**: Railgun, laser cannon, plasma lance

#### 2. Mouse-Aimed Weapons
- **Behavior**: Fire toward mouse cursor
- **Control**: Decoupled from ship facing
- **Balance**: Flexible aiming, requires multitasking
- **HUD Icon**: Crosshair (⊕)
- **Examples**: Turrets, guided missiles, beam weapons

#### 3. Auto-Target Weapons
- **Behavior**: Automatically target nearest/optimal enemy
- **Control**: Fire and forget
- **Balance**: Lower DPS, more forgiving
- **HUD Icon**: Target lock (◎)
- **Examples**: Homing missiles, auto-turrets, drone swarms

### Weapon HUD Requirements
- Visual fire rate indicator (loading bar) for each weapon
- Clear weapon type identification (icon/color coding)
- 6 total weapon slots available in late game
- Weapons unlock/upgrade through progression

---

## Utility System

### Core Utilities

#### Boost (Meta-Progression Unlock)
- **Function**: Temporary forward thrust burst
- **Use Case**: Escape danger, close distance, emergency repositioning
- **Control**: Spacebar
- **HUD**: Boost bar shows charge/cooldown

#### Hurdle/Sideways Jump (Meta-Progression Unlock)
- **Function**: Quick lateral dodge
- **Use Case**: Dodge through bullet patterns, skilled movement
- **Control**: Double-tap A or D
- **HUD**: Cooldown indicator in utility slots

### Future Utilities (6 slots total)
- Shields (recharge/boost)
- Temporary invulnerability
- Time slow
- Weapon overcharge
- Repair drones
- Decoys/countermeasures

---

## Meta-Progression

### Unlock Philosophy
- **Early runs**: Core movement only (throttle, strafe, rotate)
- **Players learn**: Momentum management, trajectory planning, rotation discipline
- **First unlocks**: Boost and hurdle feel *powerful* and change gameplay
- **Natural milestones**: Each unlock creates progression goal

### Progression Examples
1. **Start**: Basic movement, 1-2 weapons
2. **Unlock Boost**: Gain mobility tool, escape options
3. **Unlock Hurdle**: Skilled dodging, pattern navigation
4. **Unlock Forward Weapons**: Rotation becomes critical
5. **Unlock Auto-Target**: Build variety options
6. **Expand Slots**: 6 weapons + 6 utilities in late game

---

## Visual Design

### Shield System
- **HUD Display**: Shield bar bottom center (separate from HP)
- **Player Visual**: Visual shield indicator around player ship
- **Behavior**: Absorbs damage before HP, regenerates over time

### Fire Rate Visualization
- **Current**: Text descriptor (removed)
- **New**: Loading bar under each weapon slot
- **Benefit**: At-a-glance cooldown visibility during combat

### Upgrade Screen Improvements
- **Layout**: Vertical text layout (not horizontal) to fit more text
- **Interaction**: Clickable upgrade boxes OR 0.5s grace period after closing
- **UX Goal**: Prevent "player unready" feeling when returning to combat

---

## Implementation Priority

### Phase 1: Core HUD Restructure
1. Implement new HUD layout (top bar, bottom left/center/right)
2. Add neon blue styling at 65% opacity
3. Move existing elements (HP, shields, XP, time, kills) to new positions
4. Make time display larger/prominent

### Phase 2: Weapon System
1. Add weapon type indicators (forward/mouse/auto icons)
2. Implement fire rate loading bars for 6 weapon slots
3. Add colored square placeholders for weapon icons

### Phase 3: Flight Instruments
1. Implement throttle control display
2. Add boost bar UI (even if boost not yet functional)
3. Create shield bar separate from HP

### Phase 4: Utility Slots
1. Add 6 utility slot containers (bottom right)
2. Implement cooldown/charge indicators

### Phase 5: Control Scheme
1. Implement W/S throttle up/down (sticky)
2. Implement Q/E rotation
3. A/D remains strafe
4. Add boost (Space) - requires unlock system
5. Add hurdle (A/D double-tap) - requires unlock system

### Phase 6: Polish
1. Replace colored squares with sprite icons
2. Implement mini map (future)
3. Add animations/transitions to HUD elements
4. Sound design for throttle changes, boosts, etc.

---

## Open Questions

### Control Scheme
- **Throttle behavior**: Should S throttle down to zero and then reverse? Or is reverse a separate control?
- **Rotation sensitivity**: How fast should Q/E rotate the ship?
- **Boost physics**: Instant velocity change or acceleration over time?
- **Hurdle cooldown**: How long between uses? Per-direction or shared cooldown?

### Weapon System
- **Weapon switching**: Can player toggle weapons on/off, or all fire simultaneously?
- **Ammo system**: Infinite ammo or reload mechanic?
- **Weapon upgrades**: Linear upgrades or branching paths?

### Meta-Progression
- **Unlock currency**: What do players spend to unlock boost/hurdle?
- **Permanent upgrades**: What carries between runs vs. temporary?
- **Unlock order**: Player choice or fixed progression tree?

---

## Notes
- Fixed issues (as of 2026-02-07):
  - ✅ Shield integration into HUD
  - ✅ LVL 1 text overflow in XP bar
  - ✅ Upgrade text layout (vertical stacking)
  - ✅ Upgrade box UX (clickable or grace period)
