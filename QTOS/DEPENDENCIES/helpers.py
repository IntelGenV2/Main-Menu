#!/usr/bin/env python3
import os
import shutil
import time
import re
from functools import lru_cache
from pathlib import Path

# ANSI color codes - using constants for better performance
RESET       = "\033[0m"
GREEN       = "\033[32m"
LIGHT_GREEN = "\033[92m"
YELLOW      = "\033[33m"
RED         = "\033[31m"

# Cache for directory listings to avoid repeated os.listdir calls
_dir_cache = {}
_cache_timeout = 5.0  # seconds

def loading(msg, dots=3, delay=0.3):
    """Optimized loading animation with reduced string operations"""
    print(f"{YELLOW}{msg}{RESET}", end="", flush=True)
    dots_str = f"{YELLOW}.{RESET}" * dots
    for i in range(dots):
        time.sleep(delay)
        print(dots_str[i*len(f"{YELLOW}.{RESET}"):(i+1)*len(f"{YELLOW}.{RESET}")], end="", flush=True)
    print()

@lru_cache(maxsize=128)
def sanitize_name(name: str) -> str:
    """Cached name sanitization for better performance"""
    return name.replace('*', '.')

@lru_cache(maxsize=128)
def display_name(entry: str) -> str:
    """Cached display name conversion"""
    return entry.replace('.', '*')

def urn_to_dir(urn: str, fs_root: str) -> str:
    """Optimized URN to directory conversion"""
    if not urn or urn.lower() == 'base':
        return fs_root
    
    # Use pathlib for more efficient path operations
    if ':' in urn:
        parts = urn.split(':')
        if parts[0].lower() == 'base':
            parts = parts[1:]
        return str(Path(fs_root).joinpath(*parts))
    
    return fs_root

def _get_cached_listing(path: str, cache_key: str):
    """Get cached directory listing with timeout"""
    current_time = time.time()
    if cache_key in _dir_cache:
        cached_time, cached_result = _dir_cache[cache_key]
        if current_time - cached_time < _cache_timeout:
            return cached_result
    
    try:
        # Filter out .venv directories and .pyc files
        entries = []
        for e in os.listdir(path):
            # Skip .venv directories
            if e == '.venv':
                continue
            # Skip .pyc files
            if e.endswith('.pyc'):
                continue
            entries.append(display_name(e))
        
        result = sorted(entries)
        _dir_cache[cache_key] = (current_time, result)
        return result
    except OSError:
        return []

def list_fs(path: str):
    """Optimized file system listing with caching"""
    return _get_cached_listing(path, f"fs:{path}")

def list_wfe(path: str):
    """Optimized Windows file explorer listing with caching"""
    return _get_cached_listing(path, f"wfe:{path}")

def clear_cache():
    """Clear the directory listing cache"""
    global _dir_cache
    _dir_cache.clear()

def get_cache_stats():
    """Get cache statistics for debugging"""
    return {
        'entries': len(_dir_cache),
        'timeout': _cache_timeout
    }
