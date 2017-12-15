#!/usr/bin/env python3

import sys
from curses import wrapper
import curses
import copy

def main(stdscr):
    stdscr.keypad(True)
    
    instrs = []
    labels = {'mymalloc': -2}

    with open(sys.argv[1]) as f:
        for r in f:
            r = r.split('\t')
            for i, x in enumerate(r):
                r[i] = x.strip()
            if r[0] == '':
                r.pop(0)
            if r[0][0] == '.':
                continue
            print(r)
            if r[0][-1] == ':':
                labels[r[0][:-1]] = len(instrs)
            else:
                instrs.append(r)

    regs = [
        'a1', 'a2', 'a3', 'a4',
        'v1', 'v2', 'v3', 'v4',
        'v5', 'v6', 'v7', 'ip',
        'fp', 'sp', 'lr'
    ]
                
    reg = {
        'a1': 0,
        'a2': 0,
        'a3': 0,
        'a4': 0,
        'v1': 0,
        'v2': 0,
        'v3': 0,
        'v4': 0,
        'v5': 0,
        'v6': 0,
        'v7': 0,
        'fp': 32768,
        'ip': 0,
        'sp': 32768,
        'lr': -1,
    }

    instr_counter = 0
    pc = labels['_toplevel']

    # (neq, lt)
    cmp_reg = (False, False)

    heap_it = 0
    mem = [0 for i in range(65536)]

    history = [(copy.deepcopy(reg), instr_counter, pc, cmp_reg, heap_it, copy.deepcopy(mem))]

    cur = None
        
    def show_reg():
        r = 0
        c = 0
        for k in regs:
            stdscr.addstr(r, c, '%s: %5d' % (k, reg[k]))
            if c == 11 * 3:
                r += 1
                c = 0
            else:
                stdscr.addstr(r, c+9, ', ')
                c += 11

    def show_heap():
        h = 4
        w = 6
        for i in range(h):
            for j in range(w):
                p = i * w + j
                stdscr.addstr(i + 6, j * 12, '%2d: %5d' % (p * 4, mem[p]))
                
    def show_stack():
        fp = reg['fp'] // 4
        sp = reg['sp'] // 4
        hi = fp + 2
        lo = hi - 10
        for r, i in enumerate(range(lo, hi)[::-1]):
            stdscr.addstr(r + 12, 0, '%5d: %5d' % (i * 4, mem[i]))
            if i == fp and i == sp:
                stdscr.addstr(r + 12, 14, '<- fp, sp')
            if i == fp:
                stdscr.addstr(r + 12, 14, '<- fp')
            if i == sp:
                stdscr.addstr(r + 12, 14, '<- sp')

    def show_instrs():
        lo = max(0, pc - 5)
        hi = min(len(instrs), lo + 10)
        
        for r, i in enumerate(range(lo, hi)):
            stdscr.addstr(r + 12, 32, '%5d: %s' % (i, instrs[i]))
            if i == pc:
                stdscr.addstr(r + 12, 28, 'pc ->')
                
    def get_addr(addr):
        if addr[0] == '[':
            # register indirect
            x = addr[1:-1]
            li = x.split(',')
            assert(len(li) == 2)
            li[0] = li[0].strip()
            li[1] = li[1].strip()
            return reg[li[0]] + int(li[1][1:])
        elif addr[0] == '=':
            # label
            return labels[addr[1:]]
        elif addr[0] == '#':
            # imidiate
            return int(addr[1:])
        else:
            # register
            return reg[addr]

    while pc >= 0:
        instr_counter += 1
        instr = instrs[pc]
        if '[' in instr[1]:
            ope = instr[1].split(',', instr[1].count(',') - 1)
        else:
            ope = instr[1].split(',')
        for i, x in enumerate(ope):
            ope[i] = x.strip()

        if instr[0] == 'add':
            assert(len(ope) == 3)
            a = reg[ope[1]]        
            b = get_addr(ope[2])
            reg[ope[0]] = a + b
            pc += 1
        elif instr[0] == 'b':
            pc = labels[instr[1]]
        elif instr[0] == 'bl':
            reg['lr'] = pc + 1
            pc = labels[instr[1]]
        elif instr[0] == 'blt':
            if cmp_reg[1]:
                pc = labels[instr[1]]
            else:
                pc += 1
        elif instr[0] == 'blx':
            reg['lr'] = pc + 1
            pc = reg[instr[1]]
        elif instr[0] == 'bne':
            if cmp_reg[0]:
                pc = labels[instr[1]]
            else:
                pc += 1
        elif instr[0] == 'bx':
            pc = reg[instr[1]]
        elif instr[0] == 'cmp':
            assert(len(ope) == 2)
            a = reg[ope[0]]
            b = get_addr(ope[1])
            cmp_reg = (a != b, a < b)
            pc += 1
        elif instr[0] == 'ldr':
            assert(len(ope) == 2)
            a = get_addr(ope[1])
            if ope[1][0] == '=':
                reg[ope[0]] = a
            else:
                reg[ope[0]] = mem[a//4]
            pc += 1
        elif instr[0] == 'mov':
            assert(len(ope) == 2)
            a = get_addr(ope[1])
            reg[ope[0]] = a
            pc += 1
        elif instr[0] == 'mul':
            assert(len(ope) == 3)
            a = reg[ope[1]]
            b = get_addr(ope[2])
            reg[ope[0]] = a * b
            pc += 1
        elif instr[0] == 'str':
            assert(len(ope) == 2)
            a = get_addr(ope[1])
            mem[a//4] = reg[ope[0]]
            pc += 1
        elif instr[0] == 'sub':
            assert(len(ope) == 3)
            a = reg[ope[1]]
            b = get_addr(ope[2])
            reg[ope[0]] = a - b
            pc += 1

        if pc == -2:
            # mymalloc
            cur_it = heap_it
            heap_it += reg['a1'] * 4
            reg['a1'] = cur_it
            pc = reg['lr']

        history.append((copy.deepcopy(reg), instr_counter, pc, cmp_reg, heap_it, copy.deepcopy(mem)))

        end = False

        if cur:
            cur -= 1
        else:
            r = 24
            pos = 0
            while True:
                stdscr.clear()

                show_reg()
                show_heap()
                show_stack()
                show_instrs()

                # show usage
                if cur is None:
                    stdscr.addstr(r, 0, 'q: quit, left_arrow: back, colon: input, otherwise: next')
                else:
                    stdscr.addstr(r, 0, 'q: quit, c: cancel, number: input, x: go')
                
                stdscr.refresh()
                
                stdscr.move(r+1, 0)
                if cur is not None:
                    stdscr.addstr(r+1, 0, ':' + str(cur))
                    stdscr.move(r+1, len(str(cur)) + 1)
                    
                c = stdscr.getch()
                
                if c == ord('q'):
                    end = True
                    break
                elif cur is None and c == curses.KEY_LEFT:
                    if len(history) > 0:
                        reg, instr_counter, pc, cmp_reg, heap_it, mem = history[-1]
                        history.pop(len(history)-1)
                elif cur is None and c == ord(':'):
                    cur = 0
                elif cur is not None and c == ord('c'):
                    cur = None
                elif cur is not None and ord('0') <= c and c <= ord('9'):
                    x = c - ord('0')
                    cur = cur * 10 + x
                elif c == ord('x'):
                    break
                else:
                    cur = None
                    break
            if end:
                break

    stdscr.clear()

    show_reg()
    show_heap()
    show_stack()
    show_instrs()

    stdscr.refresh()

    r = 24
    stdscr.addstr(r, 0, 'press q to quit')
    
    while c != ord('q') :
        c = stdscr.getch()

wrapper(main)
