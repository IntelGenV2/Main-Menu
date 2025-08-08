#!/usr/bin/env python3
"""
QTOS Crash Timer Module
Simulates OS crashes with visual distortion effects
"""
import os
import sys
import time
import random
import threading
import signal
from pathlib import Path

# ANSI color codes for distortion effects
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BLACK = "\033[30m"

# Distortion characters for glitch effects
GLITCH_CHARS = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~\\"
CORRUPT_CHARS = "█▓▒░▄▌▐▀▄▌▐░▒▓█"
SYSTEM_CHARS = "0123456789ABCDEF"

class CrashTimer:
    def __init__(self):
        self.start_time = time.time()
        self.crash_time = None
        self.crash_thread = None
        self.is_crashed = False
        self.uptime_threshold = 60  # 1 minute minimum
        
    def start_crash_timer(self):
        """Start the crash timer in a separate thread"""
        if self.crash_thread is None:
            self.crash_thread = threading.Thread(target=self._crash_timer_loop, daemon=True)
            self.crash_thread.start()
    
    def _crash_timer_loop(self):
        """Main crash timer loop"""
        # 15% chance to crash during startup animation
        if random.random() < 0.15:
            # Wait for startup to begin, then crash at random point
            time.sleep(random.uniform(3, 8))  # Wait 3-8 seconds for startup to be in progress
            if not self.is_crashed:
                self._trigger_crash()
                return
        
        # Wait for minimum uptime
        while time.time() - self.start_time < self.uptime_threshold:
            time.sleep(1)
        
        # Pick random crash time between 1-5 minutes after threshold
        crash_delay = random.uniform(60, 300)  # 1-5 minutes
        self.crash_time = time.time() + crash_delay
        
        # Wait for crash time
        while time.time() < self.crash_time and not self.is_crashed:
            time.sleep(0.1)
        
        if not self.is_crashed:
            self._trigger_crash()
    
    def _trigger_crash(self):
        """Trigger the OS crash with visual distortion"""
        self.is_crashed = True
        
        try:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Phase 1: Initial glitch effects
            self._show_glitch_effects()
            
            # Phase 2: System corruption messages
            self._show_corruption_messages()
            
            # Phase 3: Final crash screen (this will be the last thing shown)
            self._show_crash_screen()
            
            # Phase 4: Lock up the system (just beeping, no visual changes)
            self._lock_system_final()
        except Exception:
            # If any error occurs, just lock the system
            self._lock_system_final()
    
    def _show_glitch_effects(self):
        """Show initial glitch effects"""
        for i in range(20):
            # Beep sound during glitch effects
            if i % 3 == 0:  # Beep every 3 iterations
                try:
                    if os.name == 'nt':
                        import winsound
                        winsound.Beep(1200, 50)  # Higher frequency: 1200Hz for 50ms
                    else:
                        print('\a', end='', flush=True)
                except:
                    print('\a', end='', flush=True)
            
            # Random glitch lines
            for _ in range(random.randint(1, 5)):
                line = ''.join(random.choice(GLITCH_CHARS) for _ in range(random.randint(10, 80)))
                color = random.choice([RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN])
                print(f"{color}{line}{RESET}")
            
            # Random position cursor movements
            for _ in range(random.randint(1, 3)):
                x = random.randint(0, 80)
                y = random.randint(0, 24)
                print(f"\033[{y};{x}H{random.choice(GLITCH_CHARS)}", end='', flush=True)
            
            time.sleep(random.uniform(0.05, 0.2))
    
    def _show_corruption_messages(self):
        """Show system corruption messages"""
        corruption_messages = [
            "SYSTEM MEMORY CORRUPTION DETECTED",
            "KERNEL PANIC: UNRECOVERABLE ERROR",
            "FATAL EXCEPTION IN CORE MODULE",
            "STACK OVERFLOW IN TERNARY PROCESSOR",
            "CRITICAL SYSTEM FAILURE",
            "UNEXPECTED INTERRUPT IN BASE-3 LOGIC",
            "MEMORY ACCESS VIOLATION",
            "SYSTEM HALT: EMERGENCY SHUTDOWN REQUIRED"
        ]
        
        for i, msg in enumerate(corruption_messages):
            # Beep sound during corruption messages
            try:
                if os.name == 'nt':
                    import winsound
                    winsound.Beep(1400, 75)  # Even higher frequency: 1400Hz for 75ms
                else:
                    print('\a', end='', flush=True)
            except:
                print('\a', end='', flush=True)
            
            # Corrupt the message with random characters
            corrupted = ""
            for char in msg:
                if random.random() < 0.3:  # 30% chance to corrupt
                    corrupted += random.choice(GLITCH_CHARS)
                else:
                    corrupted += char
            
            # Print with glitch effects
            for j, char in enumerate(corrupted):
                color = random.choice([RED, YELLOW, WHITE])
                print(f"{color}{char}{RESET}", end='', flush=True)
                time.sleep(random.uniform(0.01, 0.05))
            print()
            time.sleep(random.uniform(0.2, 0.5))
    
    def _show_crash_screen(self):
        """Show final crash screen"""
        crash_screen = [
            "",
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    SYSTEM CRASH DETECTED                     ║",
            "║                                                              ║",
            "║  The operating system has encountered a critical error and   ║",
            "║  must be terminated. All unsaved data will be lost.          ║",
            "║                                                              ║",
            "║  Error Code: 0xDEADBEEF                                      ║",
            "║  Memory Address: 0x00000000                                  ║",
            "║  Stack Trace: [CORRUPTED]                                    ║",
            "║                                                              ║",
            "║  Press any key to restart the system...                      ║",
            "║                                                              ║",
            "╚══════════════════════════════════════════════════════════════╝",
            ""
        ]
        
        for i, line in enumerate(crash_screen):
            # Beep sound during crash screen
            if i % 2 == 0:  # Beep every other line
                try:
                    if os.name == 'nt':
                        import winsound
                        winsound.Beep(1600, 100)  # Highest frequency: 1600Hz for 100ms
                    else:
                        print('\a', end='', flush=True)
                except:
                    print('\a', end='', flush=True)
            
            # Corrupt each line with glitch effects
            corrupted_line = ""
            for char in line:
                if random.random() < 0.1:  # 10% corruption
                    corrupted_line += random.choice(GLITCH_CHARS)
                else:
                    corrupted_line += char
            
            print(f"{RED}{corrupted_line}{RESET}")
            time.sleep(0.1)
    
    def _lock_system(self):
        """Lock up the system requiring restart"""
        # Clear screen completely
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Infinite loop to lock the system with beep sounds
        beep_counter = 0
        while True:
            # Beep sound every 250ms using Windows API for better sound
            if beep_counter % 25 == 0:  # 25 * 0.01s = 0.25s = 250ms
                try:
                    # Try Windows-specific beep first
                    if os.name == 'nt':
                        import winsound
                        winsound.Beep(1800, 150)  # Highest frequency: 1800Hz for 150ms
                    else:
                        # Fallback to system beep
                        print('\a', end='', flush=True)
                except:
                    # Final fallback
                    print('\a', end='', flush=True)
            
            # Show random glitch effects
            if random.random() < 0.1:  # 10% chance each iteration
                x = random.randint(0, 80)
                y = random.randint(0, 24)
                char = random.choice(GLITCH_CHARS)
                color = random.choice([RED, YELLOW, WHITE])
                print(f"\033[{y};{x}H{color}{char}{RESET}", end='', flush=True)
            
            time.sleep(0.01)  # 10ms intervals for precise beep timing
            beep_counter += 1
    
    def _lock_system_final(self):
        """Lock up the system with just beeping, keeping the crash screen visible"""
        # Infinite loop to lock the system with beep sounds only
        beep_counter = 0
        while True:
            # Beep sound every 250ms using Windows API for better sound
            if beep_counter % 25 == 0:  # 25 * 0.01s = 0.25s = 250ms
                try:
                    # Try Windows-specific beep first
                    if os.name == 'nt':
                        import winsound
                        winsound.Beep(1800, 150)  # Highest frequency: 1800Hz for 150ms
                    else:
                        # Fallback to system beep
                        print('\a', end='', flush=True)
                except:
                    # Final fallback
                    print('\a', end='', flush=True)
            
            time.sleep(0.01)  # 10ms intervals for precise beep timing
            beep_counter += 1

# Global crash timer instance
crash_timer = CrashTimer()

# Global crash control - default is enabled (True)
crash_enabled = True

def start_crash_timer():
    """Start the crash timer (called from core.py)"""
    if crash_enabled:
        crash_timer.start_crash_timer()

def is_system_crashed():
    """Check if system has crashed"""
    return crash_enabled and crash_timer.is_crashed

def enable_crashes():
    """Enable crash timer"""
    global crash_enabled
    crash_enabled = True
    return "Crash timer enabled"

def disable_crashes():
    """Disable crash timer"""
    global crash_enabled
    crash_enabled = False
    return "Crash timer disabled"

def get_crash_status():
    """Get current crash timer status"""
    return crash_enabled 