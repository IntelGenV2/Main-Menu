#!/usr/bin/env python3
"""
BOSCHOS v0.5 - Text-based OS Simulator
Contexts: CORE, FS (BOSCHOS FS), WFE (Windows File Explorer simulation)
Interactive CLI; run from a terminal to keep it open.
Filenames displayed with '*' for extension separator, stored with '.'.
"""
import os
import sys
import shutil
import time

# Globals
FS_ROOT = os.path.abspath(r"C:\Boschos")
current_context = 'CORE'
fs_urn = 'base'     # default location is base
wfe_path = None     # Windows File Explorer path
# Ensure base directory exists
os.makedirs(FS_ROOT, exist_ok=True)

# Loading animation helper
def loading(msg, dots=3, delay=0.3):
    print(msg, end="", flush=True)
    for _ in range(dots):
        time.sleep(delay)
        print('.', end="", flush=True)
    print()

# Sanitize filesystem names: '*' → '.' on disk
def sanitize_name(name: str) -> str:
    return name.replace('*', '.')

# Convert filesystem filenames to display: 'file.txt' → 'file*txt'
def display_name(entry: str) -> str:
    if '.' in entry:
        n, e = entry.rsplit('.',1)
        return f"{n}*{e}"
    return entry

# List entries for BOSCHOS FS
def list_fs(path: str):
    try:
        return sorted(display_name(e) for e in os.listdir(path))
    except OSError:
        return []

# List entries for Windows FS
def list_wfe(path: str):
    try:
        return sorted(os.listdir(path))
    except OSError:
        return []

# Convert URN to real path under FS_ROOT
def urn_to_dir(urn: str) -> str:
    if not urn or urn.lower()=='base':
        return FS_ROOT
    parts = urn.split(':')
    if parts[0].lower()=='base':
        parts = parts[1:]
    return os.path.normpath(os.path.join(FS_ROOT, *parts))

# CORE context handler
def handle_core():
    global current_context
    cmd = input('CORE> ').strip()
    low = cmd.lower()
    if low == 'des - fs':
        loading('Entering File System')
        print('[ ACCESS ] → Entered BOSCHOS File System')
        current_context = 'FS'
    elif low == 'des - wfe':
        loading('Entering Windows FS')
        print('[ ACCESS ] → Entered Windows File Explorer')
        current_context = 'WFE'
    else:
        print('Unknown CORE command')

# FS context handler
def handle_fs():
    global current_context, fs_urn
    cmd = input('FS> ').strip()
    low = cmd.lower()

    if low == 'des - core':
        loading('Returning to CORE')
        print('[ CORE ] → Back to CORE')
        current_context = 'CORE'
        return

    # Enter a location
    if low.startswith('/loc -e '):
        fs_urn = cmd.split('/loc -e',1)[1].strip()
        print(f'[ LOC ] → Entered location: {fs_urn}')
        return

    # Display entered location
    if low == '/loc -d':
        path = urn_to_dir(fs_urn)
        if not os.path.isdir(path):
            print(f'[ ERR ] → Location not found: {fs_urn}')
        else:
            print(f'[ LOC ] → Displaying location: {fs_urn}')
            for e in list_fs(path):
                print(f'  • {e}')
        return

    # Peek at a location without entering
    if low.startswith('/loc -n '):
        urn = cmd.split('/loc -n',1)[1].strip()
        path = urn_to_dir(urn)
        if not os.path.isdir(path):
            print(f'[ ERR ] → Location not found: {urn}')
        else:
            print(f'[ LOC ] → Peeking at: {urn}')
            for e in list_fs(path):
                print(f'  • {e}')
        return

    # Invalid loc command
    if low.startswith('/loc - '):
        print('[ ERR ] → Invalid /loc command; use "/loc -e <URN>", "/loc -d", or "/loc -n <URN>"')
        return

    # Modification commands
    if low.startswith('/mod -'):
        parts = cmd.split()
        op = parts[1].lower()
        params = {p.split('=',1)[0].lstrip('/'): p.split('=',1)[1] for p in parts[2:] if '=' in p}
        # Determine target URN
        urn_ref = params.get('loc','eloc')
        target_urn = fs_urn if urn_ref.lower()=='eloc' else params.get('loc', fs_urn)
        path = urn_to_dir(target_urn)
        name_raw = params.get('name','')
        name_fs = sanitize_name(name_raw)
        try:
            if op == '-c':
                typ = params.get('type','chunk')
                tgt = os.path.join(path, name_fs)
                if typ == 'chunk': os.makedirs(tgt, exist_ok=True)
                else: open(tgt,'w').close()
                print(f'[ MOD ] → Created {typ} "{name_raw}" in {target_urn}')
            elif op == '-d':
                tgt = os.path.join(path, name_fs)
                if os.path.isdir(tgt): shutil.rmtree(tgt)
                elif os.path.exists(tgt): os.remove(tgt)
                print(f'[ MOD ] → Deleted "{name_raw}" from {target_urn}')
            elif op == '-r':
                new_raw = params.get('to','')
                new_fs = sanitize_name(new_raw)
                os.rename(os.path.join(path,name_fs), os.path.join(path,new_fs))
                print(f'[ MOD ] → Renamed "{name_raw}" to "{new_raw}" in {target_urn}')
            elif op == '-y':
                src_raw = params.get('src','')
                dst_urn = params.get('loc2','base')
                src_path = os.path.join(path, sanitize_name(src_raw))
                dst_path = urn_to_dir(dst_urn)
                if os.path.isdir(src_path): shutil.copytree(src_path, os.path.join(dst_path, os.path.basename(src_path)))
                else: shutil.copy2(src_path, dst_path)
                print(f'[ MOD ] → Copied "{src_raw}" to {dst_urn}')
            elif op == '-m':
                src_raw = params.get('src','')
                dst_urn = params.get('loc2','base')
                shutil.move(os.path.join(path, sanitize_name(src_raw)), urn_to_dir(dst_urn))
                print(f'[ MOD ] → Moved "{src_raw}" to {dst_urn}')
            else:
                print('Unknown FS command')
        except Exception as e:
            print(f'[ ERR ] → {e}')
        return

    print('Unknown FS command')

# WFE context handler
def handle_wfe():
    global current_context, wfe_path
    cmd = input('WFE> ').strip()
    low = cmd.lower()

    if low == 'des - core':
        loading('Returning to CORE')
        print('[ CORE ] → Back to CORE')
        current_context = 'CORE'
        return

    if low.startswith('/drive -'):
        d = cmd.split('-',1)[1].strip().strip(':').upper()
        p = f"{d}:/"
        if os.path.isdir(p):
            wfe_path = p
            print(f'[ LOC ] → Displaying: {p}')
            for n in list_wfe(p): print(f'  • {n}')
        else:
            print(f'[ ERR ] → Drive not found: {p}')
        return

    if low.startswith('/loc -e '):
        wfe_path = cmd.split('/loc -e',1)[1].strip().replace(':', os.sep)
        print(f'[ LOC ] → Entered WFE Location: {wfe_path}')
        return

    if low == '/loc -d':
        if not wfe_path:
            print('[ LOC ] → No drive selected')
        else:
            print(f'[ LOC ] → Displaying: {wfe_path}')
            for n in list_wfe(wfe_path): print(f'  • {n}')
        return

    if low.startswith('/loc -n '):
        urn = cmd.split('/loc -n',1)[1].strip()
        path = urn.replace(':', os.sep)
        if not os.path.isdir(path):
            print(f'[ ERR ] → Path not found: {urn}')
        else:
            print(f'[ LOC ] → Peeking at: {urn}')
            for n in list_wfe(path): print(f'  • {n}')
        return

    if low.startswith('/loc - '):
        print('[ ERR ] → Invalid /loc command; use "/loc -e <P>", "/loc -d", or "/loc -n <P>"')
        return

    if low.startswith('/mod -'):
        parts = cmd.split()
        op = parts[1].lower()
        params = {p.split('=',1)[0].lstrip('/'):p.split('=',1)[1] for p in parts[2:] if '=' in p}
        base = wfe_path or ''
        name_raw = params.get('name','')
        name_fs = sanitize_name(name_raw)
        try:
            if op == '-c':
                tgt = os.path.join(base, name_fs)
                if params.get('type','chunk')=='chunk': os.makedirs(tgt, exist_ok=True)
                else: open(tgt,'w').close()
                print('[ MOD ] → -c operation invoked on Windows FS.')
            elif op == '-d':
                tgt = os.path.join(base, name_fs)
                if os.path.isdir(tgt): shutil.rmtree(tgt)
                else: os.remove(tgt)
                print('[ MOD ] → -d operation invoked on Windows FS.')
            elif op == '-r':
                new_fs = sanitize_name(params.get('to',''))
                os.rename(os.path.join(base,name_fs), os.path.join(base,new_fs))
                print('[ MOD ] → -r operation invoked on Windows FS.')
            elif op == '-y':
                dst = sanitize_name(params.get('to',''))
                srcp = os.path.join(base,name_fs); dstp = os.path.join(base,dst)
                if os.path.isdir(srcp): shutil.copytree(srcp,dstp)
                else: shutil.copy2(srcp,dstp)
                print('[ MOD ] → -y operation invoked on Windows FS.')
            elif op == '-m':
                dst = sanitize_name(params.get('to',''))
                shutil.move(os.path.join(base,name_fs), os.path.join(base,dst))
                print('[ MOD ] → -m operation invoked on Windows FS.')
            else:
                print('Unknown WFE command')
        except Exception as e:
            print(f'[ ERR ] → {e}')
        return

    print('Unknown WFE command')

# Main loop
def main():
    while True:
        if current_context == 'CORE':
            handle_core()
        elif current_context == 'FS':
            handle_fs()
        elif current_context == 'WFE':
            handle_wfe()

if __name__ == '__main__':
    main()
