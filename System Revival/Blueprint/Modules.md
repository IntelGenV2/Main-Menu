<span style="color:#57d4ff; font-size:2.1em; font-weight:700;">Modules</span>

This guide explains all the different parts of your computer that you'll repair in System Revival. Each module is like a different area of the motherboard (map) that needs fixing.

---

## Module names and order

**First**
- Power Supply Unit
  - PSU
- Basic Input / Output System
  - BIOS

**Any Order**
- Central Processing Unit
  - CPU
- Random Access Memory
  - RAM
- Hard Drive
  - HDD
- Peripheral Component Interconnect
  - PCI
- Serial Port
  - Serial
- Parallel Port
  - Parallel
- Universal Serial Bus
  - USB
- Co-Processor
  - Co-Processor
- Cache
  - Cache
- Real Time Clock
  - RTC

**Needs PCI**
- Graphics Processing Unit
  - GPU
- Sound Card
  - AUX
- Network Card
  - NET

**Constant**
- Motherboard
  - MotherBoard
- Basic Input / Output System
  - BIOS

**Semi-Constant**
- Power Supply Unit
  - PSU
- Fans
  - FAN

---

## Global Rules for All Modules

- **Turn off the power supply (PSU) before working** on most modules. This prevents dangerous electrical shocks.
- After you finish repairs:
  - Fix Motherboard area
  - Turn the PSU back on.
  - Visit the BIOS menu to configure the newly repaired hardware.
  - Upgrade Fans (optional)
  
- When you complete a module, the game gets better:
  - Faster performance
  - Better graphics
  - Better sound quality
  - More stable gameplay
  - etc. (depending on module)

---

## Tiers and Upgrades

- BIOS Module
  1. **CMOS** - Basic configuration storage, minimal functionality, forgets configuration after game closed
  2. **BIOS** - Traditional BIOS interface, more features, remembers configuration but limited devices
  3. **UEFI** - Modern UEFI interface, best features and stability, remembers configuration and can link to every module

- CPU Module
  1. **8 Bit** - Very limited processing power, basic operations only, frequent slowdowns
  2. **16 Bit** - Better performance, can handle more complex tasks, fewer slowdowns
  3. **32 Bit** - Good performance, standard modern computing, smooth gameplay
  4. **64 Bit** - Best performance, handles large amounts of data efficiently, maximum speed

- RAM Module
  1. **Basic RAM** - Frequent freezes, PSU must be turned off often (stack overload risk)
  2. **Standard RAM** - Fewer freezes, PSU can stay on longer
  3. **Extended RAM** - Rare freezes, PSU can run for extended periods
  4. **Maximum RAM** - No freezes, PSU can run continuously without stack overload

- HDD Module
  1. **HDD** - Slow loading times, loud drive noise, basic inventory slots
  2. **SSD** - Much faster loading times, quiet operation, 2 quick-access inventory slots
  3. **NVMe** - Fastest loading times, silent operation, 4 quick-access inventory slots

- PCI Module
  1. **ISA** - Slow and limited. GPU, Sound, and Network modules have severe limitations
  2. **PCI** - Better speed. GPU, Sound, and Network modules work but with reduced performance
  3. **PCIe** - Fastest and most reliable. GPU, Sound, and Network modules operate at maximum performance

- Serial Module
  1. **Wired Terminal** - Must physically go to Serial Port room to view system info (voltages, temperatures, module health, error logs)
  2. **Wireless Access** - Can open System Info from anywhere via visor overlay, still shows all system information

- Parallel Module
  1. **Dot-matrix** - Old impact printer, noisy, low quality prints
  2. **Inkjet** - Better quality, color support, quieter
  3. **Laser** - Best quality, fastest printing, most reliable

- USB Module
  1. **USB 1.0** - Input devices have delays and slight glitches
  2. **USB 2.0** - Input devices have lower delays and no glitches
  3. **USB 3.0** - Input devices work perfectly
  4. **USB-C** - Unlocks hidden Entrocore boss dungeon

- Co-Processor Module
  1. **FPU (Floating Point Unit)** - reduces CPU load slightly
  2. **DSP (Digital Signal Processor)** - Audio/video processing acceleration, significantly reduces CPU load, improves sound and graphics performance slightly
  3. **Neural Processor** - Advanced computation acceleration, maximum CPU load reduction

- Cache Module
  1. **L1 Cache** - Fastest, smallest cache. Slightly faster data access, reduces CPU wait times
  2. **L2 Cache** - Larger cache, further from CPU. Noticeably faster data access, reduces system slowdowns
  3. **L3 Cache** - Largest shared cache. Maximum data access speed, eliminates data bottlenecks, smooth system performance

- RTC Module
  1. **Basic RTC** - Error logs show timestamps, system uptime display in System Info
  2. **Enhanced RTC** - Repair history tracking, auto-shutdown warnings after inactivity
  3. **Advanced RTC** - Scheduled maintenance reminders, periodic system checks

- GPU Module
  1. **VGA** - Old analog connection, noisy and blurry, low fps, blanking
  2. **DVI** - Sharper, less blanking, limited fps
  3. **HDMI** - 1080p 60fps no blanking
  4. **DisplayPort** - 4k 60fps with GPU stability

- Sound Card Module
  1. **PC Speaker** - Basic system speaker, only produces simple beeps, very limited audio feedback
  2. **Mono** - Single channel audio, 8-bit quality, no spatial awareness, volume drops with distance
  3. **Stereo** - Two channel audio, clearer sound, basic left/right positioning, reduced volume drop

- NET Module
  1. **Modem** - Old dial-up connection, slow and unstable
  2. **Ethernet** - Wired connection, reliable
  3. **Wi-Fi** - Wireless, allows playing at high difficulty

- Fans Module
  1. **Air Cooled** - Basic fans and heatsinks. Reduces overheating slightly, system can still overheat under heavy load
  2. **Temperature Sensor** - Integrated temperature monitoring. Temperature info visible in System Info, warnings when components get too hot
  3. **Water Cooled** - Advanced liquid cooling. Maximum cooling efficiency, prevents overheating even under maximum load, enables overclocking

---

## Module Details

### 1. Power Supply (PSU) Module

**What's Broken:**
- The computer has no power at all
- Dangerous electrical sparks everywhere

**What You'll See:**
- A huge transformer and capacitors
- Thick electrical wires
- Sparking electrical gaps

**What You Need to Do:**
- Walk through dangerous sparking hallways
- Fix broken wires and connectors
- Connect wires to the correct power inputs
- Repair capacitors and other components
- Flip the main power switch

**What Happens When Fixed:**
- The computer turns on!
- Lights come on around the power supply area
- You can now work on other modules
- The BIOS module becomes available
- You'll need to upgrade the power supply again later as you add more components / modules

---

### 2. BIOS Module

**What's Broken:**
- No system menu appears
- Constant beeping sounds after power is on
- The computer can't coordinate different parts

**What You'll See:**
- Blank terminal and a medium sized chip slot
- Beeping sounds echoing everywhere

**What You Need to Do:**
- Purchase a BIOS chip
- Install it correctly (putting it in wrong will destroy it!)
- Turn on power to test
- Set up the basic menu system
- Progress through tiers by upgrading the chip and firmware (see Tiers and Upgrades)

**What Happens When Fixed:**
- Basic system menu becomes available
- You get warnings about other broken parts
- Game menu and options unlock
- You'll need to visit BIOS again after each major repair to configure it
- Higher tiers provide better configuration options and stability

---

### 3. CPU Module

**What's Broken:**
- Computer randomly shuts down
- Glitches and error screens
- System freezes
- Overheating and electrical shocks

**What You'll See:**
- High-tech logic room with a huge CPU smoking
- Glitchy visual effects

**What You Need to Do:**
- Turn off power first!
- Solve logic puzzles (patterns and sequences)
- Get the Diagnostic Tool from terminals
- Plug it into the CPU diagnostic port
- Use the code guide near the CPU to understand errors
- Find and fix broken CPU pins and wires
- Be careful - wrong fixes cause shocks and more damage!
- Progress through different CPU bit architectures (see Tiers and Upgrades)
- Turn power back on and test

**What Happens When Fixed:**
- Fewer errors and crashes
- Less overheating
- Computer responds faster

---

### 4. RAM Module (Memory)

**What's Broken:**
- Frequent freezes
- Beeping because there's no usable memory

**What You'll See:**
- Fragmented memory space with floating data blocks

**What You Need to Do:**
- Turn off power
- Purchase RAM chips / sticks
- Solder chips onto memory modules
- Fix memory banks and slots
- Insert RAM into slots
- Progress through different RAM capacity tiers (see Tiers and Upgrades)
- Turn power on and test

**What Happens When Fixed:**
- Game runs faster
- Freezes stop
- Beeping stops

---

### 5. Storage Module (HDD/SSD)

**What's Broken:**
- Loud drive noise
- Very slow performance
- Drive overheating
- Limited menus and features

**What You'll See:**
- A data library with shelves of file icons
- Streaming data "rivers"

**What You Need to Do:**
- Turn off power
- Collect data fragments
- Arrange them in correct binary order to form a secret message
- Fix the SATA controller (the part that connects storage):
  - Fix connectors
  - Clear communication errors
- Progress through different storage types (see Tiers and Upgrades)
- Turn power back on and test

**What Happens When Fixed:**
- Much faster loading times
- More inventory space
- Drive noise stops

---

### 6. PCI Module

**What's Broken:**
- Data corruption and disconnections
- Graphics, sound, and network cards aren't detected

**What You'll See:**
- Expansion bus lanes and slots
- Broken connectors and damaged traces
- Data corruption visual effects

**What You Need to Do:**
- Turn off power
- Navigate bus lanes to broken slots
- Fix slot connectors by matching pin layouts
- Reconnect bus lanes through routing puzzles
- Fix communication protocol errors
- Progress through different expansion bus types (see Tiers and Upgrades)
- Turn power on

**What Happens When Fixed:**
- Expansion slots work
- Corruption errors fixed
- Unlocks Graphics, Sound Card, and Network/Modem modules
- Higher tiers support faster expansion cards and better performance

---

### 7. Graphics Card (GPU) Module

**What's Broken:**
- Black and white visuals only
- Heavy static and glitches
- Low frame rate (choppy gameplay)

**What You'll See:**
- Visually chaotic area with TV static and broken geometry

**What You Need to Do:**
- Turn off power
- Progress through different video port types (see Tiers and Upgrades):
  - Fix the connectors
  - Solve signal quality puzzles
  - Calibrate the picture using knobs/sliders

**What Happens When Fixed:**
- Game goes from black & white → limited colors → full color
- Static and glitches removed
- Frame rate improves (30 → 60+ frames per second)

---

### 8. Sound Card Module

**What's Broken:**
- Low-quality or no sound
- Music sounds like old 8-bit games
- Volume drops with distance

**What You'll See:**
- Flickering sound visualizers
- Erratic sound waves
- Broken speakers

**What You Need to Do:**
- Turn off power
- Replace the sound chip (similar to BIOS chip quest)
- Reconnect audio cable to motherboard
- Progress through different audio quality tiers (see Tiers and Upgrades):
  - **PC Speaker:** Basic system speaker - only produces beeps
  - **Mono:** Install basic mono sound chip for single-channel audio
  - **Stereo:** Upgrade to stereo sound card, connect second channel for left/right audio
- Adjust volume and channels using switches
- Turn power on and test sound

**What Happens When Fixed:**
- Audio quality improves with each tier upgrade
- Higher tiers provide better spatial awareness (useful for detecting enemies/events)
- Volume drop issues resolved at higher tiers
- Audio quality also improves with PCI tier upgrades

---

### 9. Fans / Cooling Module

**What's Broken:**
- System overheats as more parts come online
- Risk of damaging other components
- No temperature monitoring - you can't see how hot things are getting

**What You'll See:**
- Industrial ventilation system: ducts, vents, cooling towers
- Broken or missing temperature sensors scattered around

**What You Need to Do:**
- Reach the fans and heatsinks
- Replace fan blades and heatsinks
- Progress through different cooling system types (see Tiers and Upgrades):
  - **Air Cooled:** Basic fans and heatsinks
  - **Temperature Sensor:** Install sensors at key locations (CPU area, GPU area, PSU area, etc.), connect to monitoring system, calibrate sensors
  - **Water Cooled:** Advanced liquid cooling system
- Arrange cooling parts for best airflow

**What Happens When Fixed:**
- Overheating greatly reduced
- System stability increased
- **Temperature monitoring active (Temperature Sensor tier):**
  - Temperature info visible in System Info screen (Serial Module)
  - Real-time temperature readings for all major components
  - Warnings when components get too hot
- Higher tiers provide better cooling and enable overclocking

---

### 10. Motherboard Module

**What's Broken:**
- Broken capacitors, resistors, and other small parts
- Broken electrical traces (wires on the board)
- Dark areas around the board

**What You'll See:**
- The entire board as a sprawling city
- Different "districts" representing different parts

**What You Need to Do:**
- Collect broken components scattered around
- Craft replacements (capacitors, resistors, transistors)
- Fix broken traces with Trace Repair Pen
- Gradually restore power paths around the board

**What Happens When Fixed:**
- System connectivity restored
- City lights come on in fixed areas (if power is on)
- Required before final USB repairs

---

### 11. Serial Module – System Info Screen

**What's Broken:**
- No system information available
- Can't monitor system health or temperatures
- No error logs visible

**What You'll See:**
- Serial port room with terminal equipment
- Broken or disconnected serial console

**What You Need to Do:**
- Progress through different Serial access types (see Tiers and Upgrades):
  - **Wired Terminal:** Go to Serial Port room, use serial console
  - **Wireless Access:** Open System Info from anywhere (visor overlay)
- See system info:
  - Power voltages
  - Temperatures (from cooling sensors)
  - Module health status
  - Error logs

**What Happens When Fixed:**
- You always have a tech-style health monitor
- Critical for planning repairs and monitoring system health
- Higher tiers allow access from anywhere

---

### 12. Parallel Module

**What's Broken:**
- Printer doesn't work
- No schematic maps available
- Can't see broken areas clearly

**What You'll See:**
- Massive Printer Module connected to Parallel port
- Broken or jammed printer mechanisms

**Failure Modes:**
- **Paper Jam**: You physically unjam the printer (careful - can hurt you!)
- **Toner/Ink Leak**: Black or colored powder/ink clouds reduce visibility and slowly damage you

**What You Need to Do:**
- Restore power to the printer
- Fix feed rollers, cartridges, and alignment
- Fix jam and leak problems
- Progress through different printer types (see Tiers and Upgrades)

**What Happens When Fixed:**
- You can print schematic maps
- Maps show broken components and completed modules
- Use maps as reference while exploring
- Higher tiers produce clearer, more detailed maps

---

### 13. Network / Modem Module

**What's Broken:**
- No network connection
- Can't access DataNet (multiplayer mode)
- Network hardware not working

**What You'll See:**
- Network card or modem hardware
- Broken network components and cables

**What You Need to Do:**
- Progress through different network connection types (see Tiers and Upgrades):
  - **Modem:** Fix analog line circuitry, fix noise filters
  - **Ethernet:** Install network card, fix connection negotiation
  - **Wi-Fi:** Install Wi-Fi card and antennas

**What Happens When Fixed:**
- Unlocks DataNet access at modem tier
- Each tier improves DataNet experience (see DataNET.md)

---

### 14. Co-Processor Module

**What's Broken:**
- CPU is overloaded with calculations
- System slows down during complex operations
- Audio and video processing causes lag

**What You'll See:**
- Co-processor socket or expansion slot
- Overheating CPU area
- Performance bottlenecks

**What You Need to Do:**
- Turn off power
- Install co-processor chip
- Progress through different co-processor types (see Tiers and Upgrades):
  - **FPU:** Install floating point unit for math calculations
  - **DSP:** Upgrade to digital signal processor for audio/video acceleration
  - **Neural Processor:** Install advanced neural processor for maximum performance
- Connect to CPU bus
- Turn power on and test

**What Happens When Fixed:**
- CPU load reduced
- Faster calculations and processing
- Better audio and video performance (higher tiers)
- System runs smoother under heavy load

---

### 15. Cache Module

**What's Broken:**
- Slow data access
- CPU frequently waits for data
- System slowdowns during data operations

**What You'll See:**
- Cache memory areas near CPU
- Broken cache controllers
- Data bottleneck visual effects

**What You Need to Do:**
- Turn off power
- Install cache memory chips
- Progress through different cache levels (see Tiers and Upgrades):
  - **L1 Cache:** Install fastest, smallest cache closest to CPU
  - **L2 Cache:** Add larger cache further from CPU
  - **L3 Cache:** Install largest shared cache for maximum performance
- Connect cache to CPU and memory bus
- Turn power on and test

**What Happens When Fixed:**
- Much faster data access
- Reduced CPU wait times
- Fewer system slowdowns
- Higher tiers eliminate data bottlenecks

---

### 16. RTC Module (Real-Time Clock)

**What's Broken:**
- No timestamps in error logs
- Can't track system uptime
- No repair history
- No time-based features

**What You'll See:**
- RTC chip and battery area
- Dead or missing CMOS battery
- Broken clock circuitry

**What You Need to Do:**
- Turn off power
- Replace CMOS battery
- Fix clock circuitry
- Progress through different RTC types (see Tiers and Upgrades):
  - **Basic RTC:** Restore basic timekeeping
  - **Enhanced RTC:** Add repair history tracking and auto-shutdown warnings
  - **Advanced RTC:** Enable scheduled maintenance and periodic system checks
- Calibrate time settings
- Turn power on and test

**What Happens When Fixed:**
- Error logs show timestamps
- System uptime display in System Info
- Repair history tracking (higher tiers)
- Time-based features and warnings (higher tiers)

---

### 17. USB Module

**What's Broken:**
- USB ports don't work
- Input devices (keyboards, mice (aka in-game controls)) are a little unreliable
- Text chat unavailable
- Contains the infection source: **Entrocore**, a dangerous virus

**What You'll See:**
- USB ports and controllers
- Damaged USB circuitry
- Signs of infection and corruption

**What You Need to Do:**
- Progress through different USB versions (see Tiers and Upgrades):
  - **USB 1.0:** Get any USB ports working
  - **USB 2.0-3.0:** Fix protection circuits to stop random failures
  - **USB-C:** Unlocks hidden Entrocore boss dungeon (see below)

**Core USB Dungeon (Hidden):**
- After reaching USB-C tier and system is stable, a hidden area appears:
  - Melted, damaged core
  - Fried wires
  - Blown protection diodes
  - This is where **Entrocore** lives

**The Entrocore Boss Fight:**
- Multi-phase boss battle
- Uses overvoltage attacks on your tools
- Data + power hybrid attacks
- Visual corruption and UI scrambling
- Overseer reveals the story

**What Happens When Fixed:**
- Input devices (keyboards, mice) work properly
- Text chat enabled in DataNet
- Entrocore defeated → Get "Entrocore Purged" badge
- USB & Ports fully repaired
- Local Machine becomes "Perfect System":
  - Maximum stability
  - Special cosmetics in DataNet
  - Unlocks New Game+ variants