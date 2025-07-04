#!/usr/bin/env python3
import os, shutil, time, re

RESET       = "\033[0m"
GREEN       = "\033[32m"
LIGHT_GREEN = "\033[92m"
YELLOW      = "\033[33m"
RED         = "\033[31m"

def loading(msg, dots=3, delay=0.3):
    print(f"{YELLOW}{msg}{RESET}", end="", flush=True)
    for _ in range(dots):
        time.sleep(delay)
        print(f"{YELLOW}.{RESET}", end="", flush=True)
    print()

def sanitize_name(name: str) -> str:
    return name.replace('*', '.')

def display_name(entry: str) -> str:
    return entry.replace('.', '*')

def urn_to_dir(urn: str, fs_root: str) -> str:
    if not urn or urn.lower() == 'base':
        return fs_root
    parts = urn.split(':')
    if parts[0].lower() == 'base':
        parts = parts[1:]
    return os.path.normpath(os.path.join(fs_root, *parts))

def list_fs(path: str):
    try:
        return sorted(display_name(e) for e in os.listdir(path))
    except:
        return []

def list_wfe(path: str):
    try:
        return sorted(display_name(e) for e in os.listdir(path))
    except:
        return []
