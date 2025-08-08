#!/usr/bin/env python3
import os
import re
from pathlib import Path
from helpers import YELLOW, LIGHT_GREEN, RESET, RED, GREEN

def edit_file(filepath, urn_label):
    """
    Optimized text-based editor for BOSCHOS:
      [ MOD ] → Editing "<FILENAME>" in <URN>
    Commands (one flag per command):
      /edit -i  <n>        – insert one line at position n (only append at end)
      /edit -ii            – enter/exit multi-line insert mode
      /edit -d  <n>        – delete line n
      /edit -dd <n>-<m>    – delete lines n through m
      /edit -r  <n>        – replace line n
      /edit -rr <n>-<m>    – enter/exit multi-line replace mode
      /edit -v  <n>        – view single line n
      /edit -vv <n>-<m>    – view lines n through m
      /edit -vvv           – view whole doc, pause every 20 lines
      /edit -vvvv          – view whole doc unbroken
      /edit -w             – write & quit
    """
    # Optimized file reading
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except (OSError, IOError) as e:
        print(f"{RED}[ ERR ] Failed to read file: {e}{RESET}")
        return
    
    fname = os.path.basename(filepath)

    print(f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Editing \"{fname}\" in {urn_label}{RESET}")
    print(
        f"Commands: {YELLOW}/edit -i{RESET} {RED}<n>{RESET}, "
        f"{YELLOW}-ii{RESET}, "
        f"{YELLOW}-d{RESET} {RED}<n>{RESET}, "
        f"{YELLOW}-dd{RESET} {RED}<n>-<m>{RESET}, "
        f"{YELLOW}-r{RESET} {RED}<n>{RESET}, "
        f"{YELLOW}-rr{RESET} {RED}<n>-<m>{RESET}, "
        f"{YELLOW}-v{RESET} {RED}<n>{RESET}, "
        f"{YELLOW}-vv{RESET} {RED}<n>-<m>{RESET}, "
        f"{YELLOW}-vvv{RESET}, "
        f"{YELLOW}-vvvv{RESET}, "
        f"{YELLOW}-w{RESET}"
    )

    def parse_range(param):
        """Optimized range parsing"""
        if '-' in param:
            a, b = param.split('-', 1)
            return int(a)-1, int(b)
        idx = int(param)-1
        return idx, idx+1

    def validate_line_index(idx):
        """Validate line index bounds"""
        return 0 <= idx < len(lines)

    def validate_range(start, end):
        """Validate range bounds"""
        return 0 <= start < end <= len(lines)

    insert_mode = False
    replace_mode = False
    replace_range = (0, 0)
    replace_cursor = 0

    # Add timeout protection (Windows-compatible)
    import time
    start_time = time.time()
    max_session_time = 300  # 5 minutes max session time
    
    try:
        while True:
            # Check for timeout
            if time.time() - start_time > max_session_time:
                print(f"{YELLOW}[ WARN ] Edit session timed out{RESET}")
                break
            
            # multi-line insert
            if insert_mode:
                user = input(f"{YELLOW}{len(lines)+1}:{RESET} ").rstrip('\n')
                if user in ("-ii", "/edit -ii"):
                    insert_mode = False
                else:
                    lines.append(user)
                continue

            # multi-line replace
            if replace_mode:
                start, end = replace_range
                idx = start + replace_cursor
                user = input(f"{YELLOW}{idx+1}:{RESET} ").rstrip('\n')
                if user in ("-rr", "/edit -rr"):
                    replace_mode = False
                else:
                    if replace_cursor < (end - start):
                        lines[idx] = user
                    else:
                        lines.insert(idx, user)
                    replace_cursor += 1
                continue

            cmd = input(f"{GREEN}EDIT> {RESET}").rstrip('\n')
            parts = cmd.split()
            if not parts or parts[0] != "/edit":
                print(f"{RED}[ ERR ] Unknown Edit Command{RESET}")
                continue

            flags = [p for p in parts[1:] if p.startswith('-')]
            if len(flags) != 1:
                print(f"{RED}[ ERR ] Invalid flag{RESET}")
                continue
            flag = flags[0]

            if flag == "-w":
                # Optimized file writing
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    break
                except (OSError, IOError) as e:
                    print(f"{RED}[ ERR ] Failed to write file: {e}{RESET}")
                    continue

            # view single line
            if flag == "-v":
                if len(parts) < 3:
                    print(f"{RED}[ ERR ] Missing line number{RESET}")
                    continue
                start, _ = parse_range(parts[2])
                if not validate_line_index(start):
                    print(f"{RED}[ ERR ] Invalid line{RESET}")
                else:
                    print(f"{start+1}: {lines[start]}")
                continue

            # view range
            if flag == "-vv":
                if len(parts) < 3:
                    print(f"{RED}[ ERR ] Missing range{RESET}")
                    continue
                start, end = parse_range(parts[2])
                if not validate_range(start, end):
                    print(f"{RED}[ ERR ] Invalid range{RESET}")
                else:
                    # Use join for more efficient output
                    output_lines = [f"{i+1}: {lines[i]}" for i in range(start, end)]
                    print('\n'.join(output_lines))
                continue

            # paged view
            if flag == "-vvv":
                count = 0
                for i, l in enumerate(lines, 1):
                    print(f"{i}: {l}")
                    count += 1
                    if count >= 20:
                        count = 0
                        key = input(f"{YELLOW}(press 'v' to continue){RESET}")
                        if key != 'v':
                            break
                continue

            # full view
            if flag == "-vvvv":
                # Use join for more efficient output
                output_lines = [f"{i}: {l}" for i, l in enumerate(lines, 1)]
                print('\n'.join(output_lines))
                continue

            # flags that need a parameter
            needs_param = {"-i", "-d", "-dd", "-r", "-rr"}
            if flag in needs_param:
                if len(parts) < 3:
                    print(f"{RED}[ ERR ] Missing parameter{RESET}")
                    continue
                param = parts[2]

            # delete single line
            if flag == "-d":
                start, _ = parse_range(param)
                if not validate_line_index(start):
                    print(f"{RED}[ ERR ] Invalid line{RESET}")
                else:
                    del lines[start]
                continue

            # delete a block
            if flag == "-dd":
                start, end = parse_range(param)
                if not validate_range(start, end):
                    print(f"{RED}[ ERR ] Invalid range{RESET}")
                else:
                    del lines[start:end]
                continue

            # insert single-line (append only)
            if flag == "-i":
                start, _ = parse_range(param)
                if start != len(lines):
                    print(f"{RED}[ ERR ] Cannot insert there{RESET}")
                else:
                    text = input(f"{YELLOW}{start+1}:{RESET} ")
                    lines.insert(start, text)
                continue

            # enter multi-line insert
            if flag == "-ii":
                insert_mode = True
                continue

            # replace single line
            if flag == "-r":
                start, _ = parse_range(param)
                if not validate_line_index(start):
                    print(f"{RED}[ ERR ] Invalid line{RESET}")
                else:
                    new = input(f"{YELLOW}{start+1}:{RESET} ")
                    lines[start] = new
                continue

            # enter multi-line replace
            if flag == "-rr":
                start, end = parse_range(param)
                if not validate_range(start, end):
                    print(f"{RED}[ ERR ] Invalid range{RESET}")
                else:
                    del lines[start:end]
                    replace_mode = True
                    replace_range = (start, end)
                    replace_cursor = 0
                continue

            print(f"{RED}[ ERR ] Something went wrong{RESET}")
    
    except KeyboardInterrupt:
        print(f"{YELLOW}[ INFO ] Edit session interrupted{RESET}")
    except Exception as e:
        print(f"{RED}[ ERR ] Edit session error: {e}{RESET}")
