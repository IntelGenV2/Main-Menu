# Arduino Tiny Basic (Dual Nano Build)

This project is a customized Tiny Basic "mini computer" that runs on **2 Arduino Nanos**:

- **CPU Nano**: Tiny Basic interpreter + PS/2 keyboard input
- **GPU Nano**: VGA text renderer

It is based on:

- Rob Cai's Arduino VGA Tiny Basic build: [https://www.instructables.com/Arduino-Basic-PC-With-VGA-Output/](https://www.instructables.com/Arduino-Basic-PC-With-VGA-Output/)
- Stefan Lenz / TinyBasic Plus lineage: [https://github.com/slviajero/tinybasic/tree/main](https://github.com/slviajero/tinybasic/tree/main)

This project was built by me, Laurence Bosch, and at this point it is my greatest project.

## Current Status

This is my tuned version for my own hardware setup.  
I kept what I needed, changed what I wanted, and removed features that did not fit this build.

## What I Changed From The Original `.ino` Files from Rob Cai

### CPU sketch (`PS2_Keyboard_Master_v0_30_commented.ino`)

- Split constants/tables into headers: `basic_keywords.h`, `basic_messages.h`, `gpu_protocol.h`, `boot_screen.h`, `hi.h`, `int_pins.h`.
- Added a boot flow and password gate (`Tron`) before normal prompt.
- Added a memory boot screen (SRAM/BASIC/EEPROM).
- Added command history browsing at prompt (up/down navigation for recent lines) and stores 3 lines with 20 chars each.
- Added/expanded commands and aliases including `DATA`, `READ`, `RESTORE`, `THEN`, `CLS`. 
- Added `HI` as a funny, one line response because I wanted to (and no it is not AI. Only "HI" works)
- Added `?`, `.`, and `!` variants to popular or constantly used commands. `?` for `Input`, `.` for `PRINT`, and `!` for `TONEW` to make music.
- Kept EEPROM workflow centered commands (`ELOAD`, `ESAVE`, `ELIST`, `EFORMAT`, `ECHAIN`) and tuned load pacing values.
- Added explicit error LED handling (`kErrorLedPin`) and feedback behaviors.
- Added/customized boot, clear, and status tones.
- Tuned RAM/stack handling and layout for this specific Nano configuration.
- Set serial console speed to `4800` for stable keyboard/display behavior in this setup. `9600` or higher causes the keyboard to go nuts.
- Removed the SD card path from the active command set (`LOAD/SAVE/FILES/CHAIN`) used in older variants because i dont have an SD card slot. i made another program to help send files to the system

### GPU sketch (`VGA_Graphics_Slave_v1_5.ino`)

- Added/fixed cursor show/hide behavior and safer text-bound handling.
- Improved line-wrap/scroll behavior so the right edge and next-line transitions are reliable.
- Added clearer color-state handling protocol (green/yellow/red cycle behavior).
- Kept serial rendering path aligned with CPU output expectations.

## Folder Tree

```text
Arduino_Tiny_Basic/
├── Arduino_Tiny_Basic_1/
│   ├── PS2_Keyboard_Master_v0_30_commented/
│   │   └── Main CPU sketch + interpreter support files
│   └── VGA_Graphics_Slave_v1_5/
│       └── Main GPU sketch + VGA support files
├── Manual/
│   └── Build/setup and TinyBasic usage
├── ORIGINAL/
│   └── Original reference sketches
├── Programs/
│   ├── TinyBasic example/user programs
│   └── Music/
│       └── TinyBasic music programs
└── Tools/
    └── Tiny Basic Sender/
        └── PC sender tool with a syntax checker + helper scripts/docs
```

## Notes

- This repo keeps the original reference sketches in `ORIGINAL/` for side-by-side comparison.
- The active build is the CPU/GPU pair under `Arduino_Tiny_Basic_1/`.

