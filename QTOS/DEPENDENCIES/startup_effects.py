#!/usr/bin/env python3
"""
QTOS Startup Effects Collection
Various cool startup animations for the Quantified Ternary OS
"""
import time
import random
import sys
from helpers import LIGHT_GREEN, GREEN, RESET, YELLOW, RED

def matrix_style_startup():
    """Matrix-style scrolling startup with Japanese characters"""
    matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
    
    messages = [
        "INITIALIZING QUANTIFIED TERNARY OS...",
        "LOADING BASE-3 MEMORY SYSTEM...",
        "CALIBRATING TRYTE CONVERSION...",
        "ESTABLISHING TERNARY LOGIC GATES...",
        "SYNCHRONIZING TRIT PROCESSORS...",
        "VALIDATING STORAGE CAPACITY...",
        "INITIALIZING CONTEXT SWITCHER...",
        "LOADING MODULE INTERFACES...",
        "ESTABLISHING FILE SYSTEM...",
        "READY FOR TERNARY OPERATIONS..."
    ]
    
    print(f"{LIGHT_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
    
    for message in messages:
        matrix_line = "".join(random.choice(matrix_chars) for _ in range(20))
        print(f"{LIGHT_GREEN}║ {matrix_line} {message:<35} {matrix_line} ║{RESET}")
        time.sleep(0.3)
        print(f"{LIGHT_GREEN}║ {' ' * 20} {message:<35} {' ' * 20} ║{RESET}")
        time.sleep(0.2)
    
    print(f"{LIGHT_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    time.sleep(0.5)

def binary_rain_startup():
    """Binary rain effect with falling 1s and 0s"""
    print(f"{LIGHT_GREEN}┌──────────────────────────────────────────────────────────────┐{RESET}")
    
    for i in range(10):
        # Create falling binary effect
        binary_line = " ".join(random.choice("01") for _ in range(16))
        print(f"{LIGHT_GREEN}│ {binary_line:<50} │{RESET}")
        time.sleep(0.2)
        
        # Show progress
        progress = "█" * (i + 1) + "░" * (10 - i - 1)
        print(f"{LIGHT_GREEN}│ [ {progress} ] Loading... {i*10:2d}%{' ' * 30} │{RESET}")
        time.sleep(0.3)
    
    print(f"{LIGHT_GREEN}└──────────────────────────────────────────────────────────────┘{RESET}")
    time.sleep(0.5)

def scanline_startup():
    """Scanline effect like old CRT monitors"""
    print(f"{LIGHT_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
    
    scanlines = [
        "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
        "████████████████████████████████████████████████████████████████████████████",
        "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
        "████████████████████████████████████████████████████████████████████████████",
    ]
    
    for i in range(8):
        for line in scanlines:
            print(f"{LIGHT_GREEN}║ {line} ║{RESET}")
            time.sleep(0.1)
        
        # Show loading message
        messages = [
            "SCANNING MEMORY BANKS...",
            "INITIALIZING PROCESSORS...",
            "LOADING SYSTEM MODULES...",
            "ESTABLISHING CONNECTIONS...",
            "VALIDATING INTEGRITY...",
            "CALIBRATING CLOCKS...",
            "SYNCHRONIZING DATA...",
            "READY FOR OPERATION..."
        ]
        if i < len(messages):
            print(f"{LIGHT_GREEN}║ {messages[i]:<70} ║{RESET}")
            time.sleep(0.3)
    
    print(f"{LIGHT_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    time.sleep(0.5)

def glitch_startup():
    """Glitch effect with corrupted text that fixes itself"""
    print(f"{LIGHT_GREEN}┌──────────────────────────────────────────────────────────────┐{RESET}")
    
    messages = [
        "INITIALIZING QUANTIFIED TERNARY OS...",
        "LOADING BASE-3 MEMORY SYSTEM...",
        "CALIBRATING TRYTE CONVERSION...",
        "ESTABLISHING TERNARY LOGIC GATES...",
        "SYNCHRONIZING TRIT PROCESSORS...",
        "VALIDATING STORAGE CAPACITY...",
        "INITIALIZING CONTEXT SWITCHER...",
        "LOADING MODULE INTERFACES...",
        "ESTABLISHING FILE SYSTEM...",
        "READY FOR TERNARY OPERATIONS..."
    ]
    
    glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    for message in messages:
        # Show glitched version first
        glitched = ""
        for char in message:
            if random.random() < 0.3:
                glitched += random.choice(glitch_chars)
            else:
                glitched += char
        
        print(f"{RED}│ {glitched:<70} │{RESET}")
        time.sleep(0.2)
        
        # Show corrected version
        print(f"{LIGHT_GREEN}│ {message:<70} │{RESET}")
        time.sleep(0.3)
    
    print(f"{LIGHT_GREEN}└──────────────────────────────────────────────────────────────┘{RESET}")
    time.sleep(0.5)

def hologram_startup():
    """Hologram effect with fading text"""
    print(f"{LIGHT_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
    
    messages = [
        "INITIALIZING QUANTIFIED TERNARY OS...",
        "LOADING BASE-3 MEMORY SYSTEM...",
        "CALIBRATING TRYTE CONVERSION...",
        "ESTABLISHING TERNARY LOGIC GATES...",
        "SYNCHRONIZING TRIT PROCESSORS...",
        "VALIDATING STORAGE CAPACITY...",
        "INITIALIZING CONTEXT SWITCHER...",
        "LOADING MODULE INTERFACES...",
        "ESTABLISHING FILE SYSTEM...",
        "READY FOR TERNARY OPERATIONS..."
    ]
    
    for message in messages:
        # Fade in effect
        for i in range(1, len(message) + 1):
            print(f"{LIGHT_GREEN}║ {message[:i]:<70} ║{RESET}", end='\r')
            time.sleep(0.02)
        print(f"{LIGHT_GREEN}║ {message:<70} ║{RESET}")
        time.sleep(0.2)
        
        # Fade out effect
        for i in range(len(message), 0, -1):
            print(f"{LIGHT_GREEN}║ {message[:i]:<70} ║{RESET}", end='\r')
            time.sleep(0.01)
        print(f"{LIGHT_GREEN}║ {' ' * 70} ║{RESET}")
        time.sleep(0.1)
    
    print(f"{LIGHT_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    time.sleep(0.5)

def quantum_startup():
    """Quantum superposition effect with multiple states"""
    print(f"{LIGHT_GREEN}┌──────────────────────────────────────────────────────────────┐{RESET}")
    
    states = [
        "QUANTUM STATE: |0⟩",
        "QUANTUM STATE: |1⟩", 
        "QUANTUM STATE: |+⟩",
        "QUANTUM STATE: |-⟩",
        "SUPERPOSITION: α|0⟩ + β|1⟩",
        "ENTANGLED STATE: |00⟩ + |11⟩",
        "MEASUREMENT: COLLAPSING TO |1⟩",
        "QUANTUM MEMORY: INITIALIZED",
        "TERNARY QUBITS: READY",
        "QUANTUM CIRCUIT: ACTIVE"
    ]
    
    for i, state in enumerate(states):
        # Show quantum state
        print(f"{LIGHT_GREEN}│ {state:<70} │{RESET}")
        time.sleep(0.2)
        
        # Show probability distribution
        prob = random.random()
        bar = "█" * int(prob * 20) + "░" * (20 - int(prob * 20))
        print(f"{LIGHT_GREEN}│ Probability: [{bar}] {prob:.2f}{' ' * 40} │{RESET}")
        time.sleep(0.3)
    
    print(f"{LIGHT_GREEN}└──────────────────────────────────────────────────────────────┘{RESET}")
    time.sleep(0.5)

def retro_terminal_startup():
    """Retro terminal startup with typewriter effect"""
    print(f"{LIGHT_GREEN}┌──────────────────────────────────────────────────────────────┐{RESET}")
    
    messages = [
        "BOOTING QUANTIFIED TERNARY OS v0.0.5.0...",
        "CHECKING MEMORY: 59,049 TRYTES AVAILABLE",
        "LOADING KERNEL: BASE-3 LOGIC GATES",
        "INITIALIZING FILE SYSTEM: 177,147 TRYTES",
        "STARTING PROCESSES: CONTEXT SWITCHER",
        "LOADING MODULES: FS, WFE, SG, SI, BP",
        "ESTABLISHING CONNECTIONS: LOCALHOST",
        "VALIDATING INTEGRITY: ALL SYSTEMS OK",
        "CALIBRATING CLOCKS: TERNARY TIMING",
        "SYSTEM READY: AWAITING USER INPUT"
    ]
    
    for message in messages:
        # Typewriter effect
        for char in message:
            print(char, end='', flush=True)
            time.sleep(0.02)
        print()
        time.sleep(0.2)
    
    print(f"{LIGHT_GREEN}└──────────────────────────────────────────────────────────────┘{RESET}")
    time.sleep(0.5)

# Dictionary of all startup effects
STARTUP_EFFECTS = {
    'matrix': matrix_style_startup,
    'binary': binary_rain_startup,
    'scanline': scanline_startup,
    'glitch': glitch_startup,
    'hologram': hologram_startup,
    'quantum': quantum_startup,
    'retro': retro_terminal_startup
}

def show_startup_menu():
    """Show available startup effects"""
    print(f"{YELLOW}Available Startup Effects:{RESET}")
    for name, func in STARTUP_EFFECTS.items():
        print(f"  {LIGHT_GREEN}{name}{RESET} - {func.__doc__.split('.')[0]}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        effect = sys.argv[1].lower()
        if effect in STARTUP_EFFECTS:
            STARTUP_EFFECTS[effect]()
        else:
            print(f"{RED}Unknown effect: {effect}{RESET}")
            show_startup_menu()
    else:
        show_startup_menu() 