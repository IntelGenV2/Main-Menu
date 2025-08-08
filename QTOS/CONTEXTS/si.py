#!/usr/bin/env python3
"""
QTOS v0.0.5.0 - Quantified Ternary OS (SI context)
"""
import os
import time
import random
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from helpers import YELLOW, LIGHT_GREEN, RESET, RED

# Import crash timer functions if available
try:
    from crash_timer import enable_crashes, disable_crashes, get_crash_status
    CRASH_TIMER_AVAILABLE = True
except ImportError:
    CRASH_TIMER_AVAILABLE = False
    def enable_crashes():
        return "Crash timer not available"
    def disable_crashes():
        return "Crash timer not available"
    def get_crash_status():
        return False

# — Ternary System Constants —
TRITS_PER_TRYTE = 6  # 6 trits = 1 tryte (3^6 = 729 possible values)
TRITS_PER_KILOTRYTE = 6000  # 1000 trytes * 6 trits per tryte

# — Storage Limits in Trytes (Base-3 Logic) —
# Using powers of 3 for proper ternary system scaling
MAX_TRYTES = 3 ** 16  # 43,046,721 trytes maximum (3¹⁶ limit)
RAM_CAPACITY_TRYTES = 3 ** 10  # 59,049 trytes for RAM (3¹⁰) - enough for exactly 3 contexts
DISK_CAPACITY_TRYTES = 3 ** 16  # 43,046,721 trytes for disk (3¹⁶)

# — Convert to bytes using proper conversion —
# 1 tryte ≈ 0.59 bytes (based on information theory)
# 1 kilotryte = 1000 trytes ≈ 594.36 bytes
BYTES_PER_TRYTE = 0.59436
RAM_CAPACITY_BYTES = int(RAM_CAPACITY_TRYTES * BYTES_PER_TRYTE)
DISK_CAPACITY_BYTES = int(DISK_CAPACITY_TRYTES * BYTES_PER_TRYTE)

# Map context names to their module filenames
MODULE_FILES = {
    'CORE': 'core.py',
    'FS':   'fs.py',
    'WFE':  'wfe.py',
    'SG':   'sg.py',
    'SI':   'si.py',
    'BP':   'bp.py'
}

# Tracks which modules are "resident" in memory
_ACCESSED_MODULES = set()

# Cache for disk usage calculations
_disk_cache = {}
_disk_cache_timeout = 10.0  # seconds

def record_access(context_name: str):
    """Call this from core.py when entering a context."""
    fname = MODULE_FILES.get(context_name)
    if fname:
        _ACCESSED_MODULES.add(fname)

def record_release(context_name: str):
    """Call this from core.py when leaving a context."""
    # Contexts now stay in RAM until explicitly cleared
    # This function is kept for compatibility but does nothing
    pass

def clear_ram():
    """Clear all loaded contexts from RAM except CORE"""
    global _ACCESSED_MODULES
    # Keep only CORE in memory
    _ACCESSED_MODULES = {'core.py'} if 'core.py' in _ACCESSED_MODULES else set()
    return len(_ACCESSED_MODULES)

def get_loaded_contexts():
    """Get list of currently loaded contexts"""
    loaded = []
    for context_name, filename in MODULE_FILES.items():
        if filename in _ACCESSED_MODULES:
            loaded.append(context_name)
    return loaded

def get_current_ram_usage_bytes() -> int:
    """Sum the on-disk sizes of all currently-loaded modules with optimized file operations."""
    total = 0
    base = Path(__file__).parent
    
    for fname in _ACCESSED_MODULES:
        path = base / fname
        try:
            if path.exists():
                total += path.stat().st_size
        except OSError:
            pass
    return total

def bytes_to_trytes(bytes_amt: int) -> int:
    """Convert bytes to trytes using proper conversion ratio"""
    return int(bytes_amt / BYTES_PER_TRYTE)

def trytes_to_bytes(trytes_amt: int) -> int:
    """Convert trytes to bytes using proper conversion ratio"""
    return int(trytes_amt * BYTES_PER_TRYTE)

def get_storage_info() -> dict:
    """Get comprehensive storage information in base-3 units"""
    return {
        'max_trytes': MAX_TRYTES,
        'max_trytes_base3': to_trits(MAX_TRYTES),
        'ram_capacity_trytes': RAM_CAPACITY_TRYTES,
        'ram_capacity_base3': to_trits(RAM_CAPACITY_TRYTES),
        'disk_capacity_trytes': DISK_CAPACITY_TRYTES,
        'disk_capacity_base3': to_trits(DISK_CAPACITY_TRYTES),
        'ram_capacity_bytes': RAM_CAPACITY_BYTES,
        'disk_capacity_bytes': DISK_CAPACITY_BYTES,
        'ram_capacity_mb': RAM_CAPACITY_BYTES / (1024 * 1024),
        'disk_capacity_mb': DISK_CAPACITY_BYTES / (1024 * 1024)
    }

@lru_cache(maxsize=64)
def to_trits(n: int, width: int = 12) -> str:
    """Convert integer n to fixed-width base-3 string, padded + subscript with caching."""
    if n > MAX_TRYTES:
        return "OVERFLOW₃"
    
    # Convert to base-3
    if n == 0:
        return "0₃"
    
    digits = []
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    
    # Reverse and pad
    result = ''.join(reversed(digits))
    result = result.zfill(width)
    return f"{result}₃"

def _format_size(bytes_amt: int):
    """Format bytes into trytes with appropriate units"""
    if bytes_amt == 0:
        return "0₃", "Ty"
    
    trytes = bytes_to_trytes(bytes_amt)
    
    if trytes < 1000:
        return f"{trytes}₃", "Ty"
    elif trytes < 1000000:
        return f"{trytes//1000}₃", "KTy"
    else:
        return f"{trytes//1000000}₃", "MTy"

def _get_disk_usage_cached(fs_root: str) -> int:
    """Get disk usage with caching for performance"""
    current_time = time.time()
    
    # Check if we have a valid cached result
    if fs_root in _disk_cache:
        cached_time, cached_size = _disk_cache[fs_root]
        if current_time - cached_time < _disk_cache_timeout:
            return cached_size
    
    # Calculate fresh disk usage
    total_size = 0
    try:
        qtos_path = Path(fs_root)
        if qtos_path.exists():
            for file_path in qtos_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
    except OSError:
        pass
    
    # Cache the result
    _disk_cache[fs_root] = (current_time, total_size)
    return total_size

def _check_storage_limit(used_bytes: int, capacity_bytes: int, storage_type: str) -> bool:
    """Check if storage usage is within limits"""
    if used_bytes > capacity_bytes:
        print(f"{RED}[ WARN ] {storage_type} usage {used_bytes} B exceeds capacity {capacity_bytes} B{RESET}")
        return False
    return True

def handle_info(cmd: str, start_time: float, fs_root: str):
    """Optimized info handler with improved performance"""
    parts = cmd.strip().split()
    if len(parts) != 2 or not parts[1].startswith('-'):
        return [f"{RED}[ ERR ] Unknown System Information Command{RESET}"]

    flag = parts[1].lower()
    out = []

    if flag == '-o':
        out.append(f"{YELLOW}[ OS  ]{RESET} {LIGHT_GREEN}→ Quantified Ternary OS v0.0.5.0{RESET}")
        out.append(f"              {LIGHT_GREEN}(Quantified Technologies){RESET}")

    elif flag == '-c':
        out.append(f"{YELLOW}[ CPU ]{RESET} {LIGHT_GREEN}→ QT 4T - 4th Generation Ternary CPU{RESET}")
        out.append(f"              {LIGHT_GREEN}@ 2 MHz, Base-3 Architecture{RESET}")

    elif flag == '-r':
        used_bytes = get_current_ram_usage_bytes()
        loaded_contexts = get_loaded_contexts()
        if _check_storage_limit(used_bytes, RAM_CAPACITY_BYTES, "RAM"):
            used_trits, used_unit = _format_size(used_bytes)
            cap_trits, cap_unit = _format_size(RAM_CAPACITY_BYTES)
            out.append(f"{YELLOW}[ RAM ]{RESET} {LIGHT_GREEN}→ {used_trits} {used_unit} / {cap_trits} {cap_unit}{RESET}")
            out.append(f"{YELLOW}[ LOADED ]{RESET} {LIGHT_GREEN}→ {len(loaded_contexts)} contexts: {', '.join(loaded_contexts)}{RESET}")

    elif flag == '-d':
        # Calculate actual QTOS folder size
        qtos_folder = Path(__file__).parent.parent
        total = 0
        try:
            for file_path in qtos_folder.rglob('*'):
                if file_path.is_file():
                    total += file_path.stat().st_size
        except OSError:
            pass
        
        if _check_storage_limit(total, DISK_CAPACITY_BYTES, "Disk"):
            used_trits, used_unit = _format_size(total)
            cap_trits, cap_unit = _format_size(DISK_CAPACITY_BYTES)
            out.append(f"{YELLOW}[ DISK]{RESET} {LIGHT_GREEN}→ {used_trits} {used_unit} / {cap_trits} {cap_unit}{RESET}")

    elif flag == '-u':
        uptime = time.time() - start_time
        days, rem = divmod(uptime, 86400)
        hrs, rem  = divmod(rem,    3600)
        mins, secs= divmod(rem,     60)
        out.append(f"{YELLOW}[ UPT ]{RESET} {LIGHT_GREEN}→ {int(days)}d {int(hrs)}h {int(mins)}m {int(secs)}s{RESET}")

    elif flag == '-t':
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        out.append(f"{YELLOW}[ TIME]{RESET} {LIGHT_GREEN}→ {now}{RESET}")

    else:
        out.append(f"{RED}[ ERR ] Unknown System Information flag{RESET}")

    return out

def handle_memory():
    """Handle memory management command"""
    try:
        from performance import force_cleanup, clear_performance_data
        memory_mb = get_current_ram_usage_bytes() / (1024 * 1024)
        print(f"{LIGHT_GREEN}[ INFO ] Current memory: {memory_mb:.1f} MB{RESET}")
        force_cleanup()
        print(f"{LIGHT_GREEN}[ INFO ] Memory cleanup completed{RESET}")
    except ImportError:
        print(f"{RED}[ ERR ] Performance module not available{RESET}")

def handle_clear():
    """Handle clear performance data command"""
    try:
        from performance import clear_performance_data
        clear_performance_data()
        print(f"{LIGHT_GREEN}[ INFO ] Performance data cleared{RESET}")
    except ImportError:
        print(f"{RED}[ ERR ] Performance module not available{RESET}")

def handle_startup():
    """Handle startup effects command"""
    try:
        from startup_effects import show_startup_menu
        show_startup_menu()
    except ImportError:
        print(f"{RED}[ ERR ] Startup effects module not available{RESET}")

def handle_startup_effect(effect: str):
    """Handle startup effect change command"""
    try:
        from startup_effects import STARTUP_EFFECTS
        if effect in STARTUP_EFFECTS:
            print(f"{LIGHT_GREEN}[ INFO ] Startup effect changed to: {effect}{RESET}")
            # You could save this to a config file here
        else:
            print(f"{RED}[ ERR ] Unknown startup effect: {effect}{RESET}")
            print(f"{YELLOW}[ INFO ] Use 'startup' to see available effects{RESET}")
    except ImportError:
        print(f"{RED}[ ERR ] Startup effects module not available{RESET}")

def handle_set(cmd: str):
    """Handle /set commands for system settings"""
    parts = cmd.strip().split()
    if len(parts) < 2 or not parts[1].startswith('-'):
        return [f"{RED}[ ERR ] Unknown Set Command{RESET}"]
    
    flag = parts[1].lower()
    lines = []

    if flag == '-c':
        # Clear performance data and memory usage
        try:
            from performance import clear_performance_data
            clear_performance_data()
            lines.append(f"{LIGHT_GREEN}[ INFO ] → Performance data cleared...{RESET}")
            
            memory_mb = get_current_ram_usage_bytes() / (1024 * 1024)
            lines.append(f"{LIGHT_GREEN}[ INFO ] → Current memory: {memory_mb:.1f} MB{RESET}")
            
            from performance import force_cleanup
            force_cleanup()
            lines.append(f"{LIGHT_GREEN}[ INFO ] → Memory cleanup completed{RESET}")
        except ImportError:
            lines.append(f"{RED}[ ERR ] Performance module not available{RESET}")

    elif flag == '-r':
        # Clear RAM - remove all contexts except CORE
        loaded_count = clear_ram()
        lines.append(f"{LIGHT_GREEN}[ INFO ] → RAM cleared - {loaded_count} context(s) remaining{RESET}")
        lines.append(f"{LIGHT_GREEN}[ INFO ] → All contexts unloaded except CORE{RESET}")
        
    elif flag == '-s':
        if len(parts) >= 3:
            # Change startup effect
            effect = parts[2].lower()
            try:
                from startup_effects import STARTUP_EFFECTS
                if effect in STARTUP_EFFECTS:
                    lines.append(f"{LIGHT_GREEN}[ INFO ] → Startup effect changed to: {effect}{RESET}")
                    # You could save this to a config file here
                else:
                    lines.append(f"{RED}[ ERR ] Unknown startup effect: {effect}{RESET}")
                    lines.append(f"{YELLOW}[ INFO ] Use '/set -s' to see available effects{RESET}")
            except ImportError:
                lines.append(f"{RED}[ ERR ] Startup effects module not available{RESET}")
        else:
            # Show available startup effects
            try:
                from startup_effects import STARTUP_EFFECTS
                lines.append(f"{LIGHT_GREEN}[ INFO ] → Available effects: {', '.join(STARTUP_EFFECTS)}{RESET}")
            except ImportError:
                lines.append(f"{RED}[ ERR ] Startup effects module not available{RESET}")

    else:
        lines.append(f"{RED}[ ERR ] Unknown Set flag{RESET}")

    return lines

# — /test handler ————————————————————————————————————————————————————————
def handle_test(cmd: str):
    """Optimized test handler"""
    parts = cmd.strip().split()
    if len(parts) != 2 or not parts[1].startswith('-'):
        return [f"{RED}[ ERR ] Unknown Test Command{RESET}"]
    
    flag = parts[1].lower()
    lines = []

    if flag == '-r':
        # RAM test with grid visualization and error detection
        lines.append(f"{YELLOW}[ RAM ]{RESET} {LIGHT_GREEN}→ Testing memory modules...{RESET}")
        
        # Create a 4x8 grid representing RAM modules
        grid_width = 8
        grid_height = 4
        total_modules = grid_width * grid_height
        
        # Generate some random errors (about 5-15% of modules)
        error_count = random.randint(1, max(1, total_modules // 10))
        error_positions = set()
        for _ in range(error_count):
            row = random.randint(0, grid_height - 1)
            col = random.randint(0, grid_width - 1)
            error_positions.add((row, col))
        
        # Display RAM grid
        lines.append(f"{YELLOW}[ GRID]{RESET} {LIGHT_GREEN}→ Memory Module Status:{RESET}")
        for row in range(grid_height):
            grid_line = "    "
            for col in range(grid_width):
                if (row, col) in error_positions:
                    grid_line += f"{RED}[X]{RESET} "  # Error module
                else:
                    grid_line += f"{LIGHT_GREEN}[O]{RESET} "  # Good module
            lines.append(grid_line)
        
        # Show statistics
        good_modules = total_modules - error_count
        error_percentage = (error_count / total_modules) * 100
        lines.append(f"{YELLOW}[ STAT]{RESET} {LIGHT_GREEN}→ Good: {good_modules}/{total_modules} modules{RESET}")
        
        if error_count > 0:
            lines.append(f"{YELLOW}[ ERR ]{RESET} {RED}→ {error_count} faulty modules detected ({error_percentage:.1f}%){RESET}")
            lines.append(f"{YELLOW}[ WARN]{RESET} {RED}→ Memory errors detected - system stability may be affected{RESET}")
        else:
            lines.append(f"{YELLOW}[ OK  ]{RESET} {LIGHT_GREEN}→ All memory modules passed{RESET}")

    elif flag == '-c':
        # CPU test with core-by-core analysis
        lines.append(f"{YELLOW}[ CPU ]{RESET} {LIGHT_GREEN}→ Testing CPU cores @ 2MHz...{RESET}")
        
        # Test each core individually
        num_cores = 4  # QT 4T CPU has 4 cores
        total_performance = 0
        
        for core in range(1, num_cores + 1):
            # Simulate core testing with realistic delays
            core_performance = random.randint(85, 100)
            total_performance += core_performance
            
            if core_performance >= 95:
                status = f"{LIGHT_GREEN}EXCELLENT{RESET}"
            elif core_performance >= 90:
                status = f"{YELLOW}GOOD{RESET}"
            elif core_performance >= 80:
                status = f"{YELLOW}FAIR{RESET}"
            else:
                status = f"{RED}POOR{RESET}"
            
            lines.append(f"{YELLOW}[ CORE]{RESET} {LIGHT_GREEN}→ Core {core}: {core_performance}% ({status}){RESET}")
        
        # Overall CPU performance
        avg_performance = total_performance // num_cores
        lines.append(f"{YELLOW}[ AVG ]{RESET} {LIGHT_GREEN}→ Average Performance: {avg_performance}%{RESET}")
        
        if avg_performance >= 90:
            lines.append(f"{YELLOW}[ OK  ]{RESET} {LIGHT_GREEN}→ CPU test passed - all cores operational{RESET}")
        else:
            lines.append(f"{YELLOW}[ WARN]{RESET} {RED}→ CPU performance below optimal - consider maintenance{RESET}")

    elif flag == '-a':
        lines.append(f"{YELLOW}[ TEST]{RESET} {LIGHT_GREEN}→ Running full system diagnostics...{RESET}")
        lines.append(f"{YELLOW}[ CPU ]{RESET} {LIGHT_GREEN} Test Passed: {random.randint(90,100)}%{RESET}")
        lines += handle_test('/test -r')
        lines.append(f"{YELLOW}[ DISK]{RESET} {LIGHT_GREEN} Test Passed: Read/Write OK{RESET}")
        lines.append(f"{YELLOW}[ ALL ]{RESET} {LIGHT_GREEN}→ System Test Complete{RESET}")

    else:
        lines.append(f"{RED}[ ERR ] Unknown Test flag{RESET}")

    return lines

def handle_crash(cmd: str):
    """Handle /crash commands for crash timer control"""
    parts = cmd.strip().split()
    if len(parts) < 2:
        # Show status when no flag provided
        status = "enabled" if get_crash_status() else "disabled"
        return [f"{YELLOW}[ CRASH ]{RESET} {LIGHT_GREEN}→ Crash timer is currently {status}{RESET}"]
    
    if not parts[1].startswith('-'):
        return [f"{RED}[ ERR ] Unknown Crash Command{RESET}"]
    
    flag = parts[1].lower()
    lines = []

    if flag == '-f':
        # Disable crashes
        result = disable_crashes()
        lines.append(f"{YELLOW}[ CRASH ]{RESET} {LIGHT_GREEN}→ {result}{RESET}")
    elif flag == '-n':
        # Enable crashes
        result = enable_crashes()
        lines.append(f"{YELLOW}[ CRASH ]{RESET} {LIGHT_GREEN}→ {result}{RESET}")
    else:
        lines.append(f"{RED}[ ERR ] Unknown crash flag. Use -f to disable, -n to enable{RESET}")

    return lines

def clear_caches():
    """Clear all caches for debugging"""
    global _disk_cache
    _disk_cache.clear()
    to_trits.cache_clear()

def get_cache_stats():
    """Get cache statistics for debugging"""
    return {
        'disk_cache_entries': len(_disk_cache),
        'disk_cache_timeout': _disk_cache_timeout,
        'trits_cache_info': to_trits.cache_info()
    }
