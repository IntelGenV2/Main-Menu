#!/usr/bin/env python3
import os
import re
from helpers import urn_to_dir, list_fs, list_wfe, sanitize_name, YELLOW, LIGHT_GREEN, RESET

GENERIC_ERR = "[ ERR ] → Locator error"

def handle_loc(cmd: str, base: str, fs_mode: bool, fs_root: str = None):
    out = []
    low = cmd.lower()

    # FS table display
    if low == '/loc -d' and fs_mode:
        out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Displaying: {base}{RESET}")
        real = urn_to_dir(base, fs_root)
        try:
            entries = list_fs(real)
        except Exception:
            return [GENERIC_ERR]
        for e in entries:
            actual = sanitize_name(e)
            full = os.path.join(real, actual)
            typ = "CHUNK" if os.path.isdir(full) else "BLOCK"
            ext = "" if typ == "CHUNK" else f"*{e.rsplit('*',1)[-1]}"
            out.append(f"  {e:<20} {typ:<8} {ext}")
        return out

    # WFE/simple display
    if low == '/loc -d':
        out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Displaying: {base}{RESET}")
        real = urn_to_dir(base, fs_root) if fs_mode else base
        try:
            entries = list_fs(real) if fs_mode else list_wfe(real)
        except Exception:
            return [GENERIC_ERR]
        for e in entries:
            out.append(f"  • {e}")
        return out

    # Search
    if low.startswith('/loc -s '):
        pat = cmd.split('/loc -s',1)[1].strip()
        out.append(f"{YELLOW}[ SEARCH ]{RESET} {LIGHT_GREEN}→ Searching in {base}{RESET}")
        real = urn_to_dir(base, fs_root) if fs_mode else base
        entries = list_fs(real) if fs_mode else []
        if not fs_mode:
            for root, dirs, files in os.walk(real):
                entries.extend(dirs + files)
        for e in entries:
            if re.search(pat, e, re.IGNORECASE):
                out.append(f"  • {e}")
        return out

    # Peek
    if low.startswith('/loc -p '):
        urn = cmd.split('/loc -p',1)[1].strip()
        real = urn_to_dir(urn, fs_root) if fs_mode else urn.replace(':', os.sep)
        if os.path.isdir(real):
            out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Peeking at: {urn}{RESET}")
            entries = list_fs(real) if fs_mode else list_wfe(real)
            for e in entries:
                out.append(f"  • {e}")
        else:
            out.append(GENERIC_ERR)
        return out

    out.append(GENERIC_ERR)
    return out
