#!/usr/bin/env python3
"""
QTOS v0.0.5.0 - Quantified Ternary OS (core + dispatcher)
"""
import os
import sys
import time
from pathlib import Path

# ─── Prepare import paths ────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.absolute()
QTOS_ROOT = SCRIPT_DIR.parent.absolute()
DEPENDENCIES = QTOS_ROOT / "DEPENDENCIES"

# Ensure we can import contexts and helpers
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(DEPENDENCIES))

# ─── Import modules with error reporting ─────────────────────────────────────────
try:
    from helpers import LIGHT_GREEN, GREEN, RESET, loading, YELLOW, RED
    from fs import handle_fs
    from wfe import handle_wfe
    from sg import snake_game
    from si import (
        handle_info, handle_test, handle_set, handle_memory, handle_clear, handle_startup, handle_startup_effect, handle_crash,
        record_access, record_release,
        get_current_ram_usage_bytes,
        RAM_CAPACITY_BYTES, DISK_CAPACITY_BYTES, MODULE_FILES, _ACCESSED_MODULES, get_loaded_contexts
    )
    # Import crash timer (hidden feature)
    from crash_timer import start_crash_timer, is_system_crashed, enable_crashes, disable_crashes, get_crash_status
    CRASH_TIMER_AVAILABLE = True
except ImportError:
    # Crash timer not available, continue without it
    CRASH_TIMER_AVAILABLE = False
    def start_crash_timer():
        pass
    def is_system_crashed():
        return False
    def enable_crashes():
        return "Crash timer not available"
    def disable_crashes():
        return "Crash timer not available"
    def get_crash_status():
        return False
except Exception as e:
    print(f"{RED}[ IMPORT ERR ]{RESET} {e}")
    sys.exit(1)

# ─── Try to import BASIC interpreter ─────────────────────────────────────────────
try:
    from bi import basic_interpreter
    BASIC_AVAILABLE = True
except Exception:
    BASIC_AVAILABLE = False
    def basic_interpreter():
        print(f"{RED}[ ERR ]{RESET} BASIC Interpreter module not found.")

# ─── Global paths & state ────────────────────────────────────────────────────────
HOME_DIR = Path.home()
FS_ROOT = HOME_DIR / "Documents" / "QTOS"
START_TIME = time.time()

CONTEXT_NAMES = {
    'CORE': 'Core',
    'FS':   'File System',
    'WFE':  'Windows File Explorer',
    'SG':   'Snake Game',
    'SI':   'System Information',
    'BI':   'BASIC Interpreter'
}

current_context = 'CORE'
fs_urn_ref = ['base']
wfe_path_ref = [None]

# ─── Helper routines ────────────────────────────────────────────────────────────
def ensure_root():
    """Ensure FS_ROOT directory exists"""
    FS_ROOT.mkdir(parents=True, exist_ok=True)

def check_boot_limits():
    """Check if module sizes exceed limits with optimized file operations"""
    total_disk = 0
    for fname in MODULE_FILES.values():
        try:
            file_path = SCRIPT_DIR / fname
            if file_path.exists():
                total_disk += file_path.stat().st_size
        except OSError:
            pass
    
    if total_disk > DISK_CAPACITY_BYTES:
        print(f"{RED}[ WARN ] Disk modules total {total_disk} B exceeds {DISK_CAPACITY_BYTES} B{RESET}")

    core_path = SCRIPT_DIR / MODULE_FILES['CORE']
    try:
        core_size = core_path.stat().st_size if core_path.exists() else 0
    except OSError:
        core_size = 0
    
    if core_size > RAM_CAPACITY_BYTES:
        print(f"{RED}[ WARN ] core.py size {core_size} B exceeds RAM cap {RAM_CAPACITY_BYTES} B{RESET}")

def check_memory_usage():
    """Check current memory usage and warn if high"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        if memory_mb > 100:  # Warn if using more than 100MB
            print(f"{YELLOW}[ WARN ] High memory usage: {memory_mb:.1f} MB{RESET}")
        
        return memory_mb
    except ImportError:
        return 0

def startup_animation():
    """Linux-style startup with ternary OS theme"""
    import time
    
    # QTOS Logo/Banner
    banner = [
        "  ░██████╗░░████████╗░░█████╗░░░██████╗",
        "  ██╔═══██╗░╚══██╔══╝░██╔══██╗░██╔════╝",
        "  ██║██╗██║░░░░██║░░░░██║░░██║░╚█████╗░",
        "  ╚██████╔╝░░░░██║░░░░██║░░██║░░╚═══██╗",
        "  ░╚═██╔═╝░░░░░██║░░░░╚█████╔╝░██████╔╝",
        "  ░░░╚═╝░░░░░░░╚═╝░░░░░╚════╝░░╚═════╝░",
        "",
        "Quantified Ternary Operating System"
    ]
    
    for line in banner:
        print(f"{LIGHT_GREEN}{line}{RESET}")
    
    print(f"\n{LIGHT_GREEN}[BOOT] Starting Quantified Ternary OS v0.0.5.0{RESET}")
    time.sleep(0.3)
    
    # Linux-style startup messages with ternary theme and realistic timing
    startup_messages = [
        ("Initializing ternary memory subsystem", 0.3),      # Memory init takes time
        ("Loading base-3 arithmetic unit", 0.2),             # CPU unit loads quickly
        ("Calibrating trit processors", 0.8),                # Calibration takes longer
        ("Establishing ternary logic gates", 0.4),           # Logic setup takes time
        ("Synchronizing tryte conversion engine", 0.6),      # Complex conversion setup
        ("Validating storage capacity (0, 1, 2)", 0.3),      # Storage check
        ("Loading context switcher", 0.2),                   # Quick module load
        ("Initializing file system interface", 0.5),         # FS setup takes time
        ("Starting module dependency resolver", 0.4),        # Dependency resolution
        ("Establishing ternary network protocols", 0.7),     # Network setup is slow
        ("Loading BASIC interpreter module", 0.3),           # Interpreter load
        ("Initializing system information daemon", 0.2),     # Quick daemon start
        ("Starting snake game engine", 0.2),                 # Game engine loads fast
        ("Configuring Windows file explorer bridge", 0.6),   # Bridge setup takes time
        ("Ternary OS kernel ready", 0.1)                     # Final status
    ]
    
    # Calculate the width for right-aligned [OK] status
    max_message_length = max(len(msg) for msg, _ in startup_messages)
    status_width = 60  # Total width for the line
    
    for message, delay in startup_messages:
        # Right-align the [OK] status
        padding = status_width - len(message) - 4  # 4 for "[OK]"
        if padding < 0:
            padding = 1  # Minimum padding
        
        status_line = f"{YELLOW}{message}{RESET}{' ' * padding}{GREEN}[OK]{RESET}"
        print(status_line)
        time.sleep(delay)  # Realistic timing based on operation complexity
    
    print(f"\n{LIGHT_GREEN}[SYSTEM] QTOS successfully booted{RESET}")
    print(f"{LIGHT_GREEN}[SYSTEM] Ready for base-3 operations{RESET}\n")

def handle_context_switch(target_context):
    """Optimized context switching with validation"""
    if target_context not in CONTEXT_NAMES or target_context == 'CORE':
        print(f"{RED}[ ERR ] Unknown Context: {target_context}{RESET}")
        return False
    
    # Check RAM before load
    mod = MODULE_FILES.get(target_context)
    if mod:
        try:
            mod_path = SCRIPT_DIR / mod
            size = mod_path.stat().st_size if mod_path.exists() else 0
        except OSError:
            size = 0
        
        current_ram = get_current_ram_usage_bytes()
        loaded_contexts = len(_ACCESSED_MODULES)
        
        if current_ram + size > RAM_CAPACITY_BYTES:
            print(f"{RED}[ ERR ] Out of RAM loading {CONTEXT_NAMES[target_context]} Context{RESET}")
            print(f"{YELLOW}[ INFO ] Current: {loaded_contexts} contexts loaded, {current_ram} bytes used{RESET}")
            print(f"{YELLOW}[ INFO ] Need: {size} more bytes, limit: {RAM_CAPACITY_BYTES} bytes{RESET}")
            print(f"{YELLOW}[ INFO ] Use '/set -r' in SI context to clear RAM{RESET}")
            return False
    
    # Switch context (contexts now persist in RAM)
    loading(f"Entering {CONTEXT_NAMES[target_context]} Context", dots=5, delay=0.2)
    record_access(target_context)
    print(f"{LIGHT_GREEN}[ ACCESS ] → Entered {CONTEXT_NAMES[target_context]} Context{RESET}")
    return True

# ─── Main loop ───────────────────────────────────────────────────────────────────
def main():
    ensure_root()
    check_boot_limits()
    startup_animation()

    print(f"{LIGHT_GREEN}QTOS v0.0.5.0 Initialized{RESET}\n")
    # Core module stays resident
    record_access('CORE')
    
    # Start crash timer (hidden feature)
    if CRASH_TIMER_AVAILABLE:
        start_crash_timer()

    global current_context
    memory_check_counter = 0
    while True:
        try:
            # Check if system has crashed
            if CRASH_TIMER_AVAILABLE and is_system_crashed():
                # System has crashed, exit the loop
                break
            
            # Check memory usage every 100 iterations
            memory_check_counter += 1
            if memory_check_counter >= 100:
                check_memory_usage()
                memory_check_counter = 0
            
            if current_context == 'CORE':
                cmd = input(f"{GREEN}CORE> {RESET}").strip().lower()
                if cmd.startswith('des - '):
                    target = cmd.split('des - ', 1)[1].upper()
                    if handle_context_switch(target):
                        current_context = target
                elif cmd == 'help':
                    print(f"{YELLOW}Core Commands:{RESET}")
                    print(f"{LIGHT_GREEN}  des - fs     - Switch to File System{RESET}")
                    print(f"{LIGHT_GREEN}  des - wfe    - Switch to Windows File Explorer{RESET}")
                    print(f"{LIGHT_GREEN}  des - sg     - Switch to Snake Game{RESET}")
                    print(f"{LIGHT_GREEN}  des - si     - Switch to System Information{RESET}")
                    print(f"{LIGHT_GREEN}  des - bp     - Switch to BASIC Interpreter{RESET}")
                    print(f"{LIGHT_GREEN}  help         - Show this help{RESET}")
                else:
                    print(f"{RED}[ ERR ] Unknown Core Command{RESET}")

            elif current_context == 'FS':
                next_ctx = handle_fs(fs_urn_ref, str(FS_ROOT))
                if next_ctx in CONTEXT_NAMES:
                    current_context = next_ctx
                continue

            elif current_context == 'WFE':
                next_ctx = handle_wfe(wfe_path_ref)
                if next_ctx in CONTEXT_NAMES:
                    current_context = next_ctx
                continue

            elif current_context == 'SG':
                cmd = input(f"{GREEN}SG> {RESET}").strip().lower()
                if cmd == '/run -sg':
                    snake_game()
                elif cmd.startswith('des - '):
                    target = cmd.split('des - ', 1)[1].upper()
                    if target in CONTEXT_NAMES:
                        if handle_context_switch(target):
                            current_context = target
                    else:
                        print(f"{RED}[ ERR ] Unknown Context: {target}{RESET}")
                elif cmd == 'help':
                    print(f"{YELLOW}Snake Game Commands:{RESET}")
                    print(f"{LIGHT_GREEN}  /run -sg     - Start Snake game{RESET}")
                    print(f"{LIGHT_GREEN}  des - <ctx>  - Switch to context{RESET}")
                    print(f"{LIGHT_GREEN}  help         - Show this help{RESET}")
                else:
                    print(f"{RED}[ ERR ] Unknown Snake Game Command{RESET}")

            elif current_context == 'SI':
                cmd = input(f"{GREEN}SI> {RESET}").strip().lower()
                if cmd.startswith('/info '):
                    for line in handle_info(cmd, START_TIME, str(FS_ROOT)):
                        print(line)
                elif cmd.startswith('/test '):
                    for line in handle_test(cmd):
                        print(line)
                elif cmd.startswith('/crash'):
                    for line in handle_crash(cmd):
                        print(line)
                elif cmd.startswith('/set '):
                    for line in handle_set(cmd):
                        print(line)
                elif cmd == 'memory':
                    handle_memory()
                elif cmd == 'clear':
                    handle_clear()
                elif cmd == 'startup':
                    handle_startup()
                elif cmd == 'loaded':
                    loaded_contexts = get_loaded_contexts()
                    print(f"{YELLOW}[ LOADED ]{RESET} {LIGHT_GREEN}→ {len(loaded_contexts)} contexts: {', '.join(loaded_contexts)}{RESET}")
                elif cmd.startswith('startup '):
                    effect = cmd.split(' ', 1)[1].lower()
                    handle_startup_effect(effect)
                elif cmd.startswith('/crash'):
                    # Handle crash control commands
                    if CRASH_TIMER_AVAILABLE:
                        parts = cmd.split()
                        if len(parts) == 2:
                            flag = parts[1].lower()
                            if flag == '-f':
                                result = disable_crashes()
                                print(f"{YELLOW}[ CRASH ]{RESET} {LIGHT_GREEN}→ {result}{RESET}")
                            elif flag == '-n':
                                result = enable_crashes()
                                print(f"{YELLOW}[ CRASH ]{RESET} {LIGHT_GREEN}→ {result}{RESET}")
                            else:
                                print(f"{RED}[ ERR ] Unknown crash flag. Use -f to disable, -n to enable{RESET}")
                        else:
                            status = "enabled" if get_crash_status() else "disabled"
                            print(f"{YELLOW}[ CRASH ]{RESET} {LIGHT_GREEN}→ Crash timer is currently {status}{RESET}")
                    else:
                        print(f"{RED}[ ERR ] Crash timer not available{RESET}")
                elif cmd.startswith('des - '):
                    target = cmd.split('des - ', 1)[1].upper()
                    if target in CONTEXT_NAMES:
                        if handle_context_switch(target):
                            current_context = target
                    else:
                        print(f"{RED}[ ERR ] Unknown Context: {target}{RESET}")
                elif cmd == 'help':
                    print(f"{YELLOW}System Information Commands:{RESET}")
                    print(f"{LIGHT_GREEN}  /info -o     - OS information{RESET}")
                    print(f"{LIGHT_GREEN}  /info -c     - CPU information{RESET}")
                    print(f"{LIGHT_GREEN}  /info -r     - Memory usage{RESET}")
                    print(f"{LIGHT_GREEN}  /info -d     - Disk usage{RESET}")
                    print(f"{LIGHT_GREEN}  /info -u     - System uptime{RESET}")
                    print(f"{LIGHT_GREEN}  /info -t     - Current time{RESET}")
                    print(f"{LIGHT_GREEN}  /test -r     - Memory test{RESET}")
                    print(f"{LIGHT_GREEN}  /test -c     - CPU test{RESET}")
                    print(f"{LIGHT_GREEN}  /test -a     - All tests{RESET}")
                    print(f"{LIGHT_GREEN}  /set -c      - Clear memory{RESET}")
                    print(f"{LIGHT_GREEN}  /set -s      - Show startup effects{RESET}")
                    print(f"{LIGHT_GREEN}  /crash       - Crash timer status{RESET}")
                    print(f"{LIGHT_GREEN}  des - <ctx>  - Switch to context{RESET}")
                    print(f"{LIGHT_GREEN}  help         - Show this help{RESET}")
                else:
                    print(f"{RED}[ ERR ] Unknown System Information Command{RESET}")

            elif current_context == 'BI':
                cmd = input(f"{GREEN}BI> {RESET}").strip().lower()
                if cmd == '/run -bi':
                    basic_interpreter()
                elif cmd.startswith('des - '):
                    target = cmd.split('des - ', 1)[1].upper()
                    if target in CONTEXT_NAMES:
                        if handle_context_switch(target):
                            current_context = target
                    else:
                        print(f"{RED}[ ERR ] Unknown Context: {target}{RESET}")
                elif cmd == 'help':
                    print(f"{YELLOW}BASIC Interpreter Commands:{RESET}")
                    print(f"{LIGHT_GREEN}  /run -bi     - Start BASIC interpreter{RESET}")
                    print(f"{LIGHT_GREEN}  des - <ctx>  - Switch to context{RESET}")
                    print(f"{LIGHT_GREEN}  help         - Show this help{RESET}")
                else:
                    print(f"{RED}[ ERR ] Unknown BASIC Interpreter command{RESET}")

            else:
                current_context = 'CORE'

        except KeyboardInterrupt:
            print(f"\n{YELLOW}[ INFO ] Interrupted by user{RESET}")
            continue
        except Exception as e:
            # Never exit on error—print and keep going
            # Don't show crash timer exceptions
            if "crash_timer" not in str(e).lower():
                print(f"{RED}[ ERR ] Unhandled exception: {e}{RESET}")

if __name__ == '__main__':
    main()
