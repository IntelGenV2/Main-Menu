#!/usr/bin/env python3
"""
QTOS v0.0.5.0 - Quantified Ternary OS (WFE context)
"""
import os
import subprocess
from pathlib import Path
from helpers import GREEN, RED, YELLOW, LIGHT_GREEN, RESET, loading

# Context switching commands mapping for faster lookup
CONTEXT_SWITCHES = {
    'des - core': ('CORE', 'Returning to Core Context'),
    'des - fs': ('FS', 'Switching to File System Context'),
    'des - sg': ('SG', 'Switching to Snake Game Context'),
    'des - si': ('SI', 'Switching to System Information Context'),
    'des - bp': ('BP', 'Switching to BASIC Interpreter Context'),
}

def handle_wfe(wfe_path_ref):
    """Optimized Windows File Explorer context handler with command mapping"""
    while True:
        try:
            cmd = input(f"{GREEN}WFE> {RESET}").strip()
            
            # Check for context switching commands first
            if cmd in CONTEXT_SWITCHES:
                target_context, message = CONTEXT_SWITCHES[cmd]
                loading(message, dots=3, delay=0.15)
                return target_context
            
            # Handle WFE commands
            if cmd.startswith('/drive -'):
                drive = cmd.split('-', 1)[1].strip().upper()
                wfe_path_ref[0] = f"{drive}:\\"
                print(f"{LIGHT_GREEN}[ DRIVE ] → Switched to {drive}:\\{RESET}")
            
            elif cmd.startswith('/run'):
                exe = cmd.split(' ', 1)[1].strip()
                if wfe_path_ref[0]:
                    full_path = Path(wfe_path_ref[0]) / exe
                    if full_path.is_file():
                        try:
                            subprocess.Popen([str(full_path)])
                            print(f"{LIGHT_GREEN}[ RUN ] → Started {exe}{RESET}")
                        except Exception as e:
                            print(f"{RED}[ ERR ] Failed to run {exe}: {e}{RESET}")
                    else:
                        print(f"{RED}[ ERR ] {exe} not found{RESET}")
                else:
                    print(f"{RED}[ ERR ] No drive selected{RESET}")
            
            elif cmd.startswith('/loc'):
                # Handle location commands similar to FS context
                print(f"{YELLOW}[ INFO ] Location commands not implemented in WFE{RESET}")
            
            elif cmd.startswith('/mod'):
                # Handle modification commands similar to FS context
                print(f"{YELLOW}[ INFO ] Modification commands not implemented in WFE{RESET}")
            
            else:
                print(f"{RED}[ ERR ] Unknown Windows File Explorer Command{RESET}")
                
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[ INFO ] Returning to Core Context{RESET}")
            return 'CORE'
        except Exception as e:
            print(f"{RED}[ ERR ] Windows File Explorer error: {e}{RESET}")
            return 'CORE'
