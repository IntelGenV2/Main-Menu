#!/usr/bin/env python3
"""
System Info context for BOSCHOS v0.0.4.0
"""
import time
import os
from datetime import datetime
from helpers import YELLOW, LIGHT_GREEN, RESET, RED

RAM_CAPACITY_KB  = 16
DISK_CAPACITY_KB = 1000

MODULE_FILES = {
    'CORE': 'core.py',
    'FS':   'fs.py',
    'WFE':  'wfe.py',
    'SG':   'sg.py',
    'SI':   'si.py',
    'BP':   'bp.py'
}

_ACCESSED_MODULES = set()

def record_access(context_name: str):
    if context_name in MODULE_FILES:
        _ACCESSED_MODULES.add(MODULE_FILES[context_name])

def handle_info(cmd: str, start_time: float, fs_root: str):
    parts = cmd.strip().split()
    if len(parts) != 2 or not parts[1].startswith('-'):
        return [f"{RED}[ ERR ] Unknown System Information command{RESET}"]

    flag = parts[1].lower()
    lines = []

    if flag == '-o':
        lines.append(f"{YELLOW}[ OS  ]{RESET} {LIGHT_GREEN}→ BOSCHOS v0.0.4.0 (QuantumByte){RESET}")

    elif flag == '-c':
        lines.append(f"{YELLOW}[ CPU ]{RESET} {LIGHT_GREEN}→ QBT 3 | Usage: n/a{RESET}")

    elif flag == '-r':
        total_bytes = 0
        for fname in _ACCESSED_MODULES:
            try:
                total_bytes += os.path.getsize(os.path.join(os.path.dirname(__file__), '..', fname))
            except OSError:
                pass
        used_kb = min(total_bytes // 1024, RAM_CAPACITY_KB)
        lines.append(f"{YELLOW}[ RAM ]{RESET} {LIGHT_GREEN}→ {used_kb} KB / {RAM_CAPACITY_KB} KB{RESET}")

    elif flag == '-d':
        total_bytes = 0
        for root, dirs, files in os.walk(fs_root):
            for f in files:
                try:
                    total_bytes += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
        used_kb = min(total_bytes // 1024, DISK_CAPACITY_KB)
        lines.append(f"{YELLOW}[ DISK]{RESET} {LIGHT_GREEN}→ {used_kb} KB / {DISK_CAPACITY_KB} KB{RESET}")

    elif flag == '-u':
        uptime = time.time() - start_time
        days, rem = divmod(uptime, 86400)
        hrs, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        lines.append(f"{YELLOW}[ UPT ]{RESET} {LIGHT_GREEN}→ {int(days)}d {int(hrs)}h {int(mins)}m {int(secs)}s{RESET}")

    elif flag == '-t':
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"{YELLOW}[ TIME]{RESET} {LIGHT_GREEN}→ {now}{RESET}")

    else:
        lines.append(f"{RED}[ ERR ] Unknown System Information flag{RESET}")

    return lines
