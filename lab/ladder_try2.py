"""ladder_try2.py: second round, training seeds 0-63 x 2 (lab/ladder.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from ladder import run, line
for rule, arm, kw in [("plain", "detect", {}), ("alternate", "detect", {}), ("alternate", "detect", dict(theta=1.0)), ("alternate", "detect", dict(theta=3.0)), ("plain", "detect", dict(theta=1.0)),
                      ("swap20", "detect", {}), ("pattern", "detect", {}),
                      ("plain", "lengths2", {}), ("alternate", "lengths2", {}), ("pattern", "lengths2", {}), ("swap10", "lengths2", {}),
                      ("plain", "volatile", {}), ("plain", "rhythm2", {})] + \
    [(f"swap{T}", a, k) for T in (50, 20, 10, 5) for a, k in (("volatile", {}), ("volatile", dict(tau=40.0)), ("rhythm2", {}), ("rhythm2", dict(lag=0.5)))]:
    L = run(rule, arm, range(0, 64), kw)
    line(f"{rule} {arm} {kw}", L)
    if arm == "detect":
        print("   latched in", sum(bool(l.on_at) for l in L), "of", len(L), "median at", np.median([l.on_at[0] for l in L if l.on_at] or [0]), flush=True)
