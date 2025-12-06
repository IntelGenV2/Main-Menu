<span style="color:#57d4ff; font-size:2.1em; font-weight:700;">Local Machine - Single Player Mode</span>

## 1. Game Structure

- Represents a single 90s-era PC.
- The motherboard is a **fixed, hand-crafted 3D map** for every player.
- Districts (zones) themed as modules:
  - PSU
  - BIOS (CMOS → BIOS → UEFI)
  - CPU
  - RAM
  - HDD/SSD (+ SATA controller)
  - PCI (ISA → PCI → PCIe)
  - GPU (VGA → DVI → HDMI → DP)
  - Sound Card
  - Network Hardware (Modem → Ethernet → Wi-Fi)
  - Fans (+ temp sensors)
  - Motherboard (discrete parts / traces)
  - Serial (System Info UI)
  - Parallel (dot-matrix → inkjet → laser)
  - USB (1.0 → 2.0 → 3.0 → USB type C (Entrocore access, final dungeon))
  - Co-Processor (FPU → DSP → Neural Processor)
  - Cache (L1 → L2 → L3)
  - RTC (Basic → Enhanced → Advanced)

**Important rule**  
- The **map layout never changes** between players.
- What does change:
  - Which specific components are broken.
  - Which hazards are present.
  - Enemy spawns and some values.

---

## 2. System Overseer

- Angry, sarcastic, philosophical entity that:
  - Explains systems by insulting your intelligence.
  - Reacts to deaths, bad repairs, botched voltage choices.
- Appears as:
  - Animated 2D character on CRTs.
  - Voice-over during gameplay.
  - Occasional intrusive on-screen messages.

---

## 3. Player, Camera & Controls

### 3.1 Player Avatar

- A tiny **diagnostic robot**:
  - Walks along traces and component housings.
  - Wears a backpack (tool & item storage).

### 3.2 Camera

- **3D, First-Person**.
- Whole game viewed through the bot's "visor."
  - Slight curvature.

### 3.3 Controls

- **Walk** – W / A / S / D  
- **Run** – Hold Shift (stamina-limited)  
- **Toggle Flashlight** – F  
- **Interact** (switches, components, terminals) – Right Click  
- **Shoot / Attack** – Left Click  
- **Swap between weapon/tool/component** – Mouse Scroll  
- **Select specific item** – Number keys 1–0  
- **Open BIOS menu** – interact with BIOS terminal.

---

## 4. Core Loop

1. **Explore a District**  
   - Walk the motherboard to the module you want to repair (PSU, CPU, RAM, etc.).
2. **Get Tools, Weapons & Parts**  
   - Scavenge damaged components and raw materials to sell.
   - Buy tools, weapons and new components with Bits.
3. **Shut Down Safely**  
   - Turn off the PSU before working on sensitive modules.
4. **Repair Module**  
   - Use tools (multimeter, soldering iron, etc.) to fix traces, chips, sockets, connectors.
5. **Upgrade Supporting Systems**  
   - Upgrade PSU and Fans (if repaired) to support new power draw or heat.
6. **Bring System Back Online**  
   - Turn PSU back on.
   - Visit BIOS to configure the repaired hardware.
7. **Defend Repairs**  
   - Fight off enemies that spawn at broken areas.
    - They can destroy what you have fixed!
8. **Repeat**  
   - Choose the next module; gradually stabilize the entire machine.
   - You can work on multiple modules at once

---

## 5. Systems & Progression

### 5.1 Inventory

- 3 base slots:
  - 1 weapon
  - 1 tool
  - 1 component slot
- Additional slots unlocked via:
  - **RAM module quest** (more runtime memory (aka, how long you can keep the PSU on before **stack overload** happens)).
  - **HDD/SSD quest** (more storage capacity).

### 5.2 Economy

- Currency: **฿ Bits**.
- Earned by:
  - Killing enemies.
  - Repairing components.
  - Completing module quests.
  - Collecting and selling broken components
- Spent on:
  - Tools.
  - Weapons.
  - Components and crafting parts.
  - Upgrades (where appropriate).

### 5.3 Death & Retry

- Hazards: fire, explosions, sparks, toxic/acid clouds, arcs, falls.
- On death:
  - Respawn at USB district.
  - Flashlight battery stays as it was.
  - Inventory drops at death location (can be recovered).
- You don't "fail" a module forever by making mistakes:
  - If you botch a repair, you can re-attempt (might cost more parts/Tools).

---

## 6. Tools & Weapons

### 6.1 Weapons (Baseline)

- **Skypiercer** – Pistol  
  - Accuracy: 2/5  
  - Damage: 10 HP  
  - Magazine: 5 bullets  
  - Reload: 3 s (≈ 500 ms per bullet)

- **Thundercoil** – Laser Beam  
  - Accuracy: 4/5  
  - Damage: 50 HP  
  - Magazine: 1 beam  
  - Reload: 6 s

- **Shockblade** – Lightning Sword  
  - Accuracy: 5/5  
  - Damage: 10 HP  
  - Cooldown: 2 s

- **Ball of Lightning** – Grenade  
  - Accuracy: 1/5  
  - Damage: 70 HP  
  - Magazine: 1 grenade  
  - Reload: 10 s

### 6.2 Tools

Core tool list:

- **Multimeter** – Measure voltage/current/resistance; critical for traces, caps.  
- **Wire Strippers** – Remove insulation from wires.  
- **Soldering Iron** – Attach components to board.   
- **Chip Puller / Insertion Tool** – Remove/insert ICs safely (BIOS, ROMs, CPU, chips).  
- **Diagnostic Tool** – Read error codes from diagnostic ports.  
- **Desoldering Gun** – Remove damaged components.  
- **Oscilloscope** – Analyze signal integrity.  
- **Trace Repair Pen** – Fix broken traces.  
- **Contact Cleaner** – Clean oxidized contacts.  
- **Flashlight** – Your main light source until districts are powered.

#### Tactile Tool Handling (First-Person)

- Soldering Iron:
  - Heat-up time.
  - Tip glows and shimmers the air.
- Desoldering Gun:
  - Visible vacuum pulse effect when used.
- Oscilloscope:
  - Deploys as a small stand-up device you connect leads to.

#### Voltage & Recharge

Tools use specific voltage rails via broken/working traces:

- Multimeter – 5 V (4 uses before recharge)  
- Soldering Iron – 12 V (2 uses)  
- Diagnostic Tool – 5 V (5 uses)  
- Desoldering Gun – 12 V (2 uses)  
- Oscilloscope – 5 V (2 uses)  
- Flashlight – 5 V (3 min per full charge)

If you connect a tool to **wrong voltage** or a dangerous point:

- Chance to destroy the tool.
- Chance to cause an arc/explosion.
- Overseer mocks you.

---

## 7. Modules & Quests

All module details in **Modules.md**

---

## 8. Enemies

### 8.1 Base Enemies

- **Kernel Titan**  
  - Ball of red lightning, with 3–5 soldier orbs.
  - 100 HP (25 per soldier).
  - 25 HP per second damage total (5 per soldier per 500 ms).
  - Spawns from broken capacitors.
  - Long-range lightning shots at player and components.
  - Drops ฿100 Bits.

- **SynErr**  
  - Distorted polygon entity.
  - 75 HP.
  - 30 HP every 2 seconds.
  - Spawns from faulty resistors.
  - Piercing melee attacks.
  - Drops ฿50 Bits.

- **Corflux**  
  - Mist of corrosion dust.
  - 50 HP.
  - 5 HP per 500 ms damage in contact.
  - Spawns from corroded traces/components.
  - Poisons player and nearby components.
  - Drops ฿25 Bits.

### 8.2 Difficulty Scaling

- Each completed module increases global difficulty by 1:
  - More frequent spawns.
  - Stronger hazard combos.

---

## 9. Lighting, Audio & Presentation

- **Flashlight**:
  - Main early game light.
  - 5 V rail, limited duration per charge.

- **District Lighting**:
  - Controlled by PSU and Motherboard health.
  - Fixing a district's Motherboard → its "city lights" activate (if PSU is on).

- **Audio**:
  - Starts as basic 8-bit.
  - Improves as Sound module is repaired (see Modules.md, section 8).

- **CRT UI**:
  - Menus and BIOS on CRT-style screens.
  - HUD styled as retro monitor overlays.
  - Upgradeable (see Modules.md, section 7)

---

## 10. Achievements & Badges (Local Machine)

- **Entrocore Purged** – Beat Entrocore in Local Machine.  
- **Analog Only** – Complete a module with GPU still on VGA tier.  
- **Voltage Veteran** – Perform 50 high-risk voltage operations without exploding a tool.  

Rewards:
- Cosmetic CRT frames.
- Bot skins.
- Titles.
