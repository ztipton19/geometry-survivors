# Neon Survivors V2 - Feature Expansion Plan

## Overview
V2 takes the solid foundation of V1 and adds depth through progression systems, content variety, and replayability mechanics. Focus is on keeping players engaged past the initial clear and adding strategic decision-making.

---

## Core Design Problems V2 Solves

### Problem 1: Maxing Out Early (Done at 10min)
**Solutions:**
- Weapon synergies/combos
- Prestige/mastery levels
- Meta-upgrades
- Mutation system

### Problem 2: Lack of Long-term Goals
**Solutions:**
- Persistent unlocks between runs
- Challenge modes
- Achievement system
- Stats tracking

### Problem 3: Repetitive Gameplay
**Solutions:**
- Enemy variety and behaviors
- Boss waves
- Dynamic events
- Multiple mission types

---

## V2 Feature Categories

---

## 1. UPGRADE SYSTEM OVERHAUL

### Weapon Synergies/Combos
When you max two weapons, unlock a combined super-weapon:

**Synergy Examples:**
- **Minigun + Laser** = "Gatling Beam" - Rapid-fire piercing shots
- **Rockets + EMP** = "EMP Missiles" - AOE stun on impact
- **Minigun + Rockets** = "Cluster Munitions" - Bullets occasionally spawn mini-rockets
- **Laser + EMP** = "Chain Lightning" - Laser bounces between enemies
- **Rockets + Health** = "Vampiric Warheads" - Heal on kill
- **Shield + EMP** = "Pulse Shield" - Shield pulses damage when recharged

**Implementation:**
- Unlock when both weapons reach level 5
- Shows special notification
- Visually distinct (different color/effect)
- Doesn't take an upgrade slot - passive bonus

---

### Prestige/Mastery Levels
After reaching level 5, weapons continue improving:

**Level 6+:** Smaller incremental bonuses
- +5% damage per level (instead of big jumps)
- +2% fire rate
- Visual indicator (gold border, star rating)

**Cap at level 10** to prevent infinite scaling

---

### Meta-Upgrades
New upgrade category affecting ALL weapons:

**Examples:**
- **Overclocking** - All weapons fire 10% faster
- **Targeting Matrix** - All projectiles track slightly
- **Critical Systems** - 15% chance for 2x damage
- **Power Surge** - All weapons deal 20% more damage, drain shields over time
- **Efficient Cooling** - All cooldowns 15% faster

**Appears in level-up pool** like regular upgrades

---

### Mutation System
Rare, powerful random modifiers:

**Mutation Examples:**
- **Triple Shot** - Fire 3 projectiles instead of 1 (33% damage each)
- **Time Dilation** - Slow enemies briefly on kill
- **Vampiric** - Heal 1 HP per 10 kills
- **Explosive Finale** - Enemies explode on death (small AOE)
- **Mag-Pull** - XP gems pulled toward you from farther away
- **Ghost Drone** - Leave afterimage that also fires (50% damage)

**Spawn Rate:** 5% chance per level-up, replaces one normal option

---

### Additional Upgrade Paths
Expand beyond the current 6:

**New Categories:**
- **Movement Speed** - Faster base movement (5 levels)
- **Dash Ability** - Short cooldown teleport/dash (unlocks at level 1, upgrades reduce cooldown)
- **Bullet Reflection** - Chance to reflect enemy projectiles
- **Magnetic Field** - Increased XP collection radius
- **Armor Plating** - Reduce damage taken by %

---

## 2. ENEMY VARIETY & BEHAVIORS

### New Enemy Types (Beyond Geometry)

#### Turrets
- **Behavior:** Stationary, shoot projectiles at player
- **Visual:** Hexagon with rotating gun barrel
- **Stats:** High HP, slow fire rate, dangerous at range
- **Spawn:** Appears in clusters, late-game

#### Chargers
- **Behavior:** Circle player, then telegraph and dash attack
- **Visual:** Triangle with trail particles
- **Stats:** Fast movement, high damage, low HP
- **Tell:** Flashes red 1 second before charging

#### Splitters
- **Behavior:** Break into 2-3 smaller enemies on death
- **Visual:** Large pentagon → smaller triangles
- **Stats:** Medium HP, creates chaos
- **Spawn:** Mid-game onwards

#### Shielded Units
- **Behavior:** Take reduced damage from certain weapon types
- **Visual:** Square with rotating shield ring
- **Stats:** High HP, slow, immune to minigun (must use heavy weapons)
- **Counter:** Rockets/Laser deal full damage

#### Swarmers
- **Behavior:** Weak individually, spawn in packs of 10-20
- **Visual:** Tiny circles, fast-moving
- **Stats:** 1-2 shot kills, but overwhelming in numbers
- **Spawn:** Wave-based (every 2-3 minutes)

---

### Elite Variants
Glowing/gold versions of existing enemies:

**Stats:** 3x HP, 2x damage, 1.5x speed
**Visual:** Bright glow, different color (gold/white)
**Drops:** Guaranteed rare upgrade or mutation
**Spawn Rate:** 1% of normal enemies

---

### Boss Waves
Every 3-5 minutes, major enemy spawns:

**Boss Examples:**

#### "Command Node" (Hexagon Boss)
- **Phase 1:** Stationary, spawns adds, shoots spread pattern
- **Phase 2 (50% HP):** Shield drops, starts moving, faster fire rate
- **Visual:** Massive hexagon, pulsing core

#### "Assault Fabricator" (Pentagon Boss)
- **Behavior:** Spawns weaker enemies constantly
- **Mechanic:** Kill spawner to stop adds
- **Visual:** Pentagon with assembly arm animations

#### "Interceptor Swarm" (Multi-boss)
- **Behavior:** 5 fast triangles in formation
- **Mechanic:** Must kill all 5 or they respawn
- **Visual:** Coordinated movement pattern

**Boss Rewards:** 
- Large XP burst
- Guaranteed level-up
- Mutation chance increased to 50%

---

### Environmental Enemies

#### Mines
- **Behavior:** Float slowly, explode on contact or after time
- **Visual:** Pulsing circle with countdown
- **Damage:** AOE blast

#### Laser Grids
- **Behavior:** Sweep across screen, predictable pattern
- **Visual:** Red warning lines before activation
- **Damage:** High damage if touched

#### Explosive Barrels
- **Behavior:** Static objects, explode when shot
- **Visual:** Red/orange barrel
- **Use:** Damage enemies in blast radius (strategy element)

---

## 3. MAP & ARENA CHANGES

### Objective Markers (Optional Hard Mode)
- **"Destroy 3 Data Cores"** - Marked locations on map, defend while destroying
- **"Assassinate Commander"** - Specific boss target appears mid-game
- **"Survive Lockdown"** - Arena shrinks over time

### Environmental Hazards
- **Laser Walls** - Sweep through arena periodically
- **Electric Fields** - Damage zones that pulse on/off
- **Explosive Barrels** - Shoot to damage nearby enemies
- **Turret Nests** - Static hazards in corners

### Safe Zones
- **Shield Generators** - Temporary cover, destructible by enemies
- **Repair Stations** - Stand still to heal slowly (risky mid-combat)

### Sector System (Visual Variety)
Different visual zones with themed enemy sets:

**Sectors:**
- **Server Room** - Grid floor, lots of turrets
- **Assembly Line** - Conveyor belt effect, swarmers
- **Power Core** - Electric arcs, shielded units
- **Hangar Bay** - Open space, chargers

**Implementation:** Change background color/pattern, spawn specific enemy types

---

### Dynamic Events
Mid-mission announcements/changes:

**Examples:**
- **"Reinforcements arriving in 30 seconds!"** - Warning, then massive spawn wave
- **"Power fluctuation detected"** - Screen flickers, all enemies briefly stunned
- **"Emergency lockdown initiated"** - Arena temporarily shrinks
- **"Self-destruct sequence active"** - Final 2 minutes, enemies go berserk

---

## 4. PROGRESSION META-GAME

### Persistent Unlocks Between Runs

#### New Starting Weapons
- **Default:** Start with Minigun
- **Unlock:** Start with Laser (after 50 laser kills total)
- **Unlock:** Start with Rockets (after 100 rocket kills total)
- **Unlock:** Start with dual weapons (after 10 wins)

#### New Upgrade Paths
Unlock through achievements:

- **Flamethrower** - Unlock after 500 total kills
- **Railgun** - Unlock after surviving 20 minutes (beyond normal timer)
- **Drone Companions** - Unlock after maxing all weapons in one run
- **Orbital Strike** - Unlock after killing a boss

#### Difficulty Modifiers (For Bonus XP)
Optional challenges with XP multipliers:

- **Glass Cannon** - 50% HP, +50% XP
- **Scavenger** - XP gems worth half, spawn rate doubled, +25% XP
- **Speed Run** - 10 minute timer instead of 15, +100% XP
- **No Shield Regen** - Shields don't recharge, +30% XP
- **Boss Rush** - Boss every 2 minutes, +75% XP

---

### Challenge Modes
Specific run variants:

- **"Rockets Only"** - Only rocket upgrades appear
- **"No Health Upgrades"** - Health locked at 100
- **"Pacifist"** - Win without killing (dodge + timer only)
- **"Boss Gauntlet"** - 5 bosses back-to-back, no timer

**Rewards:** Unique unlocks, cosmetics, bragging rights

---

### Achievement System
Track milestones:

**Examples:**
- "Exterminator" - Kill 100 hexagons
- "Untouchable" - Win without taking damage
- "Overachiever" - Reach level 30
- "Combo Master" - Unlock all weapon synergies
- "Speed Demon" - Win in under 10 minutes
- "Tank" - Survive with shield only, no HP upgrades

**UI:** Achievement pop-ups during runs, trophy room in main menu

---

### Stats Tracking
Persistent across all runs:

**Track:**
- Total enemies killed (by type)
- Total damage dealt
- Fastest clear time
- Highest level reached
- Most used weapon
- Total deaths
- Win rate
- Favorite loadout

**Display:** Stats screen in main menu

---

### Loadout Presets (Like VS Characters)
Choose starting configuration:

**Preset Examples:**

#### "Assault Drone"
- Start with Minigun level 2
- +20% fire rate
- -10% HP

#### "Tank Configuration"
- Start with Shield level 2
- +50% HP
- -20% movement speed

#### "Glass Cannon"
- Start with Rockets level 2
- +50% damage
- -50% HP

**Unlocks:** After winning with different weapon focuses

---

## 5. NARRATIVE & FLAVOR

### Mission Briefings
Different objectives each run:

**Examples:**
- "Infiltrate and destroy power cores"
- "Survive long enough for data extraction"
- "Assassinate enemy commander"
- "Maximum carnage - no objective, just destroy"

**Implementation:** Text screen before mission start

---

### Mid-Mission Comms
Voice/text updates at intervals:

**Examples:**
- **5 min left:** "Exfiltration preparing, hold position!"
- **Boss spawn:** "High-value target detected!"
- **Low HP:** "Hull integrity critical!"
- **Max weapons:** "All systems at maximum efficiency!"

**Implementation:** Text pop-ups, maybe synthesized voice

---

### Multiple Strongholds
Different "levels" to infiltrate:

**Stronghold Types:**
- **Research Facility** - Lab aesthetic, prototype enemies
- **Military Base** - Heavy defenses, lots of turrets
- **Factory** - Assembly line, swarmer focus
- **Command Center** - Mixed forces, boss heavy

**Visual:** Different backgrounds, enemy compositions

---

### Ending Variations
Performance-based outcomes:

**Rankings:**
- **D-Rank:** Survived, barely (0-10 kills)
- **C-Rank:** Mission complete (standard clear)
- **B-Rank:** Impressive (high kills, few deaths)
- **A-Rank:** Exceptional (max level, all synergies)
- **S-Rank:** Perfect (no damage, max destruction)

**Different end text** based on rank

---

### Lore Terminals (Optional)
Collectible pickups that give worldbuilding:

**Examples:**
- Enemy manufacturing logs
- Intercepted communications
- Facility schematics
- Previous drone mission reports

**Implementation:** Rare spawns, pause game to read, optional

---

## 6. VISUAL & AUDIO UPGRADES

### Dynamic Music
Music intensity scales with gameplay:

**Layers:**
- **Base:** Calm exploration (early game)
- **Layer 2:** Drums kick in (5 min remaining)
- **Layer 3:** Full intensity (3 min remaining)
- **Boss Theme:** Unique track during boss fights

**Implementation:** Pygame mixer can layer/crossfade tracks

---

### Weapon-Specific Sounds
Each weapon has distinct audio:

- **Minigun:** Rapid "pew pew pew"
- **Rockets:** Deep "thoom" with whoosh trail
- **Laser:** Sustained "bzzzzt" charge + release
- **EMP:** Electric crackle
- **Shield:** Recharge hum, hit deflection "ting"

---

### Voice Lines (Optional)
Drone AI comments on milestones:

**Examples:**
- "New weapon online!"
- "Critical damage sustained!"
- "Systems overloading!"
- "Target eliminated!"
- "Mission timer: 5 minutes!"

**Implementation:** Text-to-speech or simple voice clips

---

### Enhanced Particle Effects
More juice:

- **Trails** - Linger longer, fade gradually
- **Explosions** - Multi-stage (flash → shockwave → debris)
- **Screen Distortion** - Slight warp on EMP pulse
- **Hit Sparks** - Direction-based particles on impact
- **Weapon Glow** - Pulsing aura when firing

---

### Environmental Storytelling
Visual details in background:

- **Destroyed base assets** - Flickering lights, sparks
- **Alarms** - Flashing red warning lights
- **Smoke/fire** - Ambient particle effects
- **Debris field** - Static background elements

---

## 7. QUALITY OF LIFE

### Minimap
Corner overlay showing:

- Player position (blue triangle)
- Enemy density (red dots, clustered)
- Objective markers (gold stars)
- Boss locations (large red icon)

**Size:** 150x150px corner widget

---

### Damage Numbers
Pop-ups showing DPS:

- **Damage dealt:** Yellow numbers rising from enemies
- **Critical hits:** Larger, different color (orange)
- **Healing:** Green numbers on player

---

### Enemy Telegraphing
Clearer attack warnings:

- **Chargers:** Flash red 1 second before dash
- **Boss attacks:** Charge-up animations
- **Turrets:** Laser sight before firing

---

### Accessibility Options
Settings menu additions:

- **Colorblind Modes:** Deuteranopia, Protanopia, Tritanopia friendly palettes
- **Reduced Screen Shake:** Option to disable/reduce
- **Larger UI:** 1.5x scale for text/HUD
- **High Contrast Mode:** Brighter outlines on enemies

---

### Keybind Customization
Rebindable controls:

- Movement (WASD default)
- Pause (ESC default)
- Dash (Spacebar)
- Menu navigation

---

### Gamepad Support
Controller input:

- **Left stick:** Movement
- **Right stick:** Aiming (for rockets/laser)
- **A button:** Dash
- **Start:** Pause

---

## 8. MULTIPLAYER (Ambitious)

### Local Co-op (2-4 Players)
Shared screen:

**Implementation:**
- Separate player instances
- Individual upgrade pools
- Combined score
- Friendly fire toggle

**Camera:** Zooms out to fit all players

---

### Versus Mode
Competitive variant:

**Win Conditions:**
- Survive longer than opponent
- Most kills wins
- Race to level X

**Implementation:** Separate arenas or shared with collision

---

### Leaderboards
Global rankings:

**Categories:**
- Daily challenge (specific seed)
- Weekly best score
- All-time high kills
- Speedrun (fastest win)

**Implementation:** Online API (ambitious) or local-only

---

## V2 PRIORITY TIERS

### Tier 1: High Impact, Medium Effort (Do First)
1. **Weapon synergies/combos** - Major strategic depth
2. **Elite enemies + boss waves** - Dramatic moments
3. **Persistent unlocks** (new weapons, modifiers) - Replayability
4. **Better particle effects + sound** - Game feel

**Estimated Dev Time:** 2-4 weeks

---

### Tier 2: High Impact, High Effort
5. **Meta-progression system** - Long-term goals
6. **Multiple mission types** - Content variety
7. **Dynamic music** - Immersion
8. **Challenge modes** - Player retention

**Estimated Dev Time:** 4-8 weeks

---

### Tier 3: Medium Impact (Polish)
9. **Minimap** - Navigation help
10. **Damage numbers** - Feedback clarity
11. **More enemy behaviors** - Tactical variety
12. **Environmental hazards** - Arena complexity

**Estimated Dev Time:** 2-3 weeks

---

### Tier 4: Low Priority / V3 Territory
13. **Multiplayer** - Massive scope increase
14. **Multiple maps/strongholds** - Art-heavy
15. **Full voice acting** - Production value

**Estimated Dev Time:** 8+ weeks

---

## THE V2 KILLER FEATURE

**What makes V2 a must-play upgrade?**

### Recommended Focus: **Weapon Combos + Meta-Progression**

**Why:**
- **Combos** completely change strategy and build variety
- **Meta-progression** keeps players coming back for unlocks
- Both are high-value for development time
- Together they create "just one more run" loop

**Implementation Path:**
1. Add weapon combo system (unlock conditions + new behaviors)
2. Add persistent save file with unlocks
3. Add 2-3 new weapons to unlock through play
4. Add difficulty modifiers for bonus XP
5. Polish with better effects and sounds

**This gives players:**
- Reason to experiment with builds (combos)
- Reason to replay (unlocks)
- Reason to push harder (difficulty modes)

---

## FINAL NOTES

### Scope Management
- **V2 doesn't need everything** - pick 3-5 features and nail them
- **Iterate based on feedback** - let V1 players guide priorities
- **Save some ideas for V3** - don't burn out trying to do everything

### Technical Debt
- **Refactor upgrade system** before adding complexity
- **Modularize enemy behaviors** for easier additions
- **Build animation system** if adding visual upgrades

### Playtesting Focus
- **Does V2 solve the "done at 10min" problem?**
- **Do players want to replay for unlocks?**
- **Are weapon combos satisfying?**

---

## SUCCESS METRICS FOR V2

**V2 is successful if:**
- Average playtime increases 50%+ vs V1
- Players complete 5+ runs (vs 1-2 in V1)
- Positive feedback on strategic depth
- Friends ask "what's new?" and get excited

**Ship when:**
- Core features (combos + unlocks) are polished
- No game-breaking bugs
- At least 3 new unlockable weapons functional
- Playtesters say "this feels way better than V1"
