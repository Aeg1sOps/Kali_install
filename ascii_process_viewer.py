#!/usr/bin/env python3
"""
ASCII Process Viewer
Displays running processes as ASCII graphs (CPU and memory usage bars).
All comments and on-screen text are in English as requested.

Requirements:
  - psutil (install with `pip install psutil`)

Usage:
  python ascii_process_viewer.py          # run with defaults
  python ascii_process_viewer.py -n 15   # show top 15 processes
  python ascii_process_viewer.py -r 1.0  # refresh every 1.0 seconds

This is a lightweight, portable terminal viewer that uses simple ANSI
clearing to update the screen. It avoids external dependencies other
than psutil and should work on Linux, macOS and Windows (inside a
compatible terminal).
"""

import argparse
import os
import shutil
import sys
import time

try:
    import psutil
except Exception as e:
    sys.stderr.write("psutil is required. Install with: pip install psutil\n")
    sys.exit(1)

# ----------------------------- Configuration -----------------------------
DEFAULT_TOP = 10         # how many processes to display by default
DEFAULT_REFRESH = 1.0    # seconds between updates
MIN_BAR_WIDTH = 10       # minimum width for the ASCII bar
MAX_NAME_LEN = 25        # truncate long process names

# ----------------------------- Utility functions ------------------------

def clear_screen():
    """Clear terminal screen using ANSI escape codes (cross-platform)."""
    if os.name == 'nt':
        # modern Windows terminals understand ANSI codes; fallback to cls
        os.system('cls')
    else:
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()


def clamp(v, a, b):
    return max(a, min(b, v))


def proportion_bar(value, width):
    """Return a bar string representing `value` in percent (0-100) using `width` chars."""
    value = clamp(value, 0.0, 100.0)
    filled = int(round((value / 100.0) * width))
    empty = width - filled
    return '[' + ('#' * filled) + (' ' * empty) + ']'  # simple filled bar


# ----------------------------- Main display -----------------------------

def fetch_processes():
    """Return a list of dicts for each process with pid, name, cpu, mem."""
    procs = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            info = p.info
            # cpu_percent(None) gives the percent since last call; we call it in the main loop
            cpu = p.cpu_percent(interval=None)
            mem = p.memory_percent()
            procs.append({
                'pid': info.get('pid'),
                'name': (info.get('name') or '')[:MAX_NAME_LEN],
                'cpu': cpu,
                'mem': mem,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def draw(procs, term_width, top_n, refresh_interval):
    """Draw the process table and bars to the terminal."""
    # layout columns: PID | NAME | CPU% | CPU BAR | MEM% | MEM BAR
    # reserve minimal widths for fixed columns
    pid_w = 6
    cpu_pct_w = 6   # e.g. "100.0%"
    mem_pct_w = 6
    name_w = 1 + MAX_NAME_LEN  # padded

    # compute remaining width for two bars
    reserved = pid_w + name_w + cpu_pct_w + mem_pct_w + 10  # spacing
    bar_space = max(MIN_BAR_WIDTH, term_width - reserved)
    # split bar_space roughly half for CPU and half for MEM
    cpu_bar_w = bar_space // 2
    mem_bar_w = bar_space - cpu_bar_w

    # Header
    
    logo = r"""
    █████████                     ████             ███████                     
  ███▒▒▒▒▒███                   ▒▒███           ███▒▒▒▒▒███                   
 ▒███    ▒███   ██████   ███████ ▒███   █████  ███     ▒▒███ ████████   █████ 
 ▒███████████  ███▒▒███ ███▒▒███ ▒███  ███▒▒  ▒███      ▒███▒▒███▒▒███ ███▒▒  
 ▒███▒▒▒▒▒███ ▒███████ ▒███ ▒███ ▒███ ▒▒█████ ▒███      ▒███ ▒███ ▒███▒▒█████ 
 ▒███    ▒███ ▒███▒▒▒  ▒███ ▒███ ▒███  ▒▒▒▒███▒▒███     ███  ▒███ ▒███ ▒▒▒▒███
 █████   █████▒▒██████ ▒▒███████ █████ ██████  ▒▒▒███████▒   ▒███████  ██████ 
▒▒▒▒▒   ▒▒▒▒▒  ▒▒▒▒▒▒   ▒▒▒▒▒███▒▒▒▒▒ ▒▒▒▒▒▒     ▒▒▒▒▒▒▒     ▒███▒▒▒  ▒▒▒▒▒▒  
                        ███ ▒███                             ▒███             
                       ▒▒██████                              █████            
                        ▒▒▒▒▒▒                              ▒▒▒▒▒             
                                                                             
"""                                                                         
    print(logo)

    print(f"ASCII Process Viewer — top {top_n} processes by CPU (refresh {refresh_interval:.1f}s)")
    print('-' * term_width)
    header = f"{'PID':<{pid_w}} {'NAME':<{name_w}} {'CPU%':>{cpu_pct_w}} {'CPU BAR':<{cpu_bar_w+2}} {'MEM%':>{mem_pct_w}} {'MEM BAR':<{mem_bar_w+2}}"
    print(header)
    print('-' * term_width)

    for p in procs[:top_n]:
        pid = str(p['pid'])[:pid_w]
        name = p['name'][:MAX_NAME_LEN]
        cpu = p['cpu']
        mem = p['mem']
        cpu_bar = proportion_bar(cpu, cpu_bar_w - 2)
        mem_bar = proportion_bar(mem, mem_bar_w - 2)
        line = f"{pid:<{pid_w}} {name:<{name_w}} {cpu:>{cpu_pct_w}.1f}% {cpu_bar} {mem:>{mem_pct_w}.1f}% {mem_bar}"
        print(line)

    print('-' * term_width)
    # summary line
    total_procs = len(psutil.pids())
    print(f"Processes: {total_procs} | Showing top {min(top_n, len(procs))} by CPU usage")


def main():
    parser = argparse.ArgumentParser(description='ASCII process viewer (comments/text in English)')
    parser.add_argument('-n', '--top', type=int, default=DEFAULT_TOP, help='number of top processes to show')
    parser.add_argument('-r', '--refresh', type=float, default=DEFAULT_REFRESH, help='refresh interval in seconds')
    args = parser.parse_args()

    top_n = max(1, args.top)
    refresh = max(0.1, args.refresh)

    # Prime cpu_percent counters: first call returns 0.0 for each process
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    try:
        while True:
            time.sleep(refresh)
            procs = fetch_processes()
            # sort by cpu desc then mem desc
            procs.sort(key=lambda x: (x['cpu'], x['mem']), reverse=True)
            term_width = shutil.get_terminal_size((120, 20)).columns
            clear_screen()
            draw(procs, term_width, top_n, refresh)
    except KeyboardInterrupt:
        print('\nExiting...')
        sys.exit(0)


if __name__ == '__main__':
    main()
