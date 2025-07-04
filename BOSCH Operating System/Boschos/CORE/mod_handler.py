#!/usr/bin/env python3
import os
import shutil
from helpers import urn_to_dir, sanitize_name, YELLOW, LIGHT_GREEN, RESET, RED
import edit_handler

GENERIC_ERR = f"{RED}[ ERR ] → Modification error{RESET}"

def handle_mod(cmd: str, *, base_urn=None, base_path=None, fs_root=None, fs_mode: bool):
    parts = cmd.split()
    if len(parts) < 2:
        return GENERIC_ERR
    op = parts[1].lower()

    # parse '/key=val'
    params = {}
    for p in parts[2:]:
        if p.startswith('/') and '=' in p:
            key, val = p[1:].split('=', 1)
            params[key.lower()] = val

    name = params.get('name')
    loc  = params.get('loc')
    if not name or not loc:
        return GENERIC_ERR

    if fs_mode:
        if loc.lower() == 'eloc':
            target = urn_to_dir(base_urn, fs_root); display = base_urn
        else:
            target = urn_to_dir(loc, fs_root); display = loc
    else:
        if loc.lower() == 'eloc':
            target = base_path; display = base_path
        else:
            target = loc.replace(':', os.sep); display = target

    fs_name = sanitize_name(name)
    path    = os.path.join(target, fs_name)

    try:
        if op == '-e':
            if not os.path.isfile(path):
                return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ File not found: {name}{RESET}"
            edit_handler.edit_file(path, display)
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Finished editing \"{name}\"{RESET}"

        if op == '-c':
            typ = params.get('type', 'chunk')
            if typ == 'chunk':
                os.makedirs(path, exist_ok=True)
            else:
                open(path, 'w').close()
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Created \"{name}\" in {display}{RESET}"

        if op == '-d':
            if os.path.isdir(path): shutil.rmtree(path)
            else:                   os.remove(path)
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Deleted \"{name}\" from {display}{RESET}"

        if op == '-r':
            new = params.get('name2')
            if not new: return GENERIC_ERR
            dst = os.path.join(os.path.dirname(path), sanitize_name(new))
            os.rename(path, dst)
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Renamed \"{name}\" to \"{new}\" in {display}{RESET}"

        if op in ('-y','-m'):
            dst = params.get('loc2') or params.get('name2')
            if not dst: return GENERIC_ERR
            if fs_mode:
                dst_path = urn_to_dir(dst, fs_root); display_dst = dst
            else:
                dst_path = dst.replace(':', os.sep); display_dst = dst_path

            if op=='-y':
                if os.path.isdir(path):
                    shutil.copytree(path, os.path.join(dst_path, fs_name))
                else:
                    shutil.copy2(path, dst_path)
                verb = "Copied"
            else:
                shutil.move(path, dst_path); verb = "Moved"

            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ {verb} \"{name}\" to {display_dst}{RESET}"

        return GENERIC_ERR

    except Exception:
        return GENERIC_ERR
