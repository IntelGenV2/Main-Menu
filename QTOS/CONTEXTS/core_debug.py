#!/usr/bin/env python3
"""
QTOS v0.0.5.0 - Quantified Ternary OS (DEBUG VERSION - No crashes, no RAM limits)
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
    # DEBUG: Disable crash timer completely
    CRASH_TIMER_AVAILABLE = False
    def start_crash_timer():
        pass
    def is_system_crashed():
        return False
    def enable_crashes():
        return "Crash timer disabled in debug mode"
    def disable_crashes():
        return "Crash timer disabled in debug mode"
    def get_crash_status():
        return False
except ImportError as e:
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
    """DEBUG: Disabled boot limits check"""

def check_memory_usage():
    """DEBUG: Disabled memory usage check"""
    # Do nothing - memory limits disabled for debugging
    pass

def startup_animation():
    """Simplified startup animation for debug mode"""
    print(f"{LIGHT_GREEN}╔═════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{LIGHT_GREEN}║                    QTOS DEBUG MODE v0.0.5.0                 ║{RESET}")
    print(f"{LIGHT_GREEN}║                                                             ║{RESET}")
    print(f"{LIGHT_GREEN}║            ░██████╗░░████████╗░░█████╗░░░██████╗            ║{RESET}")
    print(f"{LIGHT_GREEN}║            ██╔═══██╗░╚══██╔══╝░██╔══██╗░██╔════╝            ║{RESET}")
    print(f"{LIGHT_GREEN}║            ██║██╗██║░░░░██║░░░░██║░░██║░╚█████╗░            ║{RESET}")
    print(f"{LIGHT_GREEN}║            ╚██████╔╝░░░░██║░░░░██║░░██║░░╚═══██╗            ║{RESET}")
    print(f"{LIGHT_GREEN}║            ░╚═██╔═╝░░░░░██║░░░░╚█████╔╝░██████╔╝            ║{RESET}")
    print(f"{LIGHT_GREEN}║            ░░░╚═╝░░░░░░░╚═╝░░░░░╚════╝░░╚═════╝░            ║{RESET}")
    print(f"{LIGHT_GREEN}║                                                             ║{RESET}")
    print(f"{LIGHT_GREEN}║  Quantified Ternary Operating System                        ║{RESET}")
    print(f"{LIGHT_GREEN}║  DEBUG MODE - No crashes, no RAM limits                     ║{RESET}")
    print(f"{LIGHT_GREEN}╚═════════════════════════════════════════════════════════════╝{RESET}")
    time.sleep(1)

def handle_context_switch(target_context):
    """Handle context switching with debug mode"""
    if target_context not in CONTEXT_NAMES:
        print(f"{RED}[ ERR ] Unknown context: {target_context}{RESET}")
        return False
    
    # DEBUG: Skip memory checks
    print(f"{YELLOW}[ DEBUG ]{RESET} {LIGHT_GREEN}→ Memory checks disabled{RESET}")
    
    # Switch context
    loading(f"Entering {CONTEXT_NAMES[target_context]} Context", dots=5, delay=0.2)
    record_access(target_context)
    print(f"{LIGHT_GREEN}[ ACCESS ] → Entered {CONTEXT_NAMES[target_context]} Context{RESET}")
    return True

# ─── Enhanced BASIC Interpreter with HELP command ────────────────────────────────
def basic_interpreter_debug():
    """Enhanced BASIC interpreter with HELP command and proper exit handling"""
    if not BASIC_AVAILABLE:
        print(f"{RED}[ ERR ] BASIC Interpreter module not found.{RESET}")
        print(f"{YELLOW}[ INFO ] Ensure all BASIC files are present in the BASIC directory.{RESET}")
        return
    
    print(f"{LIGHT_GREEN}QTOS BASIC Interpreter v1.0 (DEBUG MODE){RESET}")
    print(f"{YELLOW}Type 'EXIT' to return to QTOS{RESET}")
    print(f"{YELLOW}Type 'HELP' for BASIC commands{RESET}")
    print()
    
    try:
        # Add BASIC directory to path
        BASIC_DIR = Path(__file__).parent.parent / "BASIC"
        sys.path.insert(0, str(BASIC_DIR))
        
        from interpreter import main as basic_main
        
        # Create a custom help function
        def show_basic_help():
            print(f"{LIGHT_GREEN}BASIC Commands:{RESET}")
            print(f"{YELLOW}  RUN             - Execute current program{RESET}")
            print(f"{YELLOW}  LIST            - Display program lines{RESET}")
            print(f"{YELLOW}  NEW             - Clear current program{RESET}")
            print(f"{YELLOW}  SAVE <filename> - Save program to file{RESET}")
            print(f"{YELLOW}  LOAD <filename> - Load program from file{RESET}")
            print(f"{YELLOW}  EXIT            - Return to QTOS{RESET}")
            print(f"{YELLOW}  HELP            - Show this help{RESET}")
            print()
            print(f"{LIGHT_GREEN}Direct Mode Commands:{RESET}")
            print(f"{YELLOW}  PRINT <expr>    - Print value{RESET}")
            print(f"{YELLOW}  LET var = val   - Assign variable{RESET}")
            print(f"{YELLOW}  INPUT var       - Get user input{RESET}")
            print()
            print(f"{LIGHT_GREEN}Program Statements:{RESET}")
            print(f"{YELLOW}  Line numbers required for program mode{RESET}")
            print(f"{YELLOW}  Variables: A-Z, A0-Z9{RESET}")
            print(f"{YELLOW}  Control: IF-THEN, FOR-NEXT, GOTO{RESET}")
            print(f"{YELLOW}  Data: DATA/READ/RESTORE{RESET}")
        
        # Override the input function to handle HELP
        original_input = input
        def custom_input(prompt):
            user_input = original_input(prompt)
            if user_input.strip().upper() == 'HELP':
                show_basic_help()
                return original_input(prompt)  # Get another input after showing help
            return user_input
        
        # Temporarily replace input function
        import builtins
        builtins.input = custom_input
        
        try:
            # Run the BASIC interpreter
            basic_main()
            print(f"{LIGHT_GREEN}Returning to QTOS...{RESET}")
        finally:
            # Restore original input function
            builtins.input = original_input
            
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user{RESET}")
    except Exception as e:
        print(f"{RED}[ ERR ] BASIC interpreter error: {e}{RESET}")

# ─── Main loop ───────────────────────────────────────────────────────────────────
def main():
    ensure_root()
    check_boot_limits()
    startup_animation()

    print(f"{LIGHT_GREEN}QTOS v0.0.5.0 Initialized (DEBUG MODE){RESET}\n")
    # Core module stays resident
    record_access('CORE')
    
    # DEBUG: Crash timer disabled
    print(f"{YELLOW}[ DEBUG ]{RESET} {LIGHT_GREEN}→ Crash timer disabled{RESET}")

    global current_context
    while True:
        try:
            if current_context == 'CORE':
                cmd = input(f"{GREEN}CORE> {RESET}").strip().lower()
                if cmd.startswith('des - '):
                    target = cmd.split('des - ', 1)[1].upper()
                    if handle_context_switch(target):
                        current_context = target
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
                        print(f"{RED}[ ERR ] Unknown context{RESET}")
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
                elif cmd.startswith('des - '):
                    target = cmd.split('des - ', 1)[1].upper()
                    if target in CONTEXT_NAMES:
                        if handle_context_switch(target):
                            current_context = target
                    else:
                        print(f"{RED}[ ERR ] Unknown context{RESET}")
                else:
                    print(f"{RED}[ ERR ] Unknown System Information Command{RESET}")

            elif current_context == 'BI':
                cmd = input(f"{GREEN}BI> {RESET}").strip().lower()
                if cmd == '/run -bi':
                    basic_interpreter_debug()
                elif cmd.startswith('des - '):
                    target = cmd.split('des - ', 1)[1].upper()
                    if target in CONTEXT_NAMES:
                        if handle_context_switch(target):
                            current_context = target
                    else:
                        print(f"{RED}[ ERR ] Unknown context{RESET}")
                elif cmd == 'help':
                    print(f"{YELLOW}BASIC Interpreter Commands:{RESET}")
                    print(f"{LIGHT_GREEN}  /run -bi     - Start BASIC interpreter{RESET}")
                    print(f"{LIGHT_GREEN}  des - <ctx>  - Switch to context{RESET}")
                    print(f"{LIGHT_GREEN}  help         - Show this help{RESET}")
                else:
                    print(f"{RED}[ ERR ] Unknown BASIC Interpreter Command{RESET}")

            else:
                current_context = 'CORE'

        except KeyboardInterrupt:
            print(f"\n{YELLOW}[ INFO ] Interrupted by user{RESET}")
            continue
        except Exception as e:
            # Never exit on error—print and keep going
            print(f"{RED}[ ERR ] Unhandled exception: {e}{RESET}")

if __name__ == '__main__':
    main()
