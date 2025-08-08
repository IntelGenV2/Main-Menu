#!/usr/bin/env python3
"""
QTOS v0.0.5.0 - BASIC Interpreter Integration
"""
import sys
import os
from pathlib import Path
from helpers import GREEN, RED, YELLOW, LIGHT_GREEN, RESET, loading

# Add BASIC directory to path
BASIC_DIR = Path(__file__).parent.parent / "BASIC"
sys.path.insert(0, str(BASIC_DIR))

try:
    from interpreter import main as basic_main
    BASIC_AVAILABLE = True
except ImportError as e:
    BASIC_AVAILABLE = False
    print(f"{RED}[ WARN ] BASIC interpreter not available: {e}{RESET}")

def basic_interpreter():
    """Optimized BASIC interpreter integration"""
    if not BASIC_AVAILABLE:
        print(f"{RED}[ ERR ] BASIC Interpreter module not found.{RESET}")
        print(f"{YELLOW}[ INFO ] Ensure all BASIC files are present in the BASIC directory.{RESET}")
        return
    
    print(f"{LIGHT_GREEN}QTOS BASIC Interpreter v1.0{RESET}")
    print(f"{YELLOW}Type 'EXIT' to return to QTOS{RESET}")
    print(f"{YELLOW}Type 'HELP' for BASIC commands{RESET}")
    print()
    
    try:
        # Run the BASIC interpreter
        basic_main()
        print(f"{LIGHT_GREEN}Returning to QTOS...{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user{RESET}")
    except Exception as e:
        print(f"{RED}[ ERR ] BASIC interpreter error: {e}{RESET}")

def check_basic_availability():
    """Check if BASIC interpreter is available"""
    required_files = [
        'interpreter.py',
        'program.py', 
        'lexer.py',
        'flowsignal.py',
        'basictoken.py',
        'basicparser.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not (BASIC_DIR / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"{RED}[ WARN ] Missing BASIC files: {', '.join(missing_files)}{RESET}")
        return False
    
    return True

if __name__ == '__main__':
    # Test the BASIC interpreter
    if check_basic_availability():
        basic_interpreter()
    else:
        print(f"{RED}[ ERR ] BASIC interpreter not properly configured{RESET}") 