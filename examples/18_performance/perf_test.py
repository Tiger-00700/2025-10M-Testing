#!/usr/bin/env python3
# Placeholder example file.
"""Tiny CPU micro-benchmark example for examples/18_performance.

This script runs a small numeric loop and reports elapsed time. No external deps.
"""

import time

def work(n):
    s = 0
    for i in range(n):
        s += (i * i) % (i + 1)
    return s

if __name__ == '__main__':
    N = 200000
    t0 = time.time()
    r = work(N)
    t1 = time.time()
    print(f"work({N}) -> {r}  elapsed: {t1-t0:.4f}s")
