# QTOS v0.0.5.0 - Complete System Guide
## Quantified Ternary Operating System

================================================================================

## Table of Contents
1.  Getting Started
2.  System Architecture  
3.  Ternary System Deep Dive
4.  Core Context
5.  File System Context
6.  Windows File Explorer Context
7.  Snake Game Context
8.  System Information Context
9.  BASIC Interpreter Context
10. Command Reference
11. Error Handling
12. Performance Features
13. Hidden Features

================================================================================

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Windows, macOS, or Linux

### Installation
1. Download the QTOS folder
2. Place it in your Documents directory
3. Open a terminal/command prompt
4. Navigate to the QTOS folder
5. Run: py CONTEXTS/core.py

### First Boot
When you first run QTOS, you'll see:
- A ternary-themed startup animation
- System initialization messages
- The CORE> prompt

  ░██████╗░░████████╗░░█████╗░░░██████╗
  ██╔═══██╗░╚══██╔══╝░██╔══██╗░██╔════╝
  ██║██╗██║░░░░██║░░░░██║░░██║░╚█████╗░
  ╚██████╔╝░░░░██║░░░░██║░░██║░░╚═══██╗
  ░╚═██╔═╝░░░░░██║░░░░╚█████╔╝░██████╔╝
  ░░░╚═╝░░░░░░░╚═╝░░░░░╚════╝░░╚═════╝░

Quantified Ternary Operating System

================================================================================

## System Architecture

QTOS is built around a context-switching architecture where each context provides specialized functionality:

### Core Components
- Core Context                  -> Main dispatcher and system coordinator
- File System Context           -> File and directory management
- Windows File Explorer Context -> Windows integration
- Snake Game Context            -> Built-in game
- System Information Context    -> System monitoring and diagnostics
- BASIC Interpreter Context     -> Programming environment

### File Structure

QTOS/
├── CONTEXTS/              # Main context modules
│   ├── core.py            # Core dispatcher
│   ├── fs.py              # File System context
│   ├── wfe.py             # Windows File Explorer context
│   ├── sg.py              # Snake Game context
│   ├── si.py              # System Information context
│   └── bi.py              # BASIC Interpreter context
├── DEPENDENCIES/          # Shared utilities
│   ├── helpers.py         # Common functions
│   ├── loc_handler.py     # Location management
│   ├── mod_handler.py     # File modification
│   ├── edit_handler.py    # Text editor
│   ├── crash_timer.py     # System crash simulation
│   ├── performance.py     # Performance monitoring
│   └── startup_effects.py # Boot animations
└── BASIC/                 # BASIC interpreter
    ├── interpreter.py
    ├── program.py
    ├── lexer.py
    ├── flowsignal.py
    ├── basictoken.py
    └── basicparser.py

================================================================================

## Ternary System Deep Dive

QTOS is built on a ternary (base-3) number system instead of the traditional binary (base-2) system.

### What is Ternary?
- Base-3 =    number system using digits: 0, 1, 2
- Trit =      Ternary digit (like bit in binary)
- Tryte =     6 trits (3⁶ = 729 possible values)
- Kilotryte = 1000 trytes

### Why Ternary?
1. More Efficient:        3 states can represent more information than 2
2. Balanced:              Natural representation of positive/negative/zero
3. Quantum-Ready:         Aligns with quantum computing principles
4. Mathematical Elegance: Powers of 3 provide optimal scaling

### System Limits (Base-3)
1. Maximum Trytes: 3¹⁶ = 43,046,721
2. RAM Capacity:   3¹⁰ = 59,049 trytes ≈ 35 KB
3. Disk Capacity:  3¹⁶ = 43,046,721 trytes ≈ 25 MB

### Conversion Ratios
- 1 tryte     ≈ 0.59436 bytes
- 1 kilotryte ≈ 594.36 bytes
- 1 megatryte ≈ 594.36 KB

### Display Format
- Small values: 123₃ Ty (trytes)
- Large values: 1,234₃ KTy (kilotrites)
- Overflow:     OVERFLOW₃ ERROR

================================================================================

## Core Context

Prompt: CORE>

The Core Context is the main dispatcher and system coordinator.

### Commands

| Command          | Description                             | Response                                                                      |
|------------------|-----------------------------------------|-------------------------------------------------------------------------------|
| des - fs         | Switch to File System context           | [ACCESS] → Entered File System Context                                        |
| des - wfe        | Switch to Windows File Explorer context | [ACCESS] → Entered Windows File Explorer Context                              |
| des - sg         | Switch to Snake Game context            | [ACCESS] → Entered Snake Game Context                                         |
| des - si         | Switch to System Information context    | [ACCESS] → Entered System Information Context                                 |
| des - bi         | Switch to BASIC Interpreter context     | [ACCESS] → Entered BASIC Interpreter Context                                  |

### What Happens When
- Invalid command: [ERR] Unknown Core command
- Context switch:  Loading animation + access recording
- System crash:    Automatic crash simulation (hidden feature)

================================================================================

## File System Context

Prompt: FS>

The File System Context provides comprehensive file and directory management.

### Commands

#### Location Commands
| Command             | Description                        | Response                                   |
|---------------------|------------------------------------|--------------------------------------------|
| /loc -d             | Display current directory contents | [LOC] → Displaying: "<urn>", • <files>     |
| /loc -e <directory> | Enter a directory                  | [LOC] → Entered: "<urn>"                   |
| /loc -p <urn>       | Peek at location without entering  | [LOC] → Peeking at: "<urn>", • <files>     |
| /loc -s <pattern>   | Search OS for pattern               | [SEARCH] → Searching OS for "<pattern>", • <matches> (files shown with *) |

#### File Operations
| Command                                     | Description           | Response                                    |
|---------------------------------------------|-----------------------|---------------------------------------------|
| /mod -c /name=<name> /loc=<urn> /type=block | Create file           | [MOD] → Created "<name>" in <urn>           |
| /mod -c /name=<name> /loc=<urn> /type=chunk | Create directory      | [MOD] → Created "<name>" in <urn>           |
| /mod -d /name=<name> /loc=<urn>             | Delete file/directory | [MOD] → Deleted "<name>" from <urn>         |
| /mod -r /name=<old> /loc=<urn> /name2=<new> | Rename                | [MOD] → Renamed "<old>" to "<new>" in <urn> |
| /mod -e /name=<name> /loc=<urn>             | Edit text file        | Opens interactive text editor               |
| /mod -y /name=<name> /loc=<urn> /loc2=<urn> | Copy                  | [MOD] → Copied "<name>" to <urn>            |
| /mod -m /name=<name> /loc=<urn> /loc2=<urn> | Move                  | [MOD] → Moved "<name>" to <urn>             |

#### File Execution
| Command         | Description                   | Response                           |
|-----------------|-------------------------------|------------------------------------|
| /run <filename> | Run file in current directory | [RUN] → Started <type>: <filename> |

#### Context Switching
| Command         | Description                       | Response                             |
|-----------------|-----------------------------------|--------------------------------------|
| des - <context> | Return to Core or switch contexts | [ACCESS] → Entered <context> Context |
| help            | Show available commands           | Displays command list                |

### URN (Uniform Resource Name) Format
| Format                | Description              |
|-----------------------|--------------------------|
| base                  | Root directory           |
| base:folder           | Subdirectory             |
| base:folder:subfolder | Nested subdirectory      |
| eloc                  | Current entered location |

### File Naming Convention

QTOS uses a unique file naming convention where dots (.) in file extensions are replaced with asterisks (*) for display purposes. This applies to all file listings throughout the OS.

| Display      | Storage      | Description          |
|--------------|--------------|----------------------|
| file*txt     | file.txt     | Asterisk for display |
| document*pdf | document.pdf | Asterisk for display |

### What Happens When
- File created:    Cache cleared, immediate visibility
- File deleted:    Cache cleared, removed from listing
- File edited:     Opens interactive text editor
- File run:        Executes based on file type
- Invalid command: [ERR] Unknown File System command
- File not found:  [ERR] File not found: <filename>

================================================================================

## Windows File Explorer Context

Prompt: WFE>

The Windows File Explorer Context provides Windows system integration.

### Commands

| Command          | Description                       | Response                             |
|------------------|-----------------------------------|--------------------------------------|
| /drive -<letter> | Switch to drive (e.g., /drive -c) | [DRIVE] → Switched to <letter>:\     |
| /run <filename>  | Run executable in current drive   | [RUN] → Started <filename>           |
| des - <context>  | Return to Core or switch contexts | [ACCESS] → Entered <context> Context |

### What Happens When
- Drive switch:   [DRIVE] → Switched to C:\
- File run:       [RUN] → Started <filename>
- File not found: [ERR] <filename> not found
- No drive:       [ERR] No drive selected

================================================================================

## Snake Game Context

Prompt: SG>

The Snake Game Context provides a built-in Snake game.

### Commands

| Command         | Description                       | Response                             |
|-----------------|-----------------------------------|--------------------------------------|
| /run -sg        | Start Snake game                  | Full-screen game interface           |
| des - <context> | Return to Core or switch contexts | [ACCESS] → Entered <context> Context |

### Game Features
- Controls:  Arrow keys or WASD
- Objective: Eat food, grow longer
- Collision: Game over if snake hits wall or itself
- Scoring:   Points based on food eaten

### What Happens When
- Game start:      Full-screen game interface
- Game over:       Score display, return to prompt
- Invalid command: [ERR] Unknown Snake Game command
- Context switch:  Use des - <context> to switch contexts

================================================================================

## System Information Context

Prompt: SI>

The System Information Context provides system monitoring and diagnostics.

### Commands

#### Information Commands
| Command  | Description                  | Response                                           |
|----------|------------------------------|----------------------------------------------------|
| /info -o | Operating system information | [OS] → Quantified Ternary OS v0.0.5.0              |
| /info -c | CPU information              | [CPU] → QT 4T - 4th Generation Ternary CPU @ 2 MHz |
| /info -r | Memory usage and capacity    | [RAM] → <used> <unit> / <capacity> <unit>          |
| /info -d | Storage usage and capacity   | [DISK] → <used> <unit> / <capacity> <unit>         |
| /info -u | System uptime                | [UPT] → <days>d <hours>h <minutes>m <seconds>s     |
| /info -t | Current time                 | [TIME] → <date> <time>                             |

#### Testing Commands
| Command  | Description               | Response                                                         |
|----------|---------------------------|------------------------------------------------------------------|
| /test -r | Memory performance test   | [RAM] → Testing memory modules..., [GRID] → Memory Module Status |
| /test -c | CPU performance test      | [CPU] → Testing CPU cores @ 2MHz..., [CORE] → Core X: XX%        |
| /test -a | Run all performance tests | [TEST] → Running full system diagnostics...                      |

#### System Settings Commands
| Command          | Description                             | Response                                                                                                     |
|------------------|-----------------------------------------|--------------------------------------------------------------------------------------------------------------|
| /set -c          | Clear performance data and memory usage | [INFO] → Performance data cleared...,  [INFO] → Current memory: X.X MB, Memory cleanup completed             |
| /set -s          | Show available startup effects          | [INFO] → Available effects: matrix, binary, scanline, glitch, hologram, quantum, retro                       |
| /set -s <effect> | Change startup animation                | [INFO] → Startup effect changed to: <effect>                                                                 |

#### Crash Timer Commands
| Command      | Description                    | Response                                                         |
|--------------|--------------------------------|------------------------------------------------------------------|
| /crash       | Show crash timer status        | [CRASH] → Crash timer is currently enabled/disabled              |
| /crash -f    | Disable crash timer            | [CRASH] → Crash timer disabled                                   |
| /crash -n    | Enable crash timer             | [CRASH] → Crash timer enabled                                    |

#### Context Switching
| Command         | Description                       | Response                             |
|-----------------|-----------------------------------|--------------------------------------|
| des - <context> | Return to Core or switch contexts | [ACCESS] → Entered <context> Context |

### Information Display
- Ternary format: Values shown in base-3
- Units:          Trytes (Ty), Kilotrites (KTy)
- Capacity:       RAM and disk limits
- Usage:          Current memory and storage usage

### What Happens When
- System info:     Display ternary-formatted data
- Memory warning:  Alert if approaching limits
- Test completion: Performance metrics display
- Invalid command: [ERR] Unknown System Information command

================================================================================

## BASIC Interpreter Context

Prompt: BI>

The BASIC Interpreter Context provides a complete BASIC programming environment.

### Commands

#### Context Commands
| Command         | Description                       | Response                             |
|-----------------|-----------------------------------|--------------------------------------|
| /run -bi        | Start BASIC interpreter           | Opens BASIC programming environment  |
| des - <context> | Return to Core or switch contexts | [ACCESS] → Entered <context> Context |
| help            | Show available commands           | Displays command list                |

#### Program Control (Inside BASIC)
| Command         | Description             | Response                      |
|-----------------|-------------------------|-------------------------------|
| RUN             | Execute current program | Executes program line by line |
| LIST            | Display program lines   | Shows all program lines       |
| NEW             | Clear current program   | Program cleared               |
| SAVE <filename> | Save program to file    | Program saved                 |
| LOAD <filename> | Load program from file  | Program loaded                |
| EXIT            | Return to QTOS          | Returning to QTOS...          |
| HELP            | Show BASIC commands     | Displays command help          |

#### Direct Mode (Inside BASIC)
| Command                  | Description     | Response          |
|--------------------------|-----------------|-------------------|
| PRINT <expression>       | Print value     | Displays result   |
| LET <variable> = <value> | Assign variable | Variable assigned |
| INPUT <variable>         | Get user input  | Prompts for input |

### BASIC Features
- Variables: A-Z, A0-Z9
- Numbers:   Integer and floating-point
- Strings:   Quoted text
- Control:   IF-THEN, FOR-NEXT, GOTO
- Functions: Mathematical and string functions
- Data:      DATA/READ/RESTORE statements

### What Happens When
- Interpreter start: Opens BASIC programming environment
- Program run:     Execute line by line
- Syntax error:    Display error message
- Runtime error:   Stop execution, show error
- Exit command:    Returns to QTOS cleanly
- Invalid command: BASIC syntax error

================================================================================

## Command Reference

### Universal Commands
All contexts support these commands:

| Command         | Description                 | Response                             |
|-----------------|-----------------------------|--------------------------------------|
| des - core      | Return to Core Context      | [ACCESS] → Entered Core Context      |
| des - <context> | Switch to specified context | [ACCESS] → Entered <context> Context |

### Command Syntax Rules
1. Case insensitive: Commands work in any case
2. Whitespace:       Extra spaces are ignored
3. Parameters:       Required parameters must be provided
4. Quotes:           Use quotes for filenames with spaces
5. Error handling:   Invalid commands show error messages

### Response Format
| Type    | Format                     | Color  |
|---------|----------------------------|--------|
| Success | [TYPE] → Message           | Green  |
| Error   | [ERR] Error message        | Red    |
| Warning | [WARN] Warning message     | Yellow |
| Info    | [INFO] Information message | Yellow |

### Color Coding
- Green:       Success messages
- Yellow:      Warnings and info
- Red:         Errors
- Light Green: Status updates

================================================================================

## Error Handling

### Common Error Messages
| Error                              | Description               |
|------------------------------------|---------------------------|
| [ERR] Unknown <context> command    | Invalid command           |
| [ERR] File not found: <filename>   | File doesn't exist        |
| [ERR] Out of RAM loading <context> | Memory limit exceeded     |
| [ERR] Modification error           | File operation failed     |
| [ERR] Locator error                | Location operation failed |

### Error Recovery
1. Invalid command: Try again with correct syntax
2. File not found:  Check filename and location
3. Memory error:    Switch to Core and run memory command
4. System error:    Restart QTOS

### Debug Information
- Cache stats:    Available in System Information context
- Memory usage:   Check with memory command
- Module loading: Tracked in System Information

================================================================================

## Performance Features

### Caching System
- Directory listings: Cached for 5 seconds
- File operations:    Cache automatically cleared
- Performance data:   Tracked and displayed

### Memory Management
- Module loading:   Only load when needed
- Memory cleanup:   Automatic and manual options
- Usage monitoring: Real-time tracking

### Optimization Features
- Lazy loading:              Contexts loaded on demand
- Cache invalidation:        Immediate updates after changes
- Efficient file operations: Optimized for performance

================================================================================

## Hidden Features

### Crash Timer
- Purpose:    Simulate system crashes
- Activation: Automatic after boot
- Behavior:   Random crash between 5-15 seconds
- Control:    Use /crash commands in SI context
- Recovery:   Restart QTOS

### Startup Effects
- Multiple animations: matrix, binary, scanline, glitch, hologram, quantum, retro
- Customizable:        Change with /set -s <effect>
- Performance:         Optimized for smooth display

### Performance Monitoring
- Memory tracking:  Real-time usage monitoring
- Cache statistics: Performance metrics
- Module loading:   Track which modules are resident

================================================================================

## Advanced Usage

### File System Tips
1. Use URNs:        Navigate efficiently with URN notation
2. Cache awareness: Changes are immediately visible
3. File types:      Different handling for different extensions
4. Search patterns: Use regex patterns for file search

### System Optimization
1. Memory management:      Regular cleanup with memory command
2. Cache clearing:         Automatic after file operations
3. Module unloading:       Contexts unload when switching
4. Performance monitoring: Use System Information context

### Programming with BASIC
1. Line numbers: Required for program mode
2. Variables:    Use A-Z for simple variables
3. Input/Output: PRINT and INPUT for user interaction
4. Control flow: IF-THEN, FOR-NEXT for program logic
5. Data handling: Use DATA/READ/RESTORE for data storage

================================================================================

## Troubleshooting

### Common Issues
1. Python not found:  Install Python 3.7+
2. Import errors:     Check file structure
3. Permission errors: Run as administrator if needed
4. Memory issues:     Use memory command for cleanup
5. Performance module error: If you see "[ ERR ] Performance module not available" when running /set commands, ensure you're running QTOS from the correct directory (QTOS folder) and that all DEPENDENCIES files are present

### Performance Issues
1. Slow startup:          Check startup effects
2. High memory usage:     Monitor with System Information
3. Cache problems:        Clear caches manually
4. File operation delays: Check disk space

### System Crashes
1. Expected crashes:   Part of crash timer feature
2. Unexpected crashes: Check error messages
3. Recovery:           Restart QTOS
4. Data loss:          Files are preserved between sessions

### Command-Specific Issues
1. /set commands fail: Ensure you're in SI context (SI>) and all DEPENDENCIES files exist
2. /set -c fails: Check that performance.py exists in DEPENDENCIES folder
3. /set -s fails: Verify startup_effects.py exists in DEPENDENCIES folder
4. /crash commands fail: Ensure crash_timer.py exists in DEPENDENCIES folder
5. Import errors:       Run QTOS from the main QTOS directory, not from subdirectories

================================================================================

## Conclusion

QTOS is a unique operating system that combines:
- Ternary number system for mathematical elegance
- Context-switching architecture for modularity
- Comprehensive file management for productivity
- Built-in programming environment for development
- Performance monitoring for optimization
- Hidden features for exploration
- Crash simulation for realistic OS experience

The system is designed to be educational, functional, and entertaining while demonstrating the power of ternary computing principles.

Version: v0.0.5.0
Status: Fully Functional
Architecture: Ternary-based Context Switching 