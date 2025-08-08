#!/usr/bin/env python3
"""
Modification handler for QBOS

Commands:
  mod -c /name=<entry> /loc=<URN> /type=<type>  — chunk (folder) or Block (file)
  mod -e /name=<file> /loc=<URN>                — edit an existing file
  mod -d /name=<entry> /loc=<URN>               — delete file or folder
  mod -r /name=<old> /loc=<URN> /name2=<new>    — rename
  mod -y (copy) /name=<src> /loc=<URN> /loc2=<URN>
  mod -m (move) /name=<src> /loc=<URN> /loc2=<URN>
"""
import os
import shutil
from pathlib import Path
from helpers import urn_to_dir, sanitize_name, YELLOW, LIGHT_GREEN, RESET, RED, clear_cache
import edit_handler

GENERIC_ERR = f"{RED}[ ERR ] → Modification error{RESET}"

def _parse_params(parts):
    """Optimized parameter parsing"""
    params = {}
    for p in parts[2:]:
        if p.startswith('/') and '=' in p:
            key, val = p[1:].split('=', 1)
            params[key.lower()] = val
    return params

def _resolve_target(loc, base_urn, base_path, fs_mode, fs_root):
    """Optimized target resolution"""
    if fs_mode:
        target = urn_to_dir(loc if loc.lower() != 'eloc' else base_urn, fs_root)
        display = loc if loc.lower() != 'eloc' else base_urn
    else:
        target = loc.replace(':', os.sep) if loc.lower() != 'eloc' else base_path
        display = target
    return target, display

def handle_mod(cmd: str, *, base_urn=None, base_path=None, fs_root=None, fs_mode: bool):
    """Optimized modification handler with improved performance"""
    parts = cmd.split()
    if len(parts) < 2:
        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
    
    op = parts[1].lower()
    params = _parse_params(parts)

    name = params.get('name')
    loc = params.get('loc')
    if not name or not loc:
        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"

    # Resolve target directory
    target, display = _resolve_target(loc, base_urn, base_path, fs_mode, fs_root)
    
    fs_name = sanitize_name(name)
    path = Path(target) / fs_name

    def _get_item_kind(p: Path) -> str:
        return "chunk" if p.is_dir() else "block"

    def _available_name(directory: Path, base_name: str) -> str:
        """Return a name that does not collide in directory by appending -N before extension when needed."""
        candidate = base_name
        stem = Path(base_name).stem
        suffix = Path(base_name).suffix
        index = 1
        while (directory / candidate).exists():
            if suffix:
                candidate = f"{stem}-{index}{suffix}"
            else:
                candidate = f"{stem}-{index}"
            index += 1
        return candidate

    try:
        if op == '-e':
            # edit existing file
            if not path.exists():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            if not path.is_file():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            edit_handler.edit_file(str(path), display)
            # Clear cache after editing files
            clear_cache()
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Finished editing \"{name}\"{RESET}"

        if op == '-c':
            typ_raw = params.get('type')
            if not typ_raw:
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            typ = typ_raw.lower()
            if typ not in ['chunk', 'block']:
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            
            if path.exists():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            
            if typ == 'chunk':
                path.mkdir(parents=True, exist_ok=True)
            elif typ == 'block':
                path.touch()
            # Clear cache after creating files/directories
            clear_cache()
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Created \"{name}\" in {display}{RESET}"

        if op == '-d':
            if not path.exists():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
            # Clear cache after deleting files/directories
            clear_cache()
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Deleted \"{name}\" from {display}{RESET}"

        if op == '-r':
            new = params.get('name2')
            if not new:
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            if not path.exists():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            
            dst = path.parent / sanitize_name(new)
            if dst.exists():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            
            path.rename(dst)
            # Clear cache after renaming files/directories
            clear_cache()
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ Renamed \"{name}\" to \"{new}\" in {display}{RESET}"

        if op in ('-y', '-m'):
            dst = params.get('loc2') or params.get('name2')
            if not dst:
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            
            if not path.exists():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
            
            if fs_mode:
                dst_path = urn_to_dir(dst, fs_root)
                display_dst = dst
            else:
                dst_path = dst.replace(':', os.sep)
                display_dst = dst_path

            dst_path = Path(dst_path)
            # Destination must exist and be a directory (chunk)
            if not dst_path.exists() or not dst_path.is_dir():
                return f"{RED}[ ERR ] Unknown Modification Command{RESET}"

            # Perform copy/move with collision-safe naming
            if op == '-y':  # Copy
                if path.is_dir():
                    dest_name = _available_name(dst_path, fs_name)
                    final_dst = dst_path / dest_name
                    shutil.copytree(path, final_dst)
                    item_kind = "chunk"
                else:
                    dest_name = _available_name(dst_path, fs_name)
                    final_dst = dst_path / dest_name
                    shutil.copy2(path, final_dst)
                    item_kind = "block"
                verb = "Copied"
            else:  # Move
                if path.is_dir():
                    dest_name = _available_name(dst_path, fs_name)
                    final_dst = dst_path / dest_name
                    if final_dst.exists():
                        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
                    shutil.move(str(path), str(final_dst))
                    item_kind = "chunk"
                else:
                    dest_name = _available_name(dst_path, fs_name)
                    final_dst = dst_path / dest_name
                    if final_dst.exists():
                        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
                    shutil.move(str(path), str(final_dst))
                    item_kind = "block"
                verb = "Moved"

            # Clear cache after copy/move operations
            clear_cache()
            return f"{YELLOW}[ MOD ]{RESET} {LIGHT_GREEN}→ {verb} {item_kind} \"{name}\" from {display} to {display_dst}{RESET}"

        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"

    except PermissionError:
        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
    except FileNotFoundError:
        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
    except FileExistsError:
        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
    except OSError as e:
        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
    except Exception as e:
        return f"{RED}[ ERR ] Unknown Modification Command{RESET}"
