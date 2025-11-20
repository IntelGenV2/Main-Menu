<span style="color:#57d4ff; font-size:2.1em; font-weight:700;">System Revival - The Game</span>

# Overview
- System Revival is an isometric quest-based game.
- The goal of the game is to repair a computer made in the 90s.
- The entire adventure happens on the motherboard of the computer.
  - The motherboard is the map of the game.
- Repairing components improves game performance (GPU = Better graphics. HDD = Faster game loading time) 
<br>
<br>
<br>
<br>
<br>

# Mechanics and how the main flow goes
### Player
- **Spawn** - PSU district.
- **Inventory** - 4 slots: Starts with flashlight only; tool, weapon, and component slots empty
- **Money** - 0฿ Bits
- **Health** - 100 HP

### Controls
- **Walk** - Arrow keys
- **Run** - Hold shift (limited stamina)
- **Toggle flashlight** - Press V
- **Interact** - Press Z (activate switches, repair components)
- **Shoot / destroy** - Press space
- **Swap between weapons, tools, and Components** Press C
- **Swap weapon or tool** Press X

### Weapons
- **Skypiercer** - Pistol
  - Accuracy 2/5
  - 10 HP
  - 5 bullets
  - full Reload 3 seconds (500ms per bullet)
- **Thundercoil** - Laser Beam
  - Accuracy 4/5
  - 50 HP
  - 1 beam
  - Reload 6 seconds
- **Shockblade** - Lightning Sword
  - Accuracy 5/5
  - 10 HP
  - 1 swipe
  - Rewind 2 seconds
- **Ball of Lightning** - Grenade
  - Accuracy 1/5
  - 70 HP
  - 1 Grenade
  - Reload 10 Seconds

### Tools
- **Multimeter** - Measure voltage, current, and resistance. Critical for checking traces, capacitors, and ensuring correct voltage levels
- **Wire Strippers** - Remove insulation from wires for repairs and connections
- **Soldering Iron** - Solder components to the motherboard (RAM chips, capacitors, resistors, etc.)
- **Solder & Flux** - Materials needed for soldering work
- **Wire Cutters** - Cut wires to proper length during repairs
- **Chip Puller/Insertion Tool** - Safely remove and install IC chips (BIOS chip, CPU, memory chips) without damaging pins
- **Diagnostic Tool** - Plug into diagnostic ports (like CPU diag port) to read error codes and system information
- **Tweezers** - Handle small components (capacitors, resistors, small chips) during installation
- **Desoldering Gun** - Remove damaged components from the motherboard
- **Oscilloscope** - Analyze signal integrity on traces and data streams (for advanced troubleshooting)
- **Trace Repair Pen/Silver Paint** - Repair broken motherboard traces
- **Contact Cleaner** - Clean oxidized contacts and connectors
- **Flashlight** - Navigate dark areas, drains battery. The motherboard is completely dark and has no power

### Recharging Tools
- These use the broken traces of the Motherboard to recharge and use them.
- **Multimeter** - 5v (4 uses)
- **Soldering Iron** - 12v (2 uses)
- **Diagnostic Tool** - 5v (5 uses)
- **Desoldering Gun** - 12v (2 uses)
- **Oscilloscope** - 5v (2 uses)
- **Flashlight** - 5v (3 minutes)

### Dying and Retrying
- **Avoid hazards** - fire, explosions, sparks, toxic gas
- **Respawn at PSU if killed** - flashlight battery level is not changed, inventory gets left behind but is recoverable at death location
- You don't fail at module quests unless you die (see previous line ^). If you don't repair everything or do it wrong in the module quest, you just try again (collect more parts).

### Enemies
- **Kernel Titan** - Ball of red lightning with 3-5 (random) soldiers. 
  - 100 HP (25 HP each soldier)
  - Deals 25 HP per 1 second (5HP each soldier per 500ms)
  - Spawns from broken capacitors
  - Shoots multiple shots of lightning at the player and components on the motherboard
  - Gives ฿100 Bits when killed
- **SynErr** - Distorted polygons.
  - 75 HP
  - Deals 30 HP per 2 seconds
  - Spawns from broken resistors
  - Pierces player with its sharp polygons
  - Gives ฿50 Bits when killed
- **Corflux** - Mist of corrosion dust
  - 50 HP
  - 5 HP per 500ms
  - Spawns from corroded traces and components
  - poisons player and other Components if too close
  - Gives ฿25 Bits when killed
- Progression:
  - Easy at first
  - Every Module that is completed boosts the difficulty by 1
- Spawn:
  - Respawns every 2 minutes
  - Spawns two random enemies per module if the requirement is available

### Economy
- **Represention** ฿ Bits
- **Collecting** - Kill Enemies, Repair Components, Repair Modules
- **Buying** - Tools, Weapons, Components

### Unlocked Later
- Additional inventory slots (after RAM module quest)
- Autosave functionality (after HDD/SSD module quest)
  -(I may change this stuff, it's not fully fleshed out yet)

### Game lighting
- lighting is controlled by the player's flashlight. 
- Repairing motherboard districts enables that section of city lights to turn on. That is if they are connected to the PSU and the PSU in on.
<br>
<br>
<br>
<br>
<br>

# Core Loop
1. **Explore District**: Navigate to the module district you need to repair (PSU module quest, CPU module quest, RAM module quest, etc.)
2. **Collect Tools**: Buy required repair tools (multimeter, wire strippers, etc.) if not already purchased
3. **Pick Up Components**: Collect parts and components needed for the repair. 
4. **Repair Module**: Turn off PSU, fix the broken parts of the module (wires, capacitors, pins, traces, etc.)
5. **Upgrade Supporting Systems**: Upgrade PSU module, Fans module, Motherboard, or other supporting modules that are needed to accommodate the newly repaired module
7. **Configure / Test System**: Turn PSU back on and return to BIOS/CMOS
  - Press the BIOS button next to the terminal to configure the new part.
  - Warnings will show all modules that (still) need repairing (This is your progress bar)
8. **Defend Repairs**: Eliminate enemies that spawn near broken components before they damage your work
9. **Repeat**: Choose next module to repair and repeat the cycle.
<br>
<br>
<br>
<br>
<br>
# Quests:
### Quest Mechanics
- If the CPU module is fixed the PSU module will need to be upgraded to accommodate for the extra power.
- When servicing a module, the PSU must be turned off.
- Most module repair quests follow the same cycle listed in Core Loop.
- Completing a module quest dynamically enhances the game's performance (e.g. speed, stability, graphics) to mirror the functional improvement of the component in a real system.

### Quest Order
1. PSU Module
2. BIOS/CMOS Module
3. Player-directed module upgrades (CPU Module, RAM Module, Storage Module, etc.)
4. PCI Module — unlocks GPU Module, Network Module, and Sound Card Module quests
5. Fully repaired Motherboard — unlocks the I/O Module quest
<br>
<br>
<br>
## First Module Quests
### PSU Module
- Dysfunction:
  - Motherboard is out of power
  - High-power electrical shocks
- Quest:
  - Navigate through areas with high-voltage sparks (electrical shock hazards).
  - Restore the initial flow of power by repairing damaged wires, the transformer, etc.
  - Player must connect wires to the correct inputs and outputs
  - Locate and activate the master lever that powers the motherboard.
- Result:
  - The system powers on
  - City light turn on around the PSU
  - PSU must be kept at nominal temperature.
  - Sparks and other hazards spawn until PSU is turned off.
  - The BIOS/CMOS module quest is unlocked.

### BIOS/CMOS Module
- Dysfunction:
  - No GUI
  - Needed for other devices and OS to work together
  - Constant beeps heard in the city after PSU is turned on
- Quest:
  - Find and place the BIOS chip into the slot. Installing the chip wrong will destroy the chip.
  - Code the beginnings of the BIOS code.
  - PSU must be turned on to check system functionality
- Result:
  - The system still won't boot up but you're getting there
  - Minimal GUI is given
  - Warnings about other system faults appear (this is your progress bar).
  - As more parts of the computer are fixed, you will have to go here to set them up and make them work.
  - Faster game loading time
  - Ability to go to the game menu.
  - Player is now able to repair the rest of the map.
<br>
<br>
<br>
## Orderless Module Quests (Can be done in your own order)
### CPU Module
- Dysfunction:
  - System may randomly shut off or not turn on at all
  - Glitches and error screens
  - Game lockouts
  - Overheating
  - Electrical shocks
- Environment:
  - A high-tech logic chamber filled with floating data streams, and complex circuitry. The area is dynamic, with erratic glitch effects.
- Quest:
  - Turn off the PSU
  - Solve a series of logic grid puzzles (e.g., pattern recognition, sequence solving)
  - Retrieve diagnostic tools from various terminals to gather system error codes.
  - Plug the diag tool into the cpu diag port and understand the error messages (legend for codes on the motherboard near the CPU)
  - Find the pins on the CPU that are damaged and fix traces. Fixing them incorrectly causes an electrical shock and more pins and traces being damaged.
  - PSU must be turned on to check system functionality.
  - PSU and BIOS upgrade needed.
- Result:
  - Glitches and error screens are minimized.
  - Overheating is reduced.

### RAM Module
- Dysfunction:
  - Frequent freezes.
  - Beeping due to no known memory installed
- Environment:
  - A chaotic, fragmented memory space filled with floating data packets.
- Quest:
  - Turn off the PSU
  - Navigate the streets to find memory chips
  - Solder the memory chips onto the RAM modules
  - Fix the memory banks so the memory modules can be installed into the motherboard.
  - Insert the RAM into the slots. PSU must be turned off (hard pressing because RAM is hard to push into a slot)
  - PSU must be turned on to check system functionality.
  - PSU and BIOS upgrade needed.
- Result:
  - Game speed increases and freezes are minimized.
  - Beeping stops

### HDD/SSD Module
- Dysfunction:
  - Loud HDD background noise
  - Less of a menu and cool features.
  - Slow game performance
  - HDD Overheating
- Environment:
  - Disorganized library of data. Corridors are lined with file icons and flickering data streams.
- Quest:
  - Turn off the PSU
  - Collect data fragments and put them in the right order in binary to spell out a secret message
  - PSU must be turned on to check system functionality.
  - A system prompt indicates the need for further PSU and BIOS updates.
- Result:
  - Game load times are drastically reduced.
  - Autosave functionality is enabled.
  - The inventory capacity is increased.
  - HDD background noise is greatly reduced
  - Game performance is increased
  - Option to upgrade to a SSD

### PCI Module
- Dysfunction:
  - Expansion cards cannot communicate with the motherboard
  - Data corruption on peripheral connections
  - Intermittent disconnections and protocol errors
  - GPU, Sound Card, and Network cards remain undetected
- Quest:
  - Turn off the PSU
  - Navigate the PCI bus lanes to find broken expansion slots
  - Repair damaged slot connectors by matching pin layouts
  - Reconnect bus lanes by routing data paths correctly
  - Recode PCI protocol codes
  - PSU and BIOS upgrade needed
- Result:
  - Expansion slots become operational
  - Data corruption on peripheral connections is cleared
  - Protocol errors are resolved
  - GPU Module, Network Module, and Sound Card Module quests are unlocked
<br>
<br>
<br>
## PCI Module Quests (unlocked after PCI Module quest is finished)
### GPU Module
- Dysfunction:
  - Visuals are low, leading to static, glitched graphics, and low frame rates.
  - The whole game is in monochrome (Color to be chosen)
- Environment:
  - A visually chaotic landscape within the digital city. Glitches, static overlays, and corrupted textures.
- Quest:
  - Turn off the PSU
  - Adjust knobs to restore clarity. (This is where you can adjust the picture quality of the game.)
  - Major PSU and BIOS upgrade.
- Result:
  - Game is now in color
  - Visuals are normal.
  - Static and digital artifacts are eliminated.
  - Frame rates are enhanced (e.g. from 30 FPS to 60 FPS).

### Sound Card Module
- Dysfunction:
  - Low-quality audio output from PC speakers playing an 8‑bit version of the theme song (or no sound at all)
  - Volume diminishes when moving away.
- Environment:
  - Flickering equalizer displays and erratic waveforms.
- Quest:
  - Turn off the PSU
  - Replace the sound chip on the card like the BIOS quest
  - Connect audio cable to the motherboard and recalibrate volume controls with dip switches.
  - Update PSU and BIOS.
- Result:
  - High‑fidelity audio replaces the degraded 8-bit output
  - Enhanced sound feedback integrates into later quests.
  - Improved game experience.
<br>
<br>
<br>
## Persistent Quests
### PSU Module (Upgraded after every repaired or upgraded part)
- Details for initial repair and upgrades found in First Quests section above
- Must be upgraded after each new module is repaired to accommodate increased power requirements

### BIOS/CMOS Module (Updated after repaired or upgraded part)
- Details for initial repair and configuration found in First Quests section above
- Must be updated after each new module is repaired to configure it in the system

### Fans (Enabled after PSU is fixed)
- Dysfunction:
  - As you upgrade the system and more components are added, the system starts to overheat which can lead to further component damage.
- Environment:
  - An industrial, mechanical zone with a vast ventilation network (Pipes, ducts, and cooling towers),
- Quest:
  - Get to the fans.
  - Gather / make replacement fan blades and heat sinks.
  - Stabilize the temperature by placing the cooling parts in a way that allows the most air flow.
- Result:
  - Overheating is reduced (will need to be upgraded when other components are fixed/upgraded).
  - The overall system stability is improved.
  - An upgrade path to advanced cooling (e.g. water cooling) is unlocked.
  - Overall system performance is improved

### Motherboard (Enabled during every new area)
- Dysfunction:
  - Damaged / destroyed capacitors, resistors, traces and other components located on the motherboard are broken.
  - Most city light don't work
- Environment:
  - The Motherboard is the map
  - Picture the motherboard as a labyrinth of interconnected “districts”, each representing a different subsystem (audio, graphics, memory, etc.)
- Quest:
  - Gather broken components lying around the city.
  - Craft the component needed to fill in the empty spots on the city floor (transistors, resistors, capacitors).
  - Fix broken traces
- Result:
  - Connects all of the system together
  - Fully restored routing unlocks the I/O Module quest (details TBD)
<br>
<br>
<br>
<br>
<br>
# Inventory System
- Players collect artifacts and items throughout their journey:
- Inventory expansion is planned to tie into RAM and HDD upgrades; detailed slot management is still TBD.
<br>
<br>
<br>
<br>
<br>
# Wishlist
- I/O Module Quest
- Network Module Quest
- Adding a final boss (Entrocore). Appears after I/O Module quest through the parallel port
- Expanded UI Elements: Additional components such as a quest log, health bar, and fix and explain inventory, items (capacitors, resistors), tools (strippers, cutters), weapons (guns idk) etc.
- Economy for tools, weapons, kills, Quests (฿ Bits)
- Correct damage, HP, timing