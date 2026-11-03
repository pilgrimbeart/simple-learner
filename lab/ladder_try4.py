"""ladder_try4.py: growing the sequence when frustrated, training seeds 0-63 x 2 (lab/ladder.py, GrowSeq)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from collections import Counter
from ladder import run, line
for th, tau in [(2, 10), (3, 10), (2, 20), (3, 20), (4, 20), (4, 40)]:
    for rule in ("plain", "alternate", "pattern", "swap20"):
        L = run(rule, "grow", range(0, 64), dict(theta=float(th), tau=float(tau)))
        line(f"theta {th} tau {tau} {rule}", L)
        first = [l.grew[0][0] for l in L if l.grew]
        print("   final length", sorted(Counter(l.n for l in L).items()), "first growth median", round(float(np.median(first)), 1) if first else None, flush=True)
