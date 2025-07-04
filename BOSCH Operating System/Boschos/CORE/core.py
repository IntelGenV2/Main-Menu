#!/usr/bin/env python3
"""
BOSCHOS v0.0.4.0 - Text-based OS Simulator (core + dispatcher)
"""
import os
import time
from helpers import LIGHT_GREEN, GREEN, RESET, loading, YELLOW, RED

from fs import handle_fs
from wfe import handle_wfe
from sg import snake_game
from si import handle_info, record_access

try:
    from bp import basic_interpreter
    BASIC_AVAILABLE = True
except ModuleNotFoundError:
    BASIC_AVAILABLE = False
    def basic_interpreter():
        print(f"{RED}[ ERR ]{RESET} BASIC Interpreter module not found. Please add bp.py to enable this context.")

HOME_DIR      = os.path.expanduser("~")
FS_ROOT       = os.path.join(HOME_DIR, "Documents", "Boschos")
START_TIME    = time.time()

CONTEXT_NAMES = {
    'CORE': 'Core',
    'FS':   'File System',
    'WFE':  'Windows File Explorer',
    'SG':   'Snake Game',
    'SI':   'System Information',
    'BP':   'BASIC Interpreter'
}

current_context = 'CORE'
fs_urn_ref      = ['base']
wfe_path_ref    = [None]

def ensure_root():
    os.makedirs(FS_ROOT, exist_ok=True)

def startup_animation():
    banner = [
        r"  ____     ___    ____    ____   _   _    ___    ____   ",
        r" | __ )   / _ \  / ___|  /  __| | | | |  / _ \  / ___|  ",
        r" |  _ \  | | | | \___ \  | |    | '-' | | | | | \___ \  ",
        r" | |_) | | |_| |  ___) | | |__  | .-. | | |_| |  ___) | ",
        r" |____/   \___/  |____/  \____| |_| |_|  \___/  |____/  "
    ]
    for line in banner:
        print(line.center(80))
        time.sleep(0.1)
    print()
    steps = [
        ("Loading kernel",        0.1, 5),
        ("Mounting file systems", 0.12,5),
        ("Checking hardware",     0.14,5),
        ("Initializing UI",       0.16,5),
        ("Loading modules",       0.18,5),
        ("Starting services",     0.20,5),
        ("Applying settings",     0.22,5),
        ("Finalizing",            0.24,5),
    ]
    COL_OK = 40
    for text, delay, dots in steps:
        print(f"{YELLOW}{text}", end="", flush=True)
        for _ in range(dots):
            time.sleep(delay)
            print(".", end="", flush=True)
        spaces = max(1, COL_OK - (len(text) + dots))
        print(f"{' '*spaces}{LIGHT_GREEN}[OK]{RESET}")
    final_text = "Initializing BOSCHOS"
    print(f"{YELLOW}{final_text}", end="", flush=True)
    for _ in range(12):
        time.sleep(0.3)
        print(".", end="", flush=True)
    spaces = max(1, COL_OK - (len(final_text) + 12))
    print(f"{' '*spaces}{LIGHT_GREEN}[OK]{RESET}")

def main():
    ensure_root()
    startup_animation()
    print(f"{LIGHT_GREEN}BOSCHOS v0.0.4.0 Initialized{RESET}")

    record_access('CORE')
    global current_context

    while True:
        if current_context == 'CORE':
            cmd = input(f"{GREEN}CORE> {RESET}").strip().lower()
            if cmd == 'des - fs':
                loading("Entering File System", dots=6, delay=0.2)
                print(f"{YELLOW}[ ACCESS ]{RESET} {LIGHT_GREEN}→ Entered BOSCHOS File System Context{RESET}")
                current_context = 'FS'; record_access('FS')
            elif cmd == 'des - wfe':
                loading("Entering Windows File Explorer", dots=6, delay=0.2)
                print(f"{YELLOW}[ ACCESS ]{RESET} {LIGHT_GREEN}→ Entered BOSCHOS Windows File Explorer Context{RESET}")
                current_context = 'WFE'; record_access('WFE')
            elif cmd == 'des - sg':
                loading("Entering Snake Game", dots=6, delay=0.2)
                print(f"{YELLOW}[ ACCESS ]{RESET} {LIGHT_GREEN}→ Entered BOSCHOS Snake Game Context{RESET}")
                current_context = 'SG'; record_access('SG')
            elif cmd == 'des - si':
                loading("Entering System Information", dots=6, delay=0.2)
                print(f"{YELLOW}[ ACCESS ]{RESET} {LIGHT_GREEN}→ Entered BOSCHOS System Information Context{RESET}")
                current_context = 'SI'; record_access('SI')
            elif cmd == 'des - bp':
                if BASIC_AVAILABLE:
                    loading("Entering BASIC Interpreter", dots=6, delay=0.2)
                    print(f"{YELLOW}[ ACCESS ]{RESET} {LIGHT_GREEN}→ Entered BOSCHOS BASIC Interpreter Context{RESET}")
                    current_context = 'BP'; record_access('BP')
                else:
                    print(f"{RED}[ ERR ] BASIC Interpreter not available. Add bp.py and restart.{RESET}")
            else:
                print(f"{RED}[ ERR ] Unknown Core command{RESET}")

        elif current_context == 'FS':
            next_ctx = handle_fs(fs_urn_ref, FS_ROOT)
            if next_ctx in CONTEXT_NAMES:
                current_context = next_ctx; record_access(next_ctx)

        elif current_context == 'WFE':
            next_ctx = handle_wfe(wfe_path_ref)
            if next_ctx in CONTEXT_NAMES:
                current_context = next_ctx; record_access(next_ctx)

        elif current_context == 'SG':
            cmd = input(f"{GREEN}SG> {RESET}").strip().lower()
            if cmd == '/run - sg':
                snake_game()
            elif cmd.startswith('des - '):
                tgt = cmd.split('des - ',1)[1].upper()
                if tgt in CONTEXT_NAMES and tgt != 'SG':
                    loading(f"Switching to {CONTEXT_NAMES[tgt]}", dots=6, delay=0.2)
                    print(f"{YELLOW}[ ACCESS ]{RESET} {LIGHT_GREEN}→ Entered BOSCHOS {CONTEXT_NAMES[tgt]} Context{RESET}")
                    current_context = tgt; record_access(tgt)
                else:
                    print(f"{RED}[ ERR ] Unknown Snake Game command{RESET}")
            else:
                print(f"{RED}[ ERR ] Unknown Snake Game command{RESET}")

        elif current_context == 'SI':
            cmd = input(f"{GREEN}SI> {RESET}").strip().lower()
            if cmd.startswith('/info '):
                for line in handle_info(cmd, START_TIME, FS_ROOT):
                    print(line)
            elif cmd.startswith('des - '):
                tgt = cmd.split('des - ',1)[1].upper()
                if tgt in CONTEXT_NAMES and tgt != 'SI':
                    loading(f"Switching to {CONTEXT_NAMES[tgt]}", dots=6, delay=0.2)
                    print(f"{YELLOW}[ ACCESS ]{RESET} {LIGHT_GREEN}→ Entered BOSCHOS {CONTEXT_NAMES[tgt]} Context{RESET}")
                    current_context = tgt; record_access(tgt)
                else:
                    print(f"{RED}[ ERR ] Unknown System Information command{RESET}")
            else:
                print(f"{RED}[ ERR ] Unknown System Information command{RESET}")

        elif current_context == 'BP':
            basic_interpreter()

        else:
            current_context = 'CORE'; record_access('CORE')

if __name__ == '__main__':
    main()
