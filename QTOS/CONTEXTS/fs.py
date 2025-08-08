#!/usr/bin/env python3
"""
QTOS v0.0.5.0 - Quantified Ternary OS (FS context)
"""
import os
import sys
from pathlib import Path
from helpers import GREEN, RED, YELLOW, LIGHT_GREEN, RESET, loading
from loc_handler import handle_loc
from mod_handler import handle_mod

# Context switching commands mapping for faster lookup
CONTEXT_SWITCHES = {
    'des - core': ('CORE', 'Returning to Core Context'),
    'des - wfe': ('WFE', 'Switching to Windows File Explorer Context'),
    'des - sg': ('SG', 'Switching to Snake Game Context'),
    'des - si': ('SI', 'Switching to System Information Context'),
    'des - bp': ('BP', 'Switching to BASIC Interpreter Context'),
}

def handle_fs(fs_urn_ref, fs_root):
    """Optimized file system context handler with command mapping"""
    while True:
        try:
            cmd = input(f"{GREEN}FS> {RESET}").strip()
            
            # Check for context switching commands first
            if cmd in CONTEXT_SWITCHES:
                target_context, message = CONTEXT_SWITCHES[cmd]
                loading(message, dots=3, delay=0.15)
                return target_context
            
            # Handle file system commands
            if cmd.startswith('/loc'):
                result, new_urn = handle_loc(cmd, fs_urn_ref[0], True, fs_root)
                if new_urn:
                    fs_urn_ref[0] = new_urn
                for line in result:
                    print(line)
            
            elif cmd.startswith('/mod'):
                result = handle_mod(cmd, base_urn=fs_urn_ref[0], fs_root=fs_root, fs_mode=True)
                print(result)
            
            elif cmd.startswith('/run'):
                # Run a file in the current working directory
                parts = cmd.split()
                if len(parts) >= 2:
                    filename = parts[1]
                    # Resolve the full path to the file
                    from helpers import urn_to_dir, sanitize_name
                    current_dir = urn_to_dir(fs_urn_ref[0], fs_root)
                    file_path = Path(current_dir) / sanitize_name(filename)
                    
                    if file_path.is_file():
                        try:
                            # Try to run the file based on its extension
                            if file_path.suffix.lower() in ['.py', '.pyw']:
                                # Python files
                                import subprocess
                                subprocess.Popen([sys.executable, str(file_path)])
                                print(f"{LIGHT_GREEN}[ RUN ] → Started Python script: {filename}{RESET}")
                            elif file_path.suffix.lower() in ['.exe', '.bat', '.cmd']:
                                # Executable files
                                import subprocess
                                subprocess.Popen([str(file_path)])
                                print(f"{LIGHT_GREEN}[ RUN ] → Started executable: {filename}{RESET}")
                            else:
                                # Try to open with default application
                                import subprocess
                                subprocess.Popen([str(file_path)], shell=True)
                                print(f"{LIGHT_GREEN}[ RUN ] → Opened file: {filename}{RESET}")
                        except Exception as e:
                            print(f"{RED}[ ERR ] Failed to run {filename}: {e}{RESET}")
                    else:
                        print(f"{RED}[ ERR ] File not found: {filename}{RESET}")
                else:
                    print(f"{RED}[ ERR ] Run command requires filename{RESET}")
            
            else:
                print(f"{RED}[ ERR ] Unknown File System Command{RESET}")
                
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[ INFO ] Returning to Core Context{RESET}")
            return 'CORE'
        except Exception as e:
            print(f"{RED}[ ERR ] File System error: {e}{RESET}")
            return 'CORE'
