#!/usr/bin/env python3
import curses
import random
import time
from helpers import GREEN, RED, YELLOW, RESET

CONTEXT_NAMES = {
    'CORE': 'Core',
    'FS':   'File System',
    'WFE':  'Windows File Explorer',
    'SG':   'Snake Game',
    'SI':   'System Information'
}

def show_sg_hints():
    print(f"{GREEN}Arrow keys to move, Q to quit{RESET}")

def snake_game():
    show_sg_hints()
    def _game(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        sh, sw = stdscr.getmaxyx()
        w = curses.newwin(sh, sw, 0, 0)
        w.keypad(1)
        w.timeout(100)

        snk_x = sw//4
        snk_y = sh//2
        snake = [[snk_y, snk_x], [snk_y, snk_x-1], [snk_y, snk_x-2]]
        food = [random.randint(1, sh-2), random.randint(1, sw-2)]
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        w.addch(food[0], food[1], curses.ACS_PI, curses.color_pair(2))

        key = curses.KEY_RIGHT
        score = 0

        while True:
            next_key = w.getch()
            key = key if next_key == -1 else next_key
            head = snake[0].copy()

            if key == curses.KEY_DOWN:  head[0] += 1
            elif key == curses.KEY_UP:   head[0] -= 1
            elif key == curses.KEY_LEFT: head[1] -= 1
            elif key == curses.KEY_RIGHT:head[1] += 1
            elif key in (ord('q'), ord('Q')): break

            snake.insert(0, head)
            if head == food:
                score += 1
                food = None
                while food is None:
                    nf = [random.randint(1, sh-2), random.randint(1, sw-2)]
                    if nf not in snake:
                        food = nf
                w.addch(food[0], food[1], curses.ACS_PI, curses.color_pair(2))
            else:
                tail = snake.pop()
                w.addch(tail[0], tail[1], ' ')

            if (head[0] in [0, sh] or head[1] in [0, sw] or head in snake[1:]):
                msg = " GAME OVER! "
                w.addstr(sh//2, sw//2-len(msg)//2, msg, curses.color_pair(1))
                w.refresh()
                time.sleep(1)
                break

            w.addch(head[0], head[1], curses.ACS_CKBOARD, curses.color_pair(1))
            w.refresh()

        stdscr.clear()
        stdscr.addstr(0, 0, f"Final Score: {score}\n")
        stdscr.getch()

    curses.wrapper(_game)
