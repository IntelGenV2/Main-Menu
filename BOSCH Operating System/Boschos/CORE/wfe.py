#!/usr/bin/env python3
import os
from helpers import loading, RED, YELLOW, LIGHT_GREEN, RESET, GREEN
import loc_handler, mod_handler

CONTEXT_NAMES = {
    'CORE': 'Core',
    'FS':   'File System',
    'WFE':  'Windows File Explorer',
    'SG':   'Snake Game',
    'SI':   'System Information'
}

def handle_wfe(wfe_path_ref):
    cmd = input(f"{GREEN}WFE> {RESET}").strip().lower()
    low = cmd

    # context switches
    if low == 'des - core':
        loading("Switching to Core", dots=6, delay=0.2)
        print(f"{LIGHT_GREEN}[ ACCESS ] → Returned to {CONTEXT_NAMES['CORE']} Context{RESET}")
        return 'CORE'
    if low == 'des - fs':
        loading("Switching to File System", dots=6, delay=0.2)
        print(f"{LIGHT_GREEN}[ ACCESS ] → Entered BOSCHOS {CONTEXT_NAMES['FS']} Context{RESET}")
        return 'FS'
    if low == 'des - sg':
        loading("Switching to Snake Game", dots=6, delay=0.2)
        print(f"{LIGHT_GREEN}[ ACCESS ] → Entered BOSCHOS {CONTEXT_NAMES['SG']} Context{RESET}")
        return 'SG'
    if low == 'des - si':
        loading("Switching to System Information", dots=6, delay=0.2)
        print(f"{LIGHT_GREEN}[ ACCESS ] → Entered BOSCHOS {CONTEXT_NAMES['SI']} Context{RESET}")
        return 'SI'

    # /loc or /mod
    if low.startswith('/loc') or low.startswith('/mod'):
        if low.startswith('/loc'):
            base = wfe_path_ref[0] or os.getcwd()
            for line in loc_handler.handle_loc(cmd, base=base, fs_mode=False):
                print(line)
        else:
            base = wfe_path_ref[0] or os.getcwd()
            print(mod_handler.handle_mod(cmd, base_path=base, fs_root=None, fs_mode=False))
        return 'WFE'

    print(f"{RED}[ ERR ] Unknown {CONTEXT_NAMES['WFE']} command{RESET}")
    return 'WFE'
