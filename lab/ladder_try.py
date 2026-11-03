"""ladder_try.py: the interventions on each test, training seeds 0-63 x 2 (lab/ladder.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from ladder import run, line
for rule, arm, kw in [("plain", "circuit", {}), ("plain", "transition", {}), ("plain", "lengths", {}), ("plain", "rhythm", {}), ("plain", "circuit", dict(trust=0)),
                      ("alternate", "circuit", dict(trust=0)), ("alternate", "flip", {}), ("alternate", "alteye", {}), ("alternate", "lengths", {}), ("alternate", "transition", {}),
                      ("pattern", "circuit", dict(trust=0)), ("pattern", "flip", {}), ("pattern", "lengths", {}), ("pattern", "transition", {})] + \
    [(f"swap{T}", a, k) for T in (50, 20, 10, 5) for a, k in (("circuit", dict(trust=0)), ("rhythm", {}), ("lengths", {}))]:
    L = run(rule, arm, range(0, 64), kw)
    line(f"{rule} {arm} {kw}", L)
    if arm == "rhythm":
        print("   learned T, median", np.median([l.T for l in L if l.T and l.T < 1e8] or [0]), "flips", np.mean([len(l.flips) for l in L]))
    if arm == "lengths":
        print("   lengths, median", np.median([x for l in L for x in l.R]), "flips", np.mean([len(l.flips) for l in L]))
    if arm == "transition":
        print("   turned on in", sum(bool(l.on_at) for l in L), "of", len(L), "median at", np.median([l.on_at[0] for l in L if l.on_at] or [0]))
