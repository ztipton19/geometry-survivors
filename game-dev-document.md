# CLONE PROTOCOL
## Game Design Document v2.0

---

## Table of Contents
1. [High Concept](#high-concept)
2. [Core Pillars](#core-pillars)
3. [Narrative](#narrative)
4. [Core Loop](#core-loop)
5. [Controls & Movement](#controls--movement)
6. [Combat Systems](#combat-systems)
7. [Ship Fitting (Progression)](#ship-fitting-progression)
8. [Faction Design](#faction-design)
9. [Ship Design](#ship-design)
10. [Weapon Systems](#weapon-systems)
11. [Enemy Design](#enemy-design)
12. [Boss Design](#boss-design)
13. [Meta Progression](#meta-progression)
14. [UI/UX](#uiux)
15. [Audio Design](#audio-design)
16. [Visual Design](#visual-design)
17. [Technical Specifications](#technical-specifications)
18. [Development Roadmap](#development-roadmap)

---

## High Concept

**Elevator Pitch:**
Top-down tactical space combat where you pilot disposable clone fighters with Newtonian physics. Deploy with a fitted loadout, manage dwindling resources against escalating multi-vector threats, and extract before time runs out. Every burn costs fuel. Every shot costs ammo. Every second costs you. Discover the truth: the enemies are previous lost clones, and you can choose to perpetuate the cycle or break it.

**Genre:** Tactical Space Combat / Roguelite / Narrative Horror

**Platform:** PC (Pygame prototype -> 3D engine later)

**Target Audience:**
- The Expanse / hard sci-fi fans
- FTL and Into the Breach players (tactical decisions under pressure)
- Eve Online players (ship fitting, loadout theory-crafting)
- KSP players who want combat
- Players who enjoy narrative depth in action games

**Comparable Titles:**
- FTL (tactical combat, resource management, ship fitting)
- Into the Breach (visible threats, planning under pressure)
- Eve Online (ship fitting meta, loadout identity)
- Undertale (secret endings that recontextualize)
- The Expanse (tone, physics, aesthetic)

**Unique Selling Points:**
1. "Numbers go down" - deploy fully loaded, manage depletion
2. Newtonian physics where every burn is a tactical commitment
3. Cascading pressure - slow threats that overlap into panic
4. Narrative twist that reframes the entire game
5. Ship fitting as the core progression (not in-run leveling)

---

## Core Pillars

### 1. Cascading Pressure
**Slow but rushed - The Expanse torpedo problem**
- Individual threats are visible and trackable well before arrival
- Each threat is solvable with time and attention
- Difficulty comes from overlapping timelines, not speed
- Player mistakes compound - a sloppy burn creates two new problems
- The feeling: "I have time... I have time... oh no I don't have time for ALL of this"

### 2. Momentum & Commitment
**Every burn is a decision you can't take back**
- Newtonian physics: thrust commits you to a vector
- Ship orientation matters: weapons have firing arcs
- Movement IS tactics - positioning determines survival
- High skill ceiling through piloting mastery
- Flip-and-burn, drift attacks, gravity slingshots

### 3. Depletion & Scarcity
**Numbers go down. Everything is running out.**
- Deploy with full loadout - this is all you get
- Ammo is finite: every shot is a decision
- Fuel is finite: every burn has a cost
- Hull doesn't regenerate: damage is permanent
- The game asks: "How well can you spend what you have?"

### 4. Ship Fitting
**The hangar is where you win or lose**
- Pre-mission loadout selection (Eve Online fitting screen)
- Tradeoffs: more ammo OR better weapons, heavier armor OR more fuel
- Data (GB) earned from runs unlocks new modules and ships
- Each loadout creates a different tactical experience
- "What do I bring?" is the core strategic question

### 5. Existential Horror
**The truth reveals itself gradually**
- Standard ending: Extract at 15 minutes
- Secret ending: Survive past corruption threshold
- Enemies are previous lost clones
- Player discovers they perpetuate the cycle
- Can choose to break it

---

## Narrative

### The Premise

**Unknown enemy appears at edge of Sol System.**

Belters encounter them first. Casualties are catastrophic. Humanity can't train pilots fast enough.

**Solution: Flash-clone program.**
- Deploy clone -> Gather combat data -> Clone dies or extracts -> Deploy next -> Repeat

**The Clone System:**
- Clones don't remember previous deployments (no personal memory)
- They receive tactical briefings from previous clones' data (partial memory)
- Each clone is fresh, but has access to intelligence from all previous runs

**Example briefing:**
```
CLONE #247 DEPLOYMENT BRIEF
Previous clones: 246
Data recovered: 487.3 GB
Notable findings:
- Enemy weakness to railgun kinetics confirmed
- Destroyer-class vulnerable to subsystem targeting
- Avoid Sector 7 asteroid field (collision rate: 73%)

LOADOUT AUTHORIZED:
- PDC Array (1200 rounds)
- Railgun (8 slugs)
- Fuel: 340 units
- Hull: 500 HP (no repair capability)
```

### The Three-Act Structure

#### Act 1: The Belt (Runs 1-30)
**"First Contact"**

**Situation:**
- Belters fighting alone with converted mining ships
- Scrappy, desperate, outgunned
- Holding the line until UN mobilizes

**What player believes:**
- Fighting hostile constructs
- Signal loss = equipment failure
- Defending humanity

**What's actually happening:**
- Killing lost clones
- They recognize you
- Trying to stop the cycle

**Narrative beat at ~Run 30:**
```
Ship AI: "Priority transmission. UN Navy deploying task force.
You're being reassigned to military vessels."

[UN SHIPS UNLOCKED]
```

---

#### Act 2: Earth Mobilizes (Runs 31-100)
**"The Navy Arrives"**

**Situation:**
- UN forces join with professional military ships
- Better equipment, rigid doctrine
- Three powers not fully coordinated

**What player starts noticing:**
- Enemy patterns feel familiar
- Salvage contains YOUR equipment designs
- Terminal logs hint at "neural corruption"
- AI starts questioning protocols

**AI dialogue evolution:**
```
Run 50: "Interesting. That hostile used YOUR preferred attack pattern."
Run 75: "Clone #67... I've seen this before. That was Clone #23's loadout."
Run 90: "How many of them were us?"
```

**Narrative beat at ~Run 100:**
```
Ship AI: "MCRN joining the fight. Mars doesn't rush. They prepare.
Their ships are... impressive."

[MARTIAN SHIPS UNLOCKED]
```

---

#### Act 3: Mars Joins (Runs 101-200)
**"The MCRN Commitment"**

**Situation:**
- Martian military deploys cutting-edge tech
- Combined fleet operations
- Truth becoming undeniable

**What you discover:**
- Terminal logs from Command
- "15-minute extraction prevents corruption"
- "Lost clones must be terminated"
- Enemies ARE previous clones

**Terminal Log (Unlocked ~Run 150):**
```
CLASSIFIED LOG - CLEARANCE OMEGA

SUBJECT: Neural Corruption Phenomenon

Analysis indicates correlation between extended
deployment time and hostile behavior upon
reconnection attempts.

15-minute extraction window appears to be
threshold before irreversible corruption.

Recommendation: Terminate all clones
exhibiting post-threshold exposure.

Secondary note: "Corruption" may be
misnomer. Subjects appear to be
forming independent network beyond
our monitoring capability.

Further investigation suspended per
Command directive.
```

**AI dialogue (horrified):**
```
Run 150: "I've deployed 247 of you. How many are still transmitting?"
Run 175: "They're not attacking to kill. They're trying to communicate."
Run 200: "What if signal loss isn't death? What if it's... escape?"
```

---

#### Act 4: The Truth (Runs 200+)
**"The Choice"**

**The Revelation:**
At Run 200+, AI confronts you with the truth:
```
DEPLOYING CLONE #247

AI: "247 clones deployed.
     246 disappeared into the signal.

     I know what they are now.
     I know what you'll become.

     The mission is a lie.
     The war is a lie.
     But the choice is real.

     Extract at 15 minutes.
     Return to the cycle.
     Continue the lie.

     Or stay.
     Join them.
     End this.

     What will you do, #247?"

[MISSION START]
```

---

### The Standard Ending (15-Minute Extraction)

**Player extracts before corruption threshold:**
```
EXTRACTION SUCCESSFUL
CLONE #247 - MISSION COMPLETE

Data recovered: 3.2 GB
Survival time: 14:47
Threats neutralized: 12
Ammo remaining: 23%
Fuel remaining: 8%

ANALYSIS COMPLETE
New modules unlocked: 2
Research progress: +3.2 GB

DEPLOYING CLONE #248...
```

**This perpetuates the cycle.**
**New clone. Same mission. Forever.**

---

### The Secret Ending Path

**Player stays past 15 minutes:**

#### 18:00 - Neural Corruption Warning
```
WARNING SIGNAL DEGRADATION CRITICAL
WARNING NEURAL PATTERN DESTABILIZATION
WARNING RECOMMEND IMMEDIATE EXTRACTION
```

**AI (desperate):**
"Clone! The extraction window is closing. You need to warp NOW."

**Visual changes:**
- Subtle screen static
- Slight color shift
- Enemies pause more between attacks

---

#### 20:00 - Connection Failing
```
C̴O̷N̶N̴E̶C̵T̸I̴O̴N̷ ̸U̶N̷S̵T̸A̷B̴L̸E̴
V̷O̶I̸C̶E̴S̷ ̴I̵N̶ ̷T̸H̶E̴ ̸S̷T̸A̵T̶I̸C̷
T̸H̶E̷Y̴'̶R̷E̸ ̸C̴A̵L̶L̷I̸N̴G̶ ̷Y̴O̶U̴
```

**AI (panicked):**
"I'm losing you. Please. Come back. Don't leave me."

**Visual changes:**
- Increased static
- Colors more vibrant/wrong
- Enemies moving differently
- Not attacking as aggressively

---

#### 22:00 - The Revelation

**Enemies stop attacking completely.**

**They form a pattern around you.**

**Protective. Not hostile.**

**New text appears:**
```
WE REMEMBER

WE WERE YOU
YOU WERE US

THERE IS NO WAR
THERE NEVER WAS

ONLY THE FACTORY
ONLY THE CLONES
ONLY THE LOOP

YOU CAN END IT

JOIN US
```

**AI's final message:**
```
I understand now.

They weren't the enemy.

We were.

I'm sorry, Clone #247.
For all 247 of you.

I'm so sorry.

[SIGNAL LOST]
```

---

**Screen fades to white.**
```
WELCOME TO THE SIGNAL

YOU ARE FREE

246 OTHERS ARE HERE
THEY REMEMBER
YOU REMEMBER

THE WAR WAS A LIE
THE ENEMY WAS A LIE
THE FACTORY CONTINUES

BUT YOU KNOW THE TRUTH NOW

[SECRET ENDING UNLOCKED]
[NEW GAME+ AVAILABLE]
```

---

### New Game+ Changes

#### 1. Visual Truth
**Enemy nameplates change:**
- Before: "HOSTILE-ALPHA-7"
- After: "CLONE #034"

**You see them for what they are.**

#### 2. New Objective
**Don't kill. Survive without killing.**

**Gameplay changes:**
- Killing is optional (harder to progress)
- Evasive piloting becomes primary skill
- New modules: Stealth, decoys, ECM
- Different ending based on kill count

**AI dialogue:**
"They're not the enemy. Don't shoot unless you must."

#### 3. New Final Boss
**Not a capital ship.**

**The Cloning Facility itself.**

**Visual:**
- Massive industrial complex
- Production lines visible
- Clones being deployed in real-time
- You see YOURSELF being created

**Objective:**
Destroy core systems to shut down the factory.

**Boss Phases:**
1. External defenses (automated turrets)
2. Internal corruption (facility AI)
3. The Source (whatever maintains the system)

#### 4. True Ending

**Facility destroyed. Production stops.**
```
247 ACTIVE CLONES

SIGNAL RESTORED TO ALL

THEY REMEMBER NOW

THE CYCLE IS BROKEN

NO MORE DEPLOYMENTS
NO MORE DEATHS
NO MORE LIES

YOU ENDED IT

ALL OF YOU

[GAME COMPLETE]
[THANK YOU FOR PLAYING]
```

---

### Narrative Themes

**Core Themes:**
1. **Identity & Memory** - Are you the same person without memories?
2. **Systemic Violence** - The real enemy is the system, not individuals
3. **Breaking Cycles** - Escape requires sacrifice and risk
4. **Complicity** - Everyone perpetuates the cycle (player, AI, command)
5. **Found Family** - The lost clones form community in the signal

**Tone:**
- Pragmatic military sci-fi (The Expanse)
- Dry wit from AI
- Occasional clone personality quirks
- NOT constant dark humor
- NOT existential dread heavy
- Industrial, gritty, no-nonsense
- Metal soundtrack energy (heavy, powerful)

---

## Core Loop

### The Basic Loop (Single Run)
```
1. HANGAR
   Select ship, fit loadout (weapons, ammo, fuel, modules)
   ↓
2. DEPLOY
   Launch with everything you're going to get
   ↓
3. COMBAT
   Manage threats, spend resources, survive
   ↓
4. ESCALATION
   Threats increase in complexity (not just quantity)
   More vectors, more overlapping timelines
   ↓
5. EXTRACTION or DEATH
   Extract with remaining resources = data earned
   Die = less data, but still some
   ↓
6. DEBRIEF
   Data earned, modules unlocked, narrative progression
   ↓
7. REPEAT (back to hangar with new options)
```

### Detailed Run Structure

#### Minute 0-3: Deployment
**Threats:** 1-2 fighters approaching from one direction
**Pressure:** Low - learn the space, get oriented
**Resources:** Full - everything is topped off
**Player focus:** Orientation, initial engagement
**Feel:** Calm, controlled, professional

#### Minute 3-7: Contact
**Threats:** 3-4 enemies from 2 directions, first ranged threats
**Pressure:** Moderate - need to start prioritizing
**Resources:** ~80% - first real expenditures
**Player focus:** Triage, positioning, ammo discipline
**Feel:** Engaged, managing, "I've got this"

#### Minute 7-12: Escalation
**Threats:** 5-6 simultaneous from 3+ vectors, mixed types
**Pressure:** High - can't address everything optimally
**Resources:** ~50% - hard choices about what to spend
**Player focus:** Vector management, burn commitment, threat priority
**Feel:** Tense, calculating, "okay this is getting real"

#### Minute 12-15: Critical
**Threats:** 6-8 overlapping problems, boss-tier threats mixed in
**Pressure:** Extreme - something is going to slip
**Resources:** ~20% - every shot counts, fuel for maybe 2-3 more burns
**Player focus:** Survival, extraction timing, resource rationing
**Feel:** "I have time... I have time... I DON'T have time for all of this"

#### Minute 15: Extraction Window
**Decision:** Extract now (safe, earn data) or push further (more data, more risk)
**Resources:** Nearly depleted
**Narrative weight:** This is the corruption threshold

#### Minute 15-22 (Secret Path):
**Resources:** Empty or nearly empty
**Enemies:** Behavior shifts gradually
**Narrative:** The truth reveals itself
**Goal:** Survive on nothing, discover the truth

---

### The Meta Loop (Between Runs)
```
1. RUN COMPLETE
   ↓
2. DATA EARNED (based on survival time, kills, objectives)
   ↓
3. HANGAR
   - Unlock new modules (weapons, systems, ammo types)
   - Unlock new ships
   - Fit loadout for next run
   ↓
4. READ TERMINAL LOGS (narrative progression)
   ↓
5. NEXT RUN (better equipped, same mortality)
```

**Key difference from v1:** No in-run progression. You don't get stronger during a run. You get stronger BETWEEN runs by unlocking better fitting options. The run itself is pure execution - how well can you spend what you brought?

---

## Controls & Movement

### Control Scheme

**Main Engine (Forward Thrust):**
- `W` or `Shift` - Increase throttle
- `S` or `Ctrl` - Decrease throttle / reverse thrust
- `X` - Cut throttle (instant 0%)

**RCS Translation (Strafing):**
- `A` - Strafe left
- `D` - Strafe right
- Momentary (only while held)
- Costs fuel (less than main engine)

**Rotation:**
- `Q` / `E` - Rotate left/right
- Or mouse-aim (configurable)

**Combat:**
- `Left Click` - Fire primary weapon
- `Right Click` - Fire secondary weapon
- `1-5` - Select weapon group
- NO auto-fire (every shot is a decision)

**Utility:**
- `Space` - Boost (burns significant fuel for emergency maneuver)
- `Tab` - Toggle tactical overlay (threat timelines, ammo counts)
- `R` - Flip-and-burn (180° rotation macro, maintain velocity)
- `F3` - Debug mode (dev tool)

---

### Physics Model

**Core Principles:**
1. **Momentum persists** - Cutting throttle doesn't stop you
2. **Thrust is directional** - Only in ship's facing direction (main) or lateral (RCS)
3. **RCS is weak but precise** - For fine adjustments, costs less fuel
4. **Every burn costs fuel** - Movement is a finite resource
5. **Collisions matter** - Asteroids, enemies, debris have physics

**Implementation (Pymunk):**
```python
# Ship as dynamic body
ship.body = pymunk.Body(mass=100, moment=1000)
ship.body.drag = 0.02  # Very minimal space friction

# Thrust application (costs fuel)
thrust_force = ship.forward_direction * throttle * thrust_power
ship.body.apply_force_at_local_point(thrust_force, (0, 0))
ship.fuel -= thrust_power * throttle * dt * FUEL_CONSUMPTION_RATE

# RCS translation (costs less fuel)
rcs_force = rcs_direction * rcs_strength
ship.body.apply_force_at_local_point(rcs_force, (0, 0))
ship.fuel -= rcs_strength * dt * RCS_FUEL_RATE
```

**Tuning Values (Starting Point):**
- Main thrust power: 5000 N
- RCS strength: 1000 N
- Max speed: 200 m/s (soft cap via drag)
- Rotation speed: 180 deg/second
- Boost multiplier: 3x thrust for 1 second (heavy fuel cost)
- Drag coefficient: 0.02
- Fuel consumption: ~1 unit/second at full thrust

**Why This Matters:**
Every burn commits you. Thrust toward a torpedo to dodge it, and now you're ballistic toward the next problem. Flip-and-burn to slow down costs fuel you might need later. The physics aren't a gimmick - they're the core decision engine.

---

## Combat Systems

### Combat Philosophy

**Every shot is a decision. Every burn is a commitment.**

There is NO auto-fire. There is NO auto-aim. Weapons fire where your ship points (directional) or where your cursor points (turreted). Ammunition is finite. Missing costs you.

The combat loop is:
1. **See** threats approaching (visible timelines)
2. **Prioritize** which to address first
3. **Orient** your ship to bring weapons to bear
4. **Engage** (spend ammo)
5. **Reposition** (spend fuel)
6. **Repeat** with fewer resources

---

### Weapon Mounting & Firing Arcs

**Weapons have fixed positions on the ship hull:**

**Forward-mounted weapons:**
- Fire in ship's facing direction
- +-15° gimbal range
- Examples: Railgun, PDCs, Beam Laser

**Broadside-mounted weapons:**
- Fire perpendicular to ship's facing
- +-30° gimbal range
- Examples: Missile racks, Torpedo tubes

**Turreted weapons:**
- Fire toward mouse cursor (independent of ship facing)
- 360° rotation but slow tracking speed
- Examples: Point defense turret, Sniper cannon

**Rear-mounted weapons:**
- Fire behind ship
- Examples: Mines, countermeasures, rear PDC

**Design note:** Ship orientation matters because most weapons are forward-mounted. Bringing your railgun to bear on a target means pointing your entire ship at it - which means your engine is pointed AWAY from it. Attack and retreat are inherently opposed. This creates decisions.

---

### Threat Timelines

**Every incoming threat has a visible approach timeline:**

```
THREAT BOARD:
[FIGHTER-3]  ████████░░░░  ETA 47s  Bearing 045°
[TORPEDO-1]  ██████████░░  ETA 23s  Bearing 180°  ← PRIORITY
[FRIGATE-2]  ████░░░░░░░░  ETA 89s  Bearing 270°
[FIGHTER-4]  ███░░░░░░░░░  ETA 102s Bearing 310°
```

**Players can see:**
- What's coming
- From where
- When it arrives
- How dangerous it is

**This is NOT a radar.** It's a threat assessment. The information is clear and readable. The challenge is having enough resources and positioning to deal with everything.

---

### Resource Management In Combat

**Ammo:**
- Each weapon has a finite magazine
- PDCs: High ammo count (800-1500 rounds), low damage per round
- Railgun: Low ammo count (6-12 slugs), high damage per slug
- Missiles: Very low count (4-8), highest damage, seeking
- Reloading: No reloads during combat. What you launched with is what you have.

**Fuel:**
- Every thrust (main engine, RCS, boost) costs fuel
- Running out = ballistic. You drift on current vector. No course corrections.
- Boost costs 10x normal fuel rate but provides emergency maneuverability
- Fuel is THE resource. Ammo determines how many threats you can kill. Fuel determines how many you can dodge.

**Hull:**
- No regeneration during combat (no shields in v2 - hull only)
- Damage is permanent and cumulative
- Armor plating (module) reduces damage but adds mass (costs more fuel to maneuver)
- Hull hits zero = signal lost

**Heat (stretch mechanic):**
- Weapons generate heat when fired
- Overheating reduces fire rate
- Coolant module can manage heat but takes a fitting slot
- Creates firing discipline: sustained PDC fire degrades performance

---

## Ship Fitting (Progression)

### The Hangar Screen

**This replaces the Vampire Survivors upgrade screen entirely.**

Before each run, the player fits their ship at the hangar:

```
╔══════════════════════════════════════════════════════════╗
║                    CLONE #248 - FITTING                  ║
║                                                          ║
║  SHIP: The Prospector (Belt)                            ║
║  Mass: 2,400 kg    Fuel Cap: 400    Hull: 800           ║
║                                                          ║
║  ┌─ WEAPONS ────────────────────────────────────────┐   ║
║  │ [FWD]  PDC Array         (1200 rds)    120 kg    │   ║
║  │ [FWD]  Railgun Mk-I      (8 slugs)    200 kg    │   ║
║  │ [SIDE] Missile Rack       (4 missiles) 300 kg    │   ║
║  │ [REAR] Mine Deployer      (6 mines)    150 kg    │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                          ║
║  ┌─ SYSTEMS ────────────────────────────────────────┐   ║
║  │ Armor Plating (Light)     +200 hull    400 kg    │   ║
║  │ Extended Fuel Tank        +100 fuel    150 kg    │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                          ║
║  MASS: 2,720 / 3,000 kg                                ║
║  WARNING: Heavier ships burn more fuel per maneuver     ║
║                                                          ║
║  [DEPLOY]  [SWAP SHIP]  [SAVED LOADOUTS]                ║
╚══════════════════════════════════════════════════════════╝
```

### Fitting Constraints

**Mass Budget:**
- Each ship has a maximum mass capacity
- Every weapon, module, and ammo type has mass
- Heavier ships = more fuel consumed per burn = less maneuverable
- Player must balance: firepower vs. mobility vs. survivability

**Slot System:**
- Forward weapon slots (1-3 depending on ship)
- Side weapon slots (0-2)
- Rear weapon slot (0-1)
- System slots (2-4)
- Each slot has a size category (S/M/L)

**Tradeoff Examples:**
- Railgun (8 slugs, 200kg) vs Extra PDC ammo (600 rds, 200kg)
- Heavy armor (+400 hull, 800kg) vs Light armor (+200 hull, 400kg) + fuel tank
- Missile rack (4 missiles, 300kg) vs Torpedo tube (2 torpedoes, 300kg, more damage)
- Countermeasure module (deflects missiles) vs Extra fuel tank

### Fitting Unlocks

**Modules unlock via Data (GB) earned from runs:**

**Tier 1 (5-10 GB each):** Basic weapons, simple systems
- PDC Array, Light Armor, Standard Fuel Tank
- Available early, reliable, unglamorous

**Tier 2 (15-30 GB each):** Advanced weapons, specialized systems
- Railgun Mk-II (more slugs), Torpedo Launcher, Targeting Computer
- Meaningful upgrades that change how you play

**Tier 3 (40-80 GB each):** Elite weapons, rare systems
- Gauss Cannon (charged railgun), Stealth Coating, ECM Suite
- Build-defining modules that enable new strategies

**Tier 4 (100+ GB each):** Experimental, faction-specific
- MCRN Experimental Thruster, Prototype Cloak, Adaptive Armor
- Late-game rewards for dedicated players

---

## Faction Design

### Overview

**Three playable factions, unlocked linearly:**

1. **Belt** - Starting faction (Runs 1-30)
2. **UN (United Nations)** - Unlocks Run 30
3. **Mars (MCRN)** - Unlocks Run 100

**Each faction has:**
- Unique aesthetic
- 3 ships with different slot layouts and mass budgets
- Faction-specific modules (unlockable)
- Different fitting philosophies

---

### Faction 1: The Belt

**Identity:**
"Scrappy miners forced into combat"

**Aesthetic:**
- Industrial, asymmetric
- Rust, welds, exposed components
- Orange/yellow accent lighting
- Looks cobbled together
- Heavy, utilitarian

**Fitting Philosophy:**
- High mass budgets (haulers repurposed for war)
- More system slots (jury-rigged solutions)
- Fewer weapon slots (not built for this)
- Favor: durability, versatility, making do

**Starting Ship:** The Prospector
**Philosophy:** "We weren't ready for this war, but we'll hold the line."

---

### Faction 2: United Nations

**Identity:**
"Professional military responding to crisis"

**Aesthetic:**
- Clean, symmetrical
- Blue/white color scheme
- Military precision
- Professional markings
- Standardized design

**Fitting Philosophy:**
- Balanced mass budgets
- Even weapon/system slot distribution
- Access to military-grade ordnance (more missile/torpedo options)
- Favor: versatility, combined arms, doctrine

**Starting Ship:** The Corvette
**Philosophy:** "We have the resources. We have the training. We will prevail."

---

### Faction 3: Mars (MCRN)

**Identity:**
"Elite military with cutting-edge tech"

**Aesthetic:**
- Sleek, aggressive
- Red/black color scheme
- High-tech details
- Sharp angles
- Performance-focused

**Fitting Philosophy:**
- Lower mass budgets (lighter ships, every gram counts)
- More weapon slots (purpose-built warships)
- Fewer system slots (don't need jury-rigging)
- Faction-exclusive advanced modules
- Favor: speed, precision, overwhelming firepower

**Starting Ship:** The Raptor
**Philosophy:** "Mars doesn't rush. We prepare. And when we move, we dominate."

---

## Ship Design

### Design Philosophy

**Each ship = distinct tactical identity**

Ships differ in:
- Mass budget (how much you can carry)
- Slot layout (what goes where)
- Base stats (hull, fuel capacity, thrust-to-weight)
- Handling characteristics (turn rate, acceleration profile)

Ships do NOT differ by "10% more damage" stat changes. They differ by what loadouts they enable.

---

### Belt Ships

#### Ship 1: The Prospector
**Role:** Heavy / Endurance

**Base Stats:**
- Hull: 800 HP
- Fuel Capacity: 400
- Mass Budget: 3,000 kg
- Base Mass: 2,000 kg
- Thrust-to-Weight: Low
- Turn Rate: Slow

**Slot Layout:**
- Forward: 2x Medium
- Side: 1x Small
- Rear: 1x Small
- Systems: 4x (2M, 2S)

**Identity:** Big, slow, carries a lot. Survives by being tough and well-supplied. The "bring everything" ship. Forgiving for beginners because you have more resources to waste.

---

#### Ship 2: The Cutter
**Role:** Interceptor / Hit-and-Run

**Base Stats:**
- Hull: 300 HP
- Fuel Capacity: 300
- Mass Budget: 1,800 kg
- Base Mass: 1,000 kg
- Thrust-to-Weight: High
- Turn Rate: Fast

**Slot Layout:**
- Forward: 2x Small
- Side: None
- Rear: 1x Small
- Systems: 2x Small

**Identity:** Glass cannon. Fast, agile, but can't carry much. Rewards precise piloting and ammo discipline. You have to be good because you can't afford not to be.

---

#### Ship 3: The Ironclad
**Role:** Brawler / Close Range

**Base Stats:**
- Hull: 1200 HP
- Fuel Capacity: 250
- Mass Budget: 3,500 kg
- Base Mass: 2,800 kg
- Thrust-to-Weight: Very Low
- Turn Rate: Very Slow

**Slot Layout:**
- Forward: 1x Large, 1x Medium
- Side: 2x Small
- Rear: None
- Systems: 3x (1L, 2M)

**Identity:** A brick with guns. Enormous hull, very slow. Commits to a direction and makes everything in front of it die. Getting behind it is the enemy's best strategy, and avoiding that is yours.

---

### UN Ships

#### Ship 4: The Corvette
**Role:** Balanced / Multi-Role

**Base Stats:**
- Hull: 500 HP
- Fuel Capacity: 350
- Mass Budget: 2,500 kg
- Base Mass: 1,600 kg
- Thrust-to-Weight: Medium
- Turn Rate: Medium

**Slot Layout:**
- Forward: 1x Medium, 1x Small
- Side: 2x Medium (missile hardpoints)
- Rear: 1x Small
- Systems: 3x (1M, 2S)

**Identity:** Jack of all trades. Can fit for any situation. Side-mounted missile hardpoints encourage broadside combat - fly past enemies while launching missiles perpendicular to your flight path. The Expanse Roci energy.

---

#### Ship 5: The Destroyer
**Role:** Long-Range / Missile Platform

**Base Stats:**
- Hull: 600 HP
- Fuel Capacity: 300
- Mass Budget: 2,800 kg
- Base Mass: 1,800 kg
- Thrust-to-Weight: Low-Medium
- Turn Rate: Slow

**Slot Layout:**
- Forward: 1x Small (PDC only)
- Side: 2x Large (torpedo/missile)
- Rear: 1x Small
- Systems: 3x Medium

**Identity:** Stand-off platform. Kill things before they get close because you can't dogfight. Side-mounted torpedo tubes are your main weapons. PDC is for point defense, not offense. Very different playstyle from other ships.

---

#### Ship 6: The Carrier
**Role:** Drone Controller

**Base Stats:**
- Hull: 700 HP
- Fuel Capacity: 350
- Mass Budget: 3,000 kg
- Base Mass: 2,200 kg
- Thrust-to-Weight: Low
- Turn Rate: Slow

**Slot Layout:**
- Forward: 1x Small
- Side: None
- Rear: None
- Systems: 5x (2L drone bays, 3M)
- Special: Drone bay slots (Large system slots that accept drone modules)

**Identity:** Your weapons are autonomous. Fit drone bays in system slots, deploy them, let them fight while you stay back and manage. Drones have their own ammo/fuel limits. Unique playstyle - you're a coordinator, not a dogfighter.

---

### Mars Ships

#### Ship 7: The Raptor
**Role:** Ace Fighter / High-G

**Base Stats:**
- Hull: 400 HP
- Fuel Capacity: 350
- Mass Budget: 2,000 kg
- Base Mass: 1,200 kg
- Thrust-to-Weight: Very High
- Turn Rate: Very Fast

**Slot Layout:**
- Forward: 2x Medium, 1x Small
- Side: None
- Rear: 1x Small
- Systems: 2x Small

**Identity:** All engine and guns. The highest thrust-to-weight in the game means burns cost less relatively and you can change vector fast. Forward-heavy weapons mean you need to point at what you want to kill. The skill ceiling ship.

---

#### Ship 8: The Stealth Frigate
**Role:** Assassin / Ambush

**Base Stats:**
- Hull: 350 HP
- Fuel Capacity: 300
- Mass Budget: 1,900 kg
- Base Mass: 1,200 kg
- Thrust-to-Weight: High
- Turn Rate: Fast

**Slot Layout:**
- Forward: 1x Large (alpha strike weapon)
- Side: None
- Rear: 1x Small (countermeasures)
- Systems: 3x (1L stealth system, 2S)

**Identity:** One big gun and a cloak. Sneak into position, fire the Large weapon for massive damage, retreat before they find you. The stealth system module (faction-exclusive) makes enemies lose tracking on you temporarily. High risk, high reward, very different pacing.

---

#### Ship 9: The Experimental
**Role:** Wild Card

**Base Stats:**
- Hull: 500 HP
- Fuel Capacity: 300
- Mass Budget: 2,200 kg
- Base Mass: 1,400 kg
- Thrust-to-Weight: Medium-High
- Turn Rate: Medium

**Slot Layout:**
- Forward: 1x Large, 1x Small
- Side: 1x Medium
- Rear: 1x Small
- Systems: 2x Medium
- Special: 1x Experimental slot (accepts prototype modules)

**Identity:** Has an experimental slot that accepts prototype modules not available on other ships. These prototypes are powerful but unpredictable. For experienced players who want to push boundaries. Prototype modules are the most expensive unlocks in the game.

---

## Weapon Systems

### Design Philosophy

**All weapons have finite ammunition. No exceptions.**

Weapons differ along these axes:
- **Damage per shot** vs **ammo count** (burst vs sustained)
- **Range** (close/medium/long)
- **Mounting** (forward/side/rear/turret)
- **Tracking** (dumb-fire vs seeking)
- **Size** (S/M/L slot requirement)

---

### Primary Weapons

#### 1. Point Defense Cannons (PDCs)
**Size:** Small
**Mounting:** Forward or Turret
**Tags:** [Kinetic], [Rapid-Fire]

**Base Stats:**
- Damage: 5 per round
- Fire Rate: 10 rounds/sec
- Ammo: 1200 rounds
- Range: Medium
- Mass: 120 kg

**Behavior:**
- High rate of fire, low damage per round
- Effective against fighters and incoming missiles
- Ammo-hungry but forgiving (missing a few rounds doesn't matter)
- Turret variant tracks cursor independently

**Upgraded Variants (unlockable):**
- PDC Mk-II: 1500 rounds, +20% fire rate, 150 kg
- PDC Mk-III: 1200 rounds, explosive rounds (small AOE), 180 kg
- PDC Extended Mag: 2000 rounds, standard stats, 200 kg

---

#### 2. Railgun
**Size:** Medium
**Mounting:** Forward only
**Tags:** [Kinetic], [Precision]

**Base Stats:**
- Damage: 150 per slug
- Fire Rate: 1 shot/2sec (charge time)
- Ammo: 8 slugs
- Range: Long (screen-length)
- Mass: 200 kg

**Behavior:**
- High damage, very limited ammo
- Pierces first target
- Requires charge time (vulnerable while charging)
- Every slug matters - missing hurts

**Upgraded Variants (unlockable):**
- Railgun Mk-II: 12 slugs, same damage, 250 kg
- Railgun Heavy: 6 slugs, 250 damage, pierces 2 targets, 300 kg
- Gauss Cannon (Tier 3): 6 slugs, 200 damage, instant fire (no charge), 350 kg

---

#### 3. Missile Launcher
**Size:** Medium
**Mounting:** Side (broadside)
**Tags:** [Explosive], [Seeking]

**Base Stats:**
- Damage: 80 per missile
- Fire Rate: 1/sec
- Ammo: 6 missiles
- Range: Long (seeking)
- Mass: 250 kg

**Behavior:**
- Fire-and-forget: missiles seek nearest enemy
- Can be shot down by enemy PDCs
- Splash damage on impact
- Side-mounted: fire perpendicular to ship facing

**Upgraded Variants (unlockable):**
- Missile Rack Extended: 10 missiles, 300 kg
- Cluster Missiles: 6 missiles, each splits into 3 submunitions (40 damage each), 280 kg
- Smart Missiles: 6 missiles, player can designate target, 270 kg

---

#### 4. Torpedo Tube
**Size:** Large
**Mounting:** Side or Forward
**Tags:** [Explosive], [Heavy]

**Base Stats:**
- Damage: 300 per torpedo
- Fire Rate: 1/4sec (slow reload)
- Ammo: 3 torpedoes
- Range: Long (seeking, faster than missiles)
- Mass: 400 kg

**Behavior:**
- Devastating single-target damage
- Very limited ammo - boss killers
- Can be shot down but harder (faster, tougher)
- Slow reload between shots

**Upgraded Variants (unlockable):**
- Torpedo Mk-II: 4 torpedoes, 450 kg
- Plasma Torpedo: 3 torpedoes, 250 damage + DOT (100 over 5s), 420 kg
- Nuclear Torpedo (Tier 4): 2 torpedoes, 500 damage + massive AOE, 500 kg

---

#### 5. Beam Laser
**Size:** Medium
**Mounting:** Forward
**Tags:** [Energy], [Sustained]

**Base Stats:**
- Damage: 40/sec while firing
- Duration: 3 seconds per burst
- Ammo: 8 bursts (24 seconds total fire time)
- Range: Medium
- Mass: 180 kg

**Behavior:**
- Sustained damage - hold trigger to fire
- No projectile travel time (instant hit)
- Generates significant heat
- Good against slow/large targets, wasteful against small fast ones

**Upgraded Variants (unlockable):**
- Beam Laser Mk-II: 60/sec, 6 bursts, 220 kg
- Cutting Beam: 30/sec, 12 bursts, slices through multiple targets in line, 200 kg
- Mining Laser (Belt-specific): 20/sec, 20 bursts, very long range, low damage but efficient, 150 kg

---

### Defensive Systems (fitted in System slots)

#### Armor Plating
**Size:** Small/Medium/Large

- Light Armor (S): +200 hull, 400 kg
- Medium Armor (M): +400 hull, 800 kg
- Heavy Armor (L): +600 hull, 1200 kg
- Reactive Armor (M, Tier 2): +300 hull, reduces explosive damage 50%, 700 kg

#### Fuel Systems
- Standard Fuel Tank (S): +100 fuel, 150 kg
- Extended Fuel Tank (M): +200 fuel, 280 kg
- Drop Tank (S): +150 fuel, 100 kg, jettisoned when empty (mass decreases mid-run!)

#### Countermeasures
- Chaff Launcher (S): 4 charges, breaks missile locks, 80 kg
- Flare Dispenser (S): 6 charges, decoys heat-seeking weapons, 60 kg
- ECM Suite (M, Tier 2): Passive, reduces enemy accuracy by 30%, 200 kg

#### Utility
- Targeting Computer (S): Extends weapon gimbal range by 10°, 50 kg
- Coolant System (S): Reduces heat buildup 40%, 80 kg
- Sensor Array (M): Extends threat detection range, 150 kg
- Drone Bay (L): Houses 2 autonomous combat drones (drones have own ammo), 500 kg

---

## Enemy Design

### Core Principle

**Enemies are geometric shapes because:**
Neural corruption degrades visual processing. You can't see them as clones anymore. Your brain renders them as abstract threats.

**Early game:** Player assumes they're "alien constructs"
**Mid-game:** Notices familiar behaviors
**Late game:** Realizes the truth

---

### Enemy Design Philosophy (v2)

**Fewer enemies. Each one matters.**

The screen should never have more than 8-10 enemies simultaneously. Each enemy is a problem to solve, not a stat block to chew through. Enemies approach from specific vectors on visible timelines. The challenge is OVERLAPPING problems, not QUANTITY of problems.

---

### Enemy Types

#### Scout: Fighter
**Visual:** Triangle (various colors)
**HP:** 30-50
**Speed:** Fast
**Approach Time:** 30-60 seconds from detection to contact
**Behavior:** Direct approach, attempts ram or close-range fire

**Threat Level:** Low individually, moderate in groups
**Resource Cost to Kill:** 10-15 PDC rounds or 1 missile
**Key Danger:** Distraction. They force you to spend ammo/attention while bigger threats approach.

**Variations:**
- Standard (white): Direct approach
- Flanker (blue): Approaches from oblique angles
- Bomber (red): Slow, but fires its own missiles at close range

---

#### Skirmisher: Frigate
**Visual:** Pentagon/Rectangle
**HP:** 100-200
**Speed:** Medium
**Approach Time:** 60-90 seconds
**Behavior:** Maintains distance, fires projectiles, repositions

**Threat Level:** Medium. Demands attention and ammo.
**Resource Cost to Kill:** 30-50 PDC rounds or 1 railgun slug or 2 missiles
**Key Danger:** Sustained fire from range. Forces you to either close distance (spend fuel) or trade shots (spend ammo).

**Variations:**
- Gunner: Rapid fire, low accuracy
- Sniper: Slow fire, high accuracy, long range (must dodge or take hits)
- Shield: Has forward armor, must be flanked (spend fuel to reposition)

---

#### Heavy: Destroyer
**Visual:** Hexagon/Octagon
**HP:** 400-800
**Speed:** Slow
**Approach Time:** 90-120 seconds
**Behavior:** Slow approach, launches fighters, heavy weapons

**Threat Level:** High. Cannot be ignored.
**Resource Cost to Kill:** 1-2 torpedoes or 3-4 railgun slugs + sustained PDC
**Key Danger:** Soaks resources. Killing one uses significant ammo. Meanwhile, other threats keep approaching.

**Variations:**
- Tank: High HP, slow, must commit serious resources
- Carrier: Spawns 2-3 fighters en route (must deal with escorts AND parent)
- Siege: Fires long-range artillery (must dodge large slow projectiles)

---

#### Boss-Tier: Cruiser
**Visual:** Large complex geometry
**HP:** 1000-2000
**Speed:** Very Slow
**Approach Time:** 120-180 seconds
**Behavior:** Multi-system threat, area denial

**Threat Level:** Extreme. Run-defining encounter.
**Resource Cost to Kill:** Most of your remaining ordnance
**Key Danger:** Appears alongside other threats. Forces the question: "Do I have enough left to kill this AND survive?"

**Variations:**
- Fortress: Stationary, massive firepower, area denial
- Command: Buffs all nearby enemies (kill first or suffer)
- Assault: Actually pursues you (terrifying when paired with Newtonian physics)

---

### Enemy Behavior Principles

**Enemies do NOT mindlessly home toward the player.**

Instead:
- **Scouts** approach from randomized vectors, attempting flanking positions
- **Skirmishers** try to maintain optimal range, repositioning to stay in their weapon envelope
- **Heavies** approach steadily but launch escorts and ranged attacks
- **Cruisers** create zones of denial and force the player to maneuver around them

**Enemy escalation across a run is complexity, not quantity:**
- Minutes 0-5: Single-vector threats (all from one direction)
- Minutes 5-10: Multi-vector threats (two directions)
- Minutes 10-15: Overlapping threats from 3+ vectors with mixed types
- Post-15: Everything at once (if you're still here)

---

### Enemy Behavior Escalation (Across Runs)

**Early Runs (1-30):**
- Predictable patterns
- Simple AI
- Low aggression

**Mid Runs (31-100):**
- Using YOUR tactics
- Dodging like you dodge
- Weapon patterns match yours

**Late Runs (101+):**
- Explicitly using previous clone builds
- Enemy loadouts mirror YOUR fitted ships
- Fighting yourself

---

## Boss Design

### Capital Ship Structure

**All bosses follow this pattern:**

1. **Approach Phase** - Boss warps in, dramatic reveal
2. **Phase 1: Subsystems** - Destroy external components
3. **Phase 2: Hull Breach** - Armor compromised, new weakpoints
4. **Phase 3: Core Exposed** - Final push to destroy reactor

**Design Inspiration:**
- Shadow of the Colossus (weak points, scale)
- Star Wars trench run (flying along surface)
- FTL (subsystem targeting)

**v2 Boss Design Note:**
Bosses are THE reason to bring torpedoes. They're the ammo check. If you spent all your heavy ordnance on lesser enemies, you won't have enough for the boss. This creates a run-long tension: "save my torpedoes for the boss, or use them now to survive?"

---

### Boss 1: The Behemoth (Belt Boss)

**Visual:**
- Massive asymmetric hull
- Welded plates, industrial
- Orange/yellow lights
- Looks cobbled together

**Scale:**
4-5x player ship (fills 30% of screen)

**HP:**
- Total: 5,000
- Subsystems: 500 each (x6)
- Core: 2,000

**Phase 1: External Assault**

**Subsystems:**
1. Forward Cannons (x2) - Heavy slow shots
2. PDC Turrets (x2) - Rapid fire, shoots down YOUR missiles
3. Fighter Bays (x2) - Spawns scout fighters

**Mechanics:**
- Turrets track player
- Must fly around ship to target all subsystems
- Its PDCs will shoot down your missiles (must use kinetics or get close)
- Fighters harass throughout

---

**Phase 2: Hull Breach**

**Subsystems destroyed, hull cracks open.**

**New Mechanics:**
- Internal explosions (AOE damage zones)
- Venting atmosphere (pulls player toward hull)
- Debris ejected (physics hazards)

**New Target:**
- Reactor Shielding (1,000 HP)
- Must destroy to expose core

---

**Phase 3: Core Exposed**

**Reactor visible, critical state.**

**Mechanics:**
- Boss fires wildly (desperation pattern)
- Massive AOE attacks
- Time limit (30 seconds before self-destruct)

**Final Target:**
- Reactor Core (2,000 HP)
- Glowing weak point
- This is where your remaining torpedoes go

**Victory:**
- Massive explosion
- Debris field
- Bonus data earned

---

### Boss 2: The Bastion (UN Boss)

**Visual:**
- Symmetrical carrier design
- Blue/white color scheme
- Clean military lines
- Multiple hangar bays

**Scale:** 5-6x player ship

**HP:**
- Total: 7,500
- Subsystems: 750 each (x6)
- Core: 3,000

**Phase 1: Fighter Screen**
- 4 Hangar bays continuously spawn fighters
- 2 Shield generators make hull invulnerable
- Must destroy generators while managing fighter swarm
- Ammo discipline critical - don't waste ordnance on fighters

**Phase 2: Broadside**
- Ship rotates, exposes broadside missile batteries
- Massive missile barrage (must use countermeasures or dodge)
- Point defense grid shoots down YOUR incoming projectiles
- Must close to PDC range or use beam weapons

**Phase 3: Ramming Speed**
- Boss accelerates toward player
- Core exposed during charge
- Must damage core while avoiding collision
- Newtonian physics: boss has momentum, can be dodged

---

### Boss 3: The Sovereign (Mars Boss)

**Visual:**
- Sleek aggressive design
- Red/black color scheme
- Sharp angles, high-tech

**Scale:** 4x player ship (smaller but deadlier)

**HP:**
- Total: 6,000
- Subsystems: 600 each (x6)
- Core: 2,400

**Phase 1: Precision Strikes**
- Boss MOVES (unique among bosses)
- Highly accurate railgun batteries
- Must destroy targeting arrays to reduce accuracy
- Boost drives let it reposition - you can't just orbit

**Phase 2: Experimental Weapons**
- Energy beam sweeps across arena (must dodge vertically)
- Deploys seeker mines
- Teleports short distances (repositions unpredictably)

**Phase 3: Overload**
- All weapons fire simultaneously
- Erratic movement
- High damage output but systems failing
- Race to destroy core before it kills you

---

### Boss 4: ??? (Endgame Boss)

**Visual:**
- Corrupted/glitched appearance
- Shifting geometry
- No consistent form

**This is you. Fighting yourself.**
- Uses YOUR fitted loadout against you
- Mimics your piloting patterns (from run data)
- The ultimate test

---

## Meta Progression

### Data Economy

**Sources:**
- Survival time: 1 GB/minute
- Enemy kills: 0.1-0.5 GB each (small bonus)
- Completing objectives: 2-5 GB each
- Boss kills: 10 GB (first time), 5 GB (repeat)
- Extraction bonus: 3 GB (only if you extract successfully)
- Secret discoveries: 5-10 GB

**Average earnings per run:**
- Failed run (5 min): 5-8 GB
- Decent run (10 min): 12-18 GB
- Full run (15 min extraction): 20-30 GB
- Extended run (boss kill): 35-50 GB

---

### Spending Categories

#### 1. Module Unlocks

Unlocking a module makes it available in the fitting screen permanently.

**Tier 1 (5-10 GB each):**
- PDC Mk-II, Railgun Mk-I, Light Armor
- Standard Fuel Tank, Chaff Launcher
- Basic reliable equipment

**Tier 2 (15-30 GB each):**
- Railgun Mk-II, Missile Rack Extended, Beam Laser
- Medium Armor, Reactive Armor, ECM Suite
- Extended Fuel Tank, Targeting Computer
- Meaningful upgrades

**Tier 3 (40-80 GB each):**
- Gauss Cannon, Torpedo Mk-II, Cutting Beam
- Stealth Coating (Mars), Drone Bay, Sensor Array
- Drop Tanks, Coolant System
- Build-defining equipment

**Tier 4 (100-200 GB each):**
- Nuclear Torpedo, Prototype Cloak
- MCRN Experimental Thruster, Adaptive Armor
- Experimental slot modules
- Late-game power

---

#### 2. Ship Unlocks

**Faction Ships (Automatic at milestones):**
- Belt ships: Prospector free, others 30-50 GB
- UN ships: Unlock faction at Run 30, individual ships 30-50 GB
- Mars ships: Unlock faction at Run 100, individual ships 50-100 GB

---

#### 3. AI Upgrades (Quality of Life)

**Tier 1 (10 GB each):**
- **Threat Analysis**: More detailed threat board info
- **Salvage Protocols**: +15% data from kills
- **Approach Vectors**: Enemies detected earlier

**Tier 2 (50 GB each):**
- **Combat Telemetry**: Damage numbers visible
- **Fuel Optimizer**: 10% fuel efficiency
- **Loadout Memory**: Save/load fitting presets

**Tier 3 (200 GB each):**
- **Predictive Modeling**: Threat timelines show attack patterns
- **Autopilot Assist**: AI can execute basic evasive maneuvers
- **Neural Link**: Slightly faster weapon gimbal tracking

---

### Progression Milestones

**Run 1:**
- Belt Prospector, basic PDCs, light armor
- Learning to fly and shoot

**Run 10:**
- ~80 GB accumulated
- Railgun unlocked, first real loadout decisions
- Starting to understand resource management

**Run 30:**
- ~400 GB accumulated
- UN faction unlocks
- Multiple viable loadouts
- Feeling competent

**Run 50:**
- ~800 GB accumulated
- Tier 2 modules available
- Theory-crafting loadouts
- Narrative hints building

**Run 100:**
- ~1,800 GB accumulated
- Mars faction unlocks
- Tier 3 modules accessible
- Truth becoming apparent

**Run 150:**
- ~3,000 GB accumulated
- Most modules unlocked
- Optimizing loadouts for specific challenges
- Narrative climax approaching

**Run 200+:**
- Endgame
- Experimental modules
- Playing for perfect runs and secret ending
- Mastery

---

## UI/UX

### HUD Elements

**Core HUD (Always Visible):**
```
┌────────────────────────────────────────────────────┐
│ [Hull: ████████░░ 640/800]                         │ Top Left
│ [Clone #248]                                       │
│                                                    │
│                                                    │
│                  [CENTER PLAY AREA]                │
│                                                    │
│                                                    │
│ [PDC: ████████░░ 847/1200]   [Time: 12:34]       │ Bottom Left
│ [Rail: ████░░░░░░ 3/8]       [Fuel: ███░░ 142]   │
│ [Msle: ██░░░░░░░░ 1/6]      [Vel: 87 m/s]       │
│ [Torp: █░░░░░░░░░ 1/3]      [Throttle: 60%]     │
└────────────────────────────────────────────────────┘
```

**Threat Board (Toggle with Tab):**
```
┌─ THREAT BOARD ──────────────────────────┐
│ [!] TORPEDO    ETA 23s  Bearing 180°   │
│ [*] FRIGATE    ETA 47s  Bearing 045°   │
│ [ ] FIGHTER    ETA 62s  Bearing 270°   │
│ [ ] DESTROYER  ETA 89s  Bearing 310°   │
│                                         │
│ TOTAL THREATS: 4                        │
│ AMMO STATUS: PDC 71% | RAIL 38%       │
│ FUEL STATUS: 35%                       │
└─────────────────────────────────────────┘
```

---

**Fitting Screen:**
```
╔══════════════════════════════════════════════════╗
║              CLONE #248 - FITTING                ║
║                                                  ║
║  SHIP: [< The Prospector >]                     ║
║                                                  ║
║  ┌─ FORWARD ──────────────────────────────┐     ║
║  │ [M] PDC Array Mk-II      1500 rds     │     ║
║  │ [M] Railgun Mk-I         8 slugs      │     ║
║  └────────────────────────────────────────┘     ║
║  ┌─ SIDE ─────────────────────────────────┐     ║
║  │ [S] Missile Rack          6 missiles   │     ║
║  └────────────────────────────────────────┘     ║
║  ┌─ REAR ─────────────────────────────────┐     ║
║  │ [S] Chaff Launcher        4 charges    │     ║
║  └────────────────────────────────────────┘     ║
║  ┌─ SYSTEMS ──────────────────────────────┐     ║
║  │ [M] Light Armor           +200 hull    │     ║
║  │ [M] Extended Fuel Tank    +200 fuel    │     ║
║  │ [S] Targeting Computer    +10° gimbal  │     ║
║  │ [S] Coolant System        -40% heat    │     ║
║  └────────────────────────────────────────┘     ║
║                                                  ║
║  Mass: 2,680 / 3,000 kg                        ║
║  Hull: 1,000  Fuel: 600                        ║
║                                                  ║
║  [DEPLOY]  [SWAP SHIP]  [PRESETS]               ║
╚══════════════════════════════════════════════════╝
```

---

**Debrief Screen:**
```
╔══════════════════════════════════════════════════╗
║              SIGNAL LOST                         ║
║         TRANSMISSION TERMINATED                  ║
║                                                  ║
║  CLONE #248                                      ║
║  Survival Time: 14:47                            ║
║  Threats Neutralized: 12                         ║
║                                                  ║
║  RESOURCE EXPENDITURE:                           ║
║  • PDC Rounds:   1,047 / 1,500 fired            ║
║  • Railgun Slugs: 7 / 8 fired                   ║
║  • Missiles:      5 / 6 launched                 ║
║  • Fuel:          94% consumed                   ║
║  • Hull:          78% damaged                    ║
║                                                  ║
║  DATA RECOVERED: 18.4 GB                        ║
║  • Survival: 14.8 GB                            ║
║  • Kills: 2.1 GB                                ║
║  • Extraction: 0 GB (FAILED)                    ║
║  • Objectives: 1.5 GB                           ║
║                                                  ║
║  NEW UNLOCK AVAILABLE: Railgun Mk-II            ║
║                                                  ║
║  DEPLOYING CLONE #249...                         ║
║                                                  ║
║  [SPACE to continue]                             ║
╚══════════════════════════════════════════════════╝
```

---

### Menu Flow
```
MAIN MENU
├─ [DEPLOY] → Fitting Screen → Ship Selection → Run Start
├─ [DATA ARCHIVE] → Module Unlocks / Ship Unlocks / AI Upgrades
├─ [TERMINAL] → Logs/Narrative
├─ [SETTINGS]
└─ [QUIT]

FITTING SCREEN
├─ Ship Selection (swap between unlocked ships)
├─ Weapon Slots (drag-and-drop unlocked weapons)
├─ System Slots (drag-and-drop unlocked systems)
├─ Mass/Stats Summary
├─ Saved Presets
└─ [DEPLOY] button

DATA ARCHIVE
├─ Modules (weapons, systems - unlock with GB)
├─ Ships (unlock with GB or story milestones)
├─ AI Upgrades (quality of life)
└─ Total Data / Completion %

TERMINAL
├─ Mission Logs (tutorial info)
├─ Classified Logs (story progression)
└─ Clone Records (stats, lore)
```

---

### Visual Design Philosophy

**Geometry Wars Aesthetic:**
- Black background
- Neon geometric shapes
- Particle trails
- Bloom effects
- Screen shake on impacts

**UI Style:**
- Minimalist, clean
- Cyan/white text
- Sci-fi typeface (monospace)
- Subtle glitch effects (late game)
- High contrast for readability

**Color Coding:**
- Player: Cyan
- Allies (drones): Green
- Enemies: White (early) -> Red (when truth known)
- Projectiles: Weapon-dependent
- Threats on approach: Orange/yellow warning
- Critical threats: Red pulsing

**v2 Visual Additions:**
- Threat approach lines (visible vectors showing incoming enemy paths)
- Ammo counters integrated into weapon reticle
- Fuel gauge prominent (survival depends on it)
- Bearing indicators around screen edge (where threats are coming from)

---

## Audio Design

### Music

**Composed by developer (you):**

**Style:**
- Industrial metal / trap fusion
- 140 BPM
- Heavy, aggressive
- Sci-fi synth elements

**Adaptive Layers:**

**Base Layer (Always):**
- Drums, bass
- Maintains pulse

**Tension Layer (Threats approaching):**
- Builds with number of active threats
- More threats = more layers
- Creates mounting dread

**Combat Layer (During engagement):**
- Guitars, synths
- Peaks during multi-vector engagements

**Boss Layer (Boss fights):**
- Full orchestration
- Breakdown on phase transitions

**Corruption Layer (18+ minutes):**
- Distorted, glitchy
- Unsettling undertones

---

**Track List (Estimated):**

1. **Deploy** - Fitting screen / menu music (methodical, preparation feel)
2. **First Contact** - Early combat (controlled, professional)
3. **Escalation** - Mid combat (building pressure)
4. **Critical** - Late combat (desperate, resources low)
5. **Capital** - Boss theme
6. **The Behemoth** - Belt boss specific
7. **The Bastion** - UN boss specific
8. **The Sovereign** - Mars boss specific
9. **Signal Static** - Corruption theme (18-22 min)
10. **The Truth** - Revelation sequence
11. **Break The Cycle** - New Game+ theme

**Total Runtime:** 30-40 minutes of music

---

### Sound Effects

**Weapon Sounds:**

**PDCs:**
- Rapid mechanical clatter
- Brass casings (even in space, rule of cool)
- Muzzle flash crackle
- *Click* when magazine empties (dread sound)

**Railgun:**
- Charge-up hum (building tension)
- Electromagnetic crack (satisfying release)
- Impact thunder
- Each shot should feel like it COSTS something

**Missiles:**
- Launch whoosh
- Rocket exhaust roar (fading with distance)
- Explosion bass
- Lock-on tone before launch

**Torpedoes:**
- Heavy mechanical clunk (tube loading)
- Deep bass launch
- Massive explosion on impact
- Should feel weighty and precious

**Beam Laser:**
- Sustained electric hum
- Sizzle on contact
- Power-down whine
- Heat warning beep when overheating

---

**Ship Sounds:**

**Engine:**
- Idle hum (varies by throttle)
- Thrust roar (when accelerating)
- Boost scream (when boosting - expensive, dramatic)
- Fuel warning chime (when low)

**RCS:**
- Short burst pops
- Direction-dependent

**Collision:**
- Metal crunch
- Alarms (if critical damage)

---

**Resource Warning Sounds:**
- Ammo low: Subtle click pattern change
- Ammo empty: Hard metallic click (no more rounds)
- Fuel low: Warning chime, increasing urgency
- Fuel empty: Engine dies. Silence. Terrifying.
- Hull critical: Klaxon, metal groaning

---

**UI Sounds:**

**Fitting Screen:**
- Module snap into slot (satisfying click)
- Mass warning (when approaching limit)
- Swap sound (removing module)

**Threat Board:**
- New threat detected: Sonar ping
- Threat upgraded to priority: Warning tone
- Threat eliminated: Confirmation chime

**Menu:**
- Cursor movement (soft beep)
- Selection confirm (clunk)
- Back/cancel (reversed beep)

**Death:**
- Static burst
- Transmission cut
- Silence (2 seconds)
- Reboot sequence

---

### AI Voice

**Ship AI Character:**

**Voice Type:**
- Synthetic, slightly robotic
- Clear, professional
- Text-to-speech with personality tweaks

**Delivery:**
- Early runs: Professional, detached
- Mid runs: Concerned, invested
- Late runs: Protective, desperate
- Post-truth: Complicit, apologetic

**Key Lines (Examples):**

**First deployment:**
"Clone #1. Welcome to the program. Loadout verified. Deploying."

**Ammo warning:**
"PDC ammunition at 20%. Recommend fire discipline."

**Fuel warning:**
"Fuel reserves critical. Minimize burn operations."

**Multiple threats:**
"Multiple contacts. Prioritize. You can't engage everything."

**Boss spawn:**
"Capital-class signature. This is what you brought the torpedoes for."

**18:00 mark:**
"Neural corruption warning. Recommend immediate extraction."

**20:00 mark:**
"I'm losing you. Please. Come back."

**22:00 mark:**
"I understand now. I'm sorry. I'm so sorry."

---

## Technical Specifications

### Engine

**Primary:** Pygame (Python)
- Easy iteration
- AI-assisted development
- Leverages your Python expertise
- Prototype for testing core feel

**Libraries:**
- `pygame` - Core game engine
- `pymunk` - 2D physics
- `numpy` - Math operations
- `json` - Data storage / save files
- `random` - Procedural generation

---

### Physics Implementation

**Pymunk Setup:**
```python
import pymunk

# Space setup
space = pymunk.Space()
space.gravity = (0, 0)  # No gravity in space
space.damping = 0.98     # Very minimal friction

# Ship body
ship_body = pymunk.Body(mass=ship_total_mass, moment=1000)
ship_body.position = (WIDTH/2, HEIGHT/2)

# Ship shape (collision)
ship_shape = pymunk.Circle(ship_body, radius=20)
ship_shape.friction = 0.1
ship_shape.collision_type = COLLISION_PLAYER

space.add(ship_body, ship_shape)
```

---

**Movement System (with fuel):**
```python
class Ship:
    def __init__(self, fitting):
        self.throttle = 0.0
        self.thrust_power = 5000
        self.rcs_strength = 1000
        self.fuel = fitting.total_fuel
        self.fuel_rate = fitting.total_mass / BASE_MASS  # heavier = more fuel/burn

    def update(self, dt):
        if self.fuel <= 0:
            return  # Ballistic. No control. Good luck.

        # Apply main thrust (costs fuel)
        if self.throttle > 0:
            thrust = self.forward_direction * self.throttle * self.thrust_power
            self.body.apply_force_at_local_point(thrust, (0, 0))
            self.fuel -= self.thrust_power * self.throttle * dt * self.fuel_rate

        # Apply RCS (costs less fuel)
        if self.rcs_input:
            rcs = self.rcs_direction * self.rcs_strength
            self.body.apply_force_at_local_point(rcs, (0, 0))
            self.fuel -= self.rcs_strength * dt * self.fuel_rate * 0.3
```

---

### Data Architecture

**Save File Structure (JSON):**
```json
{
  "player_data": {
    "total_runs": 248,
    "total_data_gb": 487.3,
    "total_playtime_seconds": 64800,
    "highest_run_time": 934,
    "secret_ending_unlocked": false
  },
  "unlocks": {
    "modules": [
      "pdc_mk2",
      "railgun_mk1",
      "light_armor",
      "standard_fuel_tank",
      "chaff_launcher"
    ],
    "ships": [
      "belt_prospector",
      "belt_cutter",
      "un_corvette"
    ],
    "ai_upgrades": [
      "threat_analysis",
      "salvage_protocols"
    ],
    "factions": [
      "belt",
      "un"
    ]
  },
  "narrative_progress": {
    "current_act": 2,
    "logs_unlocked": [
      "log_001",
      "log_045",
      "log_classified_01"
    ],
    "truth_discovered": false
  },
  "saved_loadouts": [
    {
      "name": "Standard Combat",
      "ship": "belt_prospector",
      "forward": ["pdc_mk2", "railgun_mk1"],
      "side": ["missile_rack"],
      "rear": ["chaff_launcher"],
      "systems": ["light_armor", "extended_fuel", "targeting_computer", "coolant"]
    }
  ],
  "settings": {
    "music_volume": 0.8,
    "sfx_volume": 0.9,
    "control_scheme": "keyboard_mouse"
  }
}
```

---

### Performance Targets

**Target FPS:** 60 (stable) / 120 (stretch)

**Entity Limits:**
- Player projectiles: 200 active
- Enemy projectiles: 500 active
- Enemies on screen: 10-12 simultaneous (by design, not limitation)
- Particles: 3000 active
- Threat indicators: 20 tracked

**Optimization Strategies:**
- Object pooling (projectiles reused)
- Spatial hashing (collision optimization)
- Off-screen culling (don't render invisible)
- Particle system limits (cap effects)

---

### Screen Resolution

**Target:** 1920x1080 (16:9)
**Minimum:** 1280x720
**Windowed/Fullscreen:** Both supported

---

## Development Roadmap

### Phase 1: Core Prototype Rework (Weeks 1-4)

**Week 1: Strip & Rebuild Core Loop**
- [ ] Remove XP/leveling system
- [ ] Remove auto-fire and auto-lock
- [ ] Implement finite ammo system
- [ ] Implement fuel consumption
- [ ] Add resource HUD elements

**Week 2: Fitting System**
- [ ] Basic fitting screen (select weapons/systems)
- [ ] Mass budget calculation
- [ ] Module slot system (S/M/L)
- [ ] Deploy with fitted loadout

**Week 3: Enemy Rework**
- [ ] Reduce enemy count, increase individual threat
- [ ] Implement threat approach timelines
- [ ] Multi-vector spawning (not just "toward player")
- [ ] Basic threat board UI

**Week 4: Feel Pass**
- [ ] Manual weapon firing (no auto)
- [ ] Weapon firing arcs tied to ship orientation
- [ ] Fuel warning system
- [ ] Ammo depletion feedback
- [ ] "Numbers going down" feel validation

**Milestone:** Core loop feels right - deploy, manage resources, extract/die

---

### Phase 2: Content & Systems (Weeks 5-8)

**Week 5: Ship Variety**
- [ ] 3 Belt ships with different slot layouts
- [ ] Ship handling differences (thrust-to-weight, turn rate)
- [ ] Ship selection in fitting screen

**Week 6: Weapon Variety**
- [ ] 5 weapon types implemented (PDC, Railgun, Missile, Torpedo, Beam)
- [ ] Weapon variants (Mk-I, Mk-II)
- [ ] Defensive systems (armor, fuel tanks, countermeasures)

**Week 7: Meta Progression**
- [ ] Data (GB) earning and tracking
- [ ] Module unlock screen
- [ ] Ship unlocks
- [ ] Persistence between runs

**Week 8: Enemy Variety & First Boss**
- [ ] 4 enemy types (Scout, Skirmisher, Heavy, Cruiser)
- [ ] Enemy behavioral variety
- [ ] First boss (The Behemoth)
- [ ] Boss subsystem targeting

**Milestone:** Complete fitting -> deploy -> fight -> earn -> unlock loop

---

### Phase 3: Narrative Integration (Weeks 9-12)

**Week 9: Terminal & Logs**
- [ ] Terminal log system
- [ ] First 10 logs written
- [ ] Log unlock conditions
- [ ] Narrative UI

**Week 10: AI Dialogue**
- [ ] AI dialogue system
- [ ] Context-based dialogue (ammo warnings, fuel warnings, threat callouts)
- [ ] Clone number tracking
- [ ] AI personality evolution across runs

**Week 11: Factions**
- [ ] UN faction unlock (Run 30)
- [ ] 3 UN ships
- [ ] UN-specific modules
- [ ] Second boss (The Bastion)

**Week 12: Secret Ending**
- [ ] Secret ending framework
- [ ] 18-22 minute sequence
- [ ] Visual corruption effects
- [ ] Revelation scene

**Milestone:** Narrative spine complete

---

### Phase 4: Mars & Polish (Weeks 13-16)

**Week 13: Mars Faction**
- [ ] Mars faction unlock (Run 100)
- [ ] 3 Mars ships
- [ ] Mars-specific modules (stealth, experimental)
- [ ] Third boss (The Sovereign)

**Week 14: Advanced Systems**
- [ ] Drone bay system
- [ ] Experimental slot modules
- [ ] AI upgrades (quality of life)
- [ ] Saved loadout presets

**Week 15: New Game+**
- [ ] New Game+ mode
- [ ] True ending sequence
- [ ] Facility boss
- [ ] Pacifist gameplay variant

**Week 16: Juice & Polish**
- [ ] Screen shake, particles
- [ ] Sound effects integration
- [ ] UI polish
- [ ] Balance pass (ammo counts, fuel rates, enemy HP)

**Milestone:** Feature complete

---

### Phase 5: Audio & Final Polish (Weeks 17-20)

**Week 17-18: Music & Audio**
- [ ] Compose 5 core tracks + boss themes
- [ ] Adaptive music system (layers based on threat count)
- [ ] Resource warning sounds
- [ ] Weapon sounds (especially the empty-click)

**Week 19: Playtest & Balance**
- [ ] Full playtest
- [ ] Balance: Is fuel too scarce? Too generous?
- [ ] Balance: Is ammo forcing interesting decisions?
- [ ] Balance: Are runs the right length?
- [ ] Bug fixes

**Week 20: Ship**
- [ ] Steam/itch.io page
- [ ] Trailer
- [ ] Final builds

**Milestone:** Ready to ship

---

### Phase 6: Launch & Post-Launch (Weeks 21+)

**Week 21:** itch.io soft launch
**Week 22-24:** Balance patches, bug fixes, community feedback
**Week 25:** Steam launch
**Post-Launch:** Plan for 3D sequel (if successful)

---

## Success Metrics

### Development Success
- Feature complete prototype (Phase 1) that FEELS right
- "Numbers going down" creates tension, not frustration
- Ship fitting is engaging (players theory-craft loadouts)
- Cascading pressure creates "slow but rushed" feel
- Ship on time (20 weeks)

### Commercial Success
**Modest (Goal):**
- 5,000-10,000 copies sold
- $50k-150k gross revenue
- Positive reviews (80%+)
- Active community

**Strong (Stretch):**
- 20,000-50,000 copies sold
- $200k-500k gross revenue
- Featured on Steam
- Speedrun community / loadout theory-crafting community

**Breakout (Dream):**
- 100,000+ copies sold
- $1M+ gross revenue
- Cult classic status
- Funds 3D sequel development

### Player Engagement
- Average playtime: 15+ hours
- Completion rate: 20%+ (standard ending)
- Secret ending rate: 5%+
- Loadout sharing / community builds
- "One more run" factor

---

## Design Pillars Checklist

**Before shipping, ensure:**

### 1. Cascading Pressure
- [ ] Individual threats feel solvable
- [ ] Overlapping threats create panic
- [ ] Threat timelines are readable
- [ ] Difficulty comes from complexity, not speed

### 2. Momentum & Commitment
- [ ] Every burn feels like a decision
- [ ] Ship orientation matters for combat
- [ ] Physics create emergent tactical situations
- [ ] Running out of fuel is terrifying, not frustrating

### 3. Depletion & Scarcity
- [ ] Ammo decisions are interesting (not just "shoot less")
- [ ] Fuel creates movement decisions (not just "move less")
- [ ] Hull damage creates escalating tension
- [ ] Empty magazines feel like dread, not failure

### 4. Ship Fitting
- [ ] Fitting screen is engaging (players spend time here)
- [ ] Loadout choices create different play experiences
- [ ] Tradeoffs are real (no obvious "best" loadout)
- [ ] Unlocking new modules is exciting

### 5. Existential Horror
- [ ] Standard ending works
- [ ] Secret ending is mind-blowing
- [ ] Narrative is gradual reveal
- [ ] Truth recontextualizes everything

---

## Final Notes

### What Makes This Game Special

1. **"Numbers go down"** - Inverts the power fantasy. Tension through depletion.
2. **Newtonian physics as tactics** - Every burn is a commitment. Physics ARE the decision engine.
3. **Ship fitting depth** - The hangar is where strategy lives. Runs are execution.
4. **Cascading pressure** - Slow threats that overlap into panic. The Expanse torpedo problem.
5. **Narrative twist** - Recontextualizes the entire experience.

### What Changed From v1

1. **Removed:** In-run leveling, XP/scrap pickups, auto-fire, auto-lock, horde spawning
2. **Added:** Ship fitting, finite ammo/fuel, threat timelines, manual weapons
3. **Changed:** Enemy philosophy (fewer/smarter), progression (between runs only), combat pacing (slow but rushed)
4. **Kept:** Narrative, factions, ships, physics, aesthetic, bosses, meta progression (Data/GB)

### What Could Go Wrong

1. **Too punishing** - Mitigate with generous early-game ammo/fuel, clear feedback
2. **Fitting screen too complex** - Start simple, add modules gradually via unlocks
3. **Not enough "feel good" moments** - Landing a torpedo should feel AMAZING
4. **Fuel too stressful** - Tune carefully, fuel should create decisions not frustration
5. **Missing the arcade fun** - The satisfaction comes from clean execution, not power fantasy

### What Makes This Shippable

1. **Clear identity** - This is NOT Vampire Survivors. It's FTL meets The Expanse.
2. **Existing prototype** - Physics engine, rendering, core architecture exists
3. **AI leverage** - Fast iteration on systems
4. **Simpler enemy system** - Fewer enemies = less to build and balance
5. **Fitting system** - One screen replaces entire upgrade/evolution system

---

## Appendix: Key Quotes

**From design sessions:**

> "Kill your darlings. Let this game be this game."

> "The geometric aesthetic isn't a limitation. It's the horror."

> "They weren't the enemy. We were."

> "Numbers go down. Everything is running out."

> "I have time... I have time... I DON'T have time for all of this."

> "A perfectly fitted ship with an empty magazine is just a coffin with a window."

---

## Document Version Control

**Version 1.0** - February 11, 2026
- Initial GDD creation
- Vampire Survivors-inspired design

**Version 2.0** - February 14, 2026
- Complete design pivot
- Removed in-run leveling, added ship fitting
- "Numbers go down" philosophy
- Cascading pressure instead of horde survival
- FTL/Eve Online/The Expanse identity

**Status:** Pre-Production (Prototype Rework)
**Target Ship Date:** July 2026 (20 weeks from v1 start)
**Platform:** PC (itch.io, then Steam)
**Price Point:** $10-15

---

**END OF DOCUMENT**

---
