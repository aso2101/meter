#!/usr/bin/env python3
"""Check Pratyaya/pratyaya.py against the original scripts and for round trips."""
import os, subprocess, sys, random
here = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(here, '..', 'Pratyaya')
sys.path.insert(0, P)
from pratyaya import uddista, nasta
import itertools

for n in range(1, 13):
    seen = set()
    for t in itertools.product('GL', repeat=n):
        p = ''.join(t); s = uddista(p)
        assert nasta(n, s) == p, (p, s)
        seen.add(s)
    assert seen == set(range(1, 2 ** n + 1)), n
random.seed(1)
for _ in range(25):
    n = random.randint(1, 26); p = ''.join(random.choice('GL') for _ in range(n))
    a = subprocess.run([sys.executable, os.path.join(P, 'uddista.py'), p], capture_output=True, text=True).stdout.strip()
    b = subprocess.run([sys.executable, os.path.join(P, 'nasta.py'), str(n), a], capture_output=True, text=True).stdout.strip()
    assert int(a) == uddista(p) and b == p == nasta(n, int(a)), (p, a, b)
print('ok')
