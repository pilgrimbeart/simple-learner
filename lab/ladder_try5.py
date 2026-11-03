"""ladder_try5.py: one brain reading which cure from the run of goods before a vouched bad, training seeds 0-63 x 2."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from collections import Counter
from ladder import run, line
for sh, tv in [(2, 40), (3, 40), (2, 20), (4, 40)]:
    for rule in ("plain", "alternate", "pattern", "swap50", "swap20", "swap10", "swap5"):
        L = run(rule, "diagnose", range(0, 64), dict(theta=3.0, tau=10.0, short=float(sh), tau_v=float(tv)))
        line(f"short {sh} tau_v {tv} {rule}", L)
        print("   final length", sorted(Counter(l.n for l in L).items()), flush=True)
