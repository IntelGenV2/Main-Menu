#!/usr/bin/env python3
import os
import re
from functools import lru_cache
from pathlib import Path
from helpers import urn_to_dir, list_fs, list_wfe, sanitize_name, YELLOW, LIGHT_GREEN, RESET, RED

GENERIC_ERR = f"{RED}[ ERR ] Unknown Locator Command{RESET}"

# Cache for compiled regex patterns
_regex_cache = {}

@lru_cache(maxsize=64)
def _compile_regex(pattern: str, flags=re.IGNORECASE):
    """Cache compiled regex patterns for better performance"""
    return re.compile(pattern, flags)

def _search_entries(entries, pattern):
    """Optimized search with cached regex"""
    if pattern not in _regex_cache:
        _regex_cache[pattern] = _compile_regex(pattern)
    
    regex = _regex_cache[pattern]
    return [e for e in entries if regex.search(e)]

def handle_loc(cmd: str, base: str, fs_mode: bool, fs_root: str = None):
    """Optimized location handler with improved performance"""
    out = []
    new_loc = None
    low = cmd.lower()

    # Display
    if low == '/loc -d':
        out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Displaying: \"{base}\"{RESET}")
        real = urn_to_dir(base, fs_root) if fs_mode else base
        try:
            entries = list_fs(real) if fs_mode else list_wfe(real)
        except Exception:
            return [GENERIC_ERR], None
        
        # Use join for more efficient string concatenation
        out.extend(f"  • {e}" for e in entries)
        return out, None

    # Search (enhanced to search OS with full paths)
    if low.startswith('/loc -s '):
        pat = cmd.split('/loc -s', 1)[1].strip()
        out.append(f"{YELLOW}[ SEARCH ]{RESET} {LIGHT_GREEN}→ Searching OS for \"{pat}\"{RESET}")
        
        if fs_mode:
            # Search the entire QTOS file system with full paths
            location_matches = {}
            try:
                for root, dirs, files in os.walk(fs_root):
                    # Skip .venv directory
                    if '.venv' in dirs:
                        dirs.remove('.venv')
                    
                    # Search directories
                    for dir_name in dirs:
                        if _compile_regex(pat, re.IGNORECASE).search(dir_name):
                            rel_path = os.path.relpath(root, fs_root)
                            urn_path = rel_path.replace(os.sep, ':') if rel_path != '.' else 'base'
                            if urn_path not in location_matches:
                                location_matches[urn_path] = []
                            location_matches[urn_path].append(f"{dir_name} (chunk)")
                    
                    # Search files (exclude .pyc files)
                    for file_name in files:
                        if not file_name.endswith('.pyc') and _compile_regex(pat, re.IGNORECASE).search(file_name):
                            rel_path = os.path.relpath(root, fs_root)
                            urn_path = rel_path.replace(os.sep, ':') if rel_path != '.' else 'base'
                            if urn_path not in location_matches:
                                location_matches[urn_path] = []
                            # Display file name with asterisk instead of dot
                            display_name = file_name.replace('.', '*')
                            location_matches[urn_path].append(f"{display_name} (block)")
            except OSError:
                pass
            
            # Display results organized by location
            for location in sorted(location_matches.keys()):
                out.append(f"  {location}:")
                for match in sorted(location_matches[location]):
                    out.append(f"    • {match}")
        else:
            # For WFE mode, search all drives with full paths
            location_matches = {}
            try:
                for drive in range(ord('A'), ord('Z') + 1):
                    drive_letter = chr(drive) + ":\\"
                    if os.path.exists(drive_letter):
                        for root, dirs, files in os.walk(drive_letter):
                            # Skip .venv directory
                            if '.venv' in dirs:
                                dirs.remove('.venv')
                            
                            # Search directories
                            for dir_name in dirs:
                                if _compile_regex(pat, re.IGNORECASE).search(dir_name):
                                    if root not in location_matches:
                                        location_matches[root] = []
                                    location_matches[root].append(f"{dir_name} (chunk)")
                            
                            # Search files (exclude .pyc files)
                            for file_name in files:
                                if not file_name.endswith('.pyc') and _compile_regex(pat, re.IGNORECASE).search(file_name):
                                    if root not in location_matches:
                                        location_matches[root] = []
                                    # Display file name with asterisk instead of dot
                                    display_name = file_name.replace('.', '*')
                                    location_matches[root].append(f"{display_name} (block)")
            except OSError:
                pass
            
            # Display results organized by location
            for location in sorted(location_matches.keys()):
                out.append(f"  {location}:")
                for match in sorted(location_matches[location]):
                    out.append(f"    • {match}")
        
        return out, None

    # Peek
    if low.startswith('/loc -p '):
        urn = cmd.split('/loc -p', 1)[1].strip()
        real = urn_to_dir(urn, fs_root) if fs_mode else urn.replace(':', os.sep)
        
        if os.path.isdir(real):
            out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Peeking at: \"{urn}\"{RESET}")
            entries = list_fs(real) if fs_mode else list_wfe(real)
            out.extend(f"  • {e}" for e in entries)
        else:
            out.append(GENERIC_ERR)
        return out, None

    # Enter
    if low.startswith('/loc -e '):
        target = cmd.split('/loc -e', 1)[1].strip()
        real_base = urn_to_dir(base, fs_root) if fs_mode else base

        if target.lower() == 'base':
            out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Returned to base{RESET}")
            return out, 'base' if fs_mode else None

        # Full URN
        if ':' in target:
            real_target = urn_to_dir(target, fs_root) if fs_mode else target.replace(':', os.sep)
            if os.path.isdir(real_target):
                out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Entered: \"{target}\"{RESET}")
                return out, target if fs_mode else real_target
            else:
                out.append(GENERIC_ERR)
                return out, None

        # Direct child - use pathlib for more efficient path operations
        child_path = Path(real_base) / target
        if child_path.is_dir():
            if fs_mode:
                new_urn = f"{base}:{target}" if base != 'base' else f'base:{target}'
                out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Entered: \"{new_urn}\"{RESET}")
                return out, new_urn
            else:
                out.append(f"{YELLOW}[ LOC ]{RESET} {LIGHT_GREEN}→ Entered: \"{child_path}\"{RESET}")
                return out, str(child_path)

        out.append(GENERIC_ERR)
        return out, None

    out.append(GENERIC_ERR)
    return out, None

def clear_regex_cache():
    """Clear the regex pattern cache"""
    global _regex_cache
    _regex_cache.clear()
