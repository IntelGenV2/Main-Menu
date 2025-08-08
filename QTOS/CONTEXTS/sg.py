#!/usr/bin/env python3
import random
import time
from helpers import GREEN, RED, YELLOW, RESET

# Try to import curses, with fallback for Windows
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

CONTEXT_NAMES = {
    'CORE': 'Core',
    'FS':   'File System',
    'WFE':  'Windows File Explorer',
    'SG':   'Snake Game',
    'SI':   'System Information'
}

def show_sg_hints():
    """Display game instructions"""
    print(f"{GREEN}Arrow keys to move, Q to quit{RESET}")

def snake_game():
    """Optimized snake game with improved performance"""
    if not CURSES_AVAILABLE:
        print(f"{RED}[ ERR ] Snake game requires curses support{RESET}")
        print(f"{YELLOW}[ INFO ] Install windows-curses: pip install windows-curses{RESET}")
        return
    
    show_sg_hints()
    
    def _game(stdscr):
        # Initialize curses
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        
        # Get screen dimensions
        sh, sw = stdscr.getmaxyx()
        w = curses.newwin(sh, sw, 0, 0)
        w.keypad(1)
        w.timeout(100)

        # Initialize game state
        snk_x = sw // 4
        snk_y = sh // 2
        snake = [[snk_y, snk_x], [snk_y, snk_x-1], [snk_y, snk_x-2]]
        food = [random.randint(1, sh-2), random.randint(1, sw-2)]
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        
        # Draw initial food
        w.addch(food[0], food[1], curses.ACS_PI, curses.color_pair(2))

        key = curses.KEY_RIGHT
        score = 0
        
        # Game constants
        FOOD_CHAR = curses.ACS_PI
        SNAKE_CHAR = curses.ACS_CKBOARD
        FOOD_COLOR = curses.color_pair(2)
        SNAKE_COLOR = curses.color_pair(1)

        while True:
            # Handle input
            next_key = w.getch()
            key = key if next_key == -1 else next_key
            head = snake[0].copy()

            # Update head position based on key
            if key == curses.KEY_DOWN:  head[0] += 1
            elif key == curses.KEY_UP:   head[0] -= 1
            elif key == curses.KEY_LEFT: head[1] -= 1
            elif key == curses.KEY_RIGHT:head[1] += 1
            elif key in (ord('q'), ord('Q')): break

            # Add new head
            snake.insert(0, head)
            
            # Check for food collision
            if head == food:
                score += 1
                food = None
                # Generate new food position
                while food is None:
                    nf = [random.randint(1, sh-2), random.randint(1, sw-2)]
                    if nf not in snake:
                        food = nf
                w.addch(food[0], food[1], FOOD_CHAR, FOOD_COLOR)
            else:
                # Remove tail
                tail = snake.pop()
                w.addch(tail[0], tail[1], ' ')

            # Check for collision with walls or self
            if (head[0] in [0, sh] or head[1] in [0, sw] or head in snake[1:]):
                msg = " GAME OVER! "
                w.addstr(sh//2, sw//2-len(msg)//2, msg, SNAKE_COLOR)
                w.refresh()
                time.sleep(1)
                break

            # Draw new head
            w.addch(head[0], head[1], SNAKE_CHAR, SNAKE_COLOR)
            w.refresh()

        # Game over screen
        stdscr.clear()
        stdscr.addstr(0, 0, f"Final Score: {score}\n")
        stdscr.getch()

    curses.wrapper(_game)
