#!/usr/bin/env python3
import os
from helpers import loading, RED, YELLOW, LIGHT_GREEN, RESET, GREEN, urn_to_dir
import loc_handler, mod_handler

CONTEXT_NAMES = {
    'CORE': 'Core',
    'FS':   'File System',
    'WFE':  'Windows File Explorer',
    'SG':   'Snake Game',
    'SI':   'System Information'
}

def handle_fs(fs_urn_ref, fs_root):
    cmd = input(f"{GREEN}FS> {RESET}").strip().lower()
    low = cmd

    # context switches
    if low == 'des - core':
        loading("Switching to Core", dots=6, delay=0.2)
        print(f"{LIGHT_GREEN}[ ACCESS ] → Returned to {CONTEXT_NAMES['CORE']} Context{RESET}")
        return 'CORE'
    if low == 'des - wfe':
        loading("Switching to File System", dots=6, delay=0.2)
        print(f"{LIGHT_GREEN}[ ACCESS ] → Entered BOSCHOS {CONTEXT_NAMES['WFE']} Context{RESET}")
        return 'WFE'
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
            for line in loc_handler.handle_loc(cmd, base=fs_urn_ref[0], fs_mode=True, fs_root=fs_root):
                print(line)
        else:
            print(mod_handler.handle_mod(cmd, base_urn=fs_urn_ref[0], fs_root=fs_root, fs_mode=True))
        return 'FS'

    print(f"{RED}[ ERR ] Unknown {CONTEXT_NAMES['FS']} command{RESET}")
    return 'FS'
