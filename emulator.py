#!/usr/bin/env python3

from curses import wrapper

def main(stdscr):
    stdscr.clear()

    wina = stdscr.

    for i in range(0, 10):
        v = 10 - i
        stdscr.addstr(i, i, '10 devided by %d is %f' % (v, 10/v))

    stdscr.refresh()
    stdscr.getkey()

wrapper(main)
