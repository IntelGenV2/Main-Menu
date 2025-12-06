<span style="color:#57d4ff; font-size:2.1em; font-weight:700;">DataNET - Multiplayer Mode</span>

DataNET is the multiplayer mode of System Revival. It's a separate game mode where you and other players work together to repair remote computer systems.

---

## What is DataNET?

DataNET is accessed from your Local Machine (your single-player world) through the Network/Modem module. Think of it as traveling to other broken computers across a network.

**Key Features:**
- **Procedural Dungeons**: Each run generates a new random layout
- **Cooperative Play**: 2-6 players work together
- **Module-Themed Rooms**: Areas based on computer parts (PSU chambers, CPU halls, RAM vaults, etc.)
- **Main Goal**: Stabilize the remote system and deliver stored files to the Overseer
- **Special Challenges**: Survive DataNET mutators (random modifiers that change each run)

---

## How Your Local Machine Affects DataNET

Your single-player progress directly impacts your DataNET experience. If something is broken in your Local Machine, it affects DataNET too!

### Sound Card (see Modules.md, section 8)
- **Broken** → No voice chat or very low-quality voice chat
- **Fixed** → High-quality voice chat available

### USB / Ports (see Modules.md, section 17)
- **Broken** → No text chat or mixed up chat (some keys don't work)
- **Fixed** → Text chat works

### Graphics Card (see Modules.md, section 7)
- **Low tier (VGA/DVI)** → Black & white or glitchy visuals in DataNET
- **High tier (HDMI/DisplayPort)** → Full color, clear visuals
- Aim jitter, visual misalignment

### Network Hardware (see Modules.md, section 13)
- **Modem tier** → Simulated lag, connection issues, stutters, small lobbies (3 people)
- **Ethernet tier** → Less lag, faster matchmaking, lobbies are still small (4 people)
- **Wi-Fi tier** → Best connection, larger lobbies possible. (6 people)

### RAM / Storage (see Modules.md, sections 4 & 5)
- **Limited** → Smaller inventory, fewer tools available
- **Upgraded** → More inventory space, more tools

### CPU (see Modules.md, section 3)
- **CPU instability** → Weapon firing delays, "ghost shots" that don't register

**Tools and weapons** work the same way as in Local Machine, but voltage mechanics may be affected by DataNET mutators.

---

## Controls in DataNET

- **Text Chat** – Press T
  - Requires USB Module to be fixed in Local Machine
- **Voice Chat** – Press Q (push-to-talk)
  - Requires Sound Card Module to be fixed in Local Machine

---

## DataNET Structure

**Procedural Generation:**
- Each run creates a new random layout
- Rooms are themed around computer modules
- Layout changes every time you play

**Cooperative Objectives:**
- Players must work together
- Stabilize the remote system
- Deliver files to the Overseer

**Access Requirements:**
- Must have Network/Modem module repaired in Local Machine
- See Modules.md, section 13

---

## DataNET Mutators (Per-Run Modifiers)

Each DataNET run can randomly get 1-2 special modifiers that change gameplay:

### Voltage Surge
- **Effect**: Tools hit harder and repair faster
- **Risk**: Higher chance tools explode if misused
- **Reference**: See main blueprint for tool mechanics

### Static Storm
- **Effect**: More electrical shock hazards
- **Bonus**: Enemies drop more Bits (currency)

### Packet Loss
- **Effect**: Periodic input delay and rubber-banding (lag spikes)
- **Bonus**: Rare components are more common

### Corrosion Bloom
- **Effect**: Extra corrosion enemies and poison puddles
- **Risk**: Corrosion damage is higher
- **Reference**: See main blueprint for Corflux enemy details

### Thermal Drift
- **Effect**: Fans fight an ambient heat wave
- **Risk**: Overheating penalties happen more often
- **Reference**: See Modules.md, section 9 for cooling mechanics

**Important**: These mutators only affect DataNET, not your Local Machine.

---

## Enemies in DataNET

### Base Enemies (Same as Local Machine)
DataNET uses the same enemies as Local Machine:
- **Kernel Titan** - Ball of red lightning with soldier orbs
- **SynErr** - Distorted polygon entity
- **Corflux** - Mist of corrosion dust

### DataNET-Specific Enemies

**Packet Phantoms**
- Embodiment of network latency
- Cause delayed hits and positional stutters
- More common with lower-tier Network hardware (modem)

---

## Rewards / Achievements

**Completion Rewards:**
- Bits (currency)
- Rare components that can be used in Local Machine

**Achievements**
- Silent Runner
    - Complete a DataNET run with no text/voice chat
    - Requires broken USB/Sound Card in Local Machine

- Network Whisperer
    - Reach Wi-Fi tier (see Modules.md, section 13)
    - Complete 10 flawless DataNET runs

**Rewards:**
- Titles visible in DataNET lobbies
- Special cosmetics that appear in both Local Machine and DataNET

---

## Future Wishlist

- More DataNET enemy types and mutator combinations
- Additional procedural room types
- Expanded cooperative mechanics

---

## Quick Reference

**To Access DataNET:**
1. Fix Network/Modem module in Local Machine (see Modules.md, section 13)
2. Access DataNET from the Network area
3. Start with Modem tier, upgrade to Ethernet or Wi-Fi for better experience

**Remember:**
- Your Local Machine hardware state affects DataNET
- Fix modules in Local Machine to improve DataNET experience
- Mutators change each run - adapt your strategy!

