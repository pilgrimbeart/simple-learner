"""story1_run3.py short|long: a limit on the run (lab/story1.py, Timed), lives of 100 s on training seeds, then long
lives: efficiency, the longest gap between meals (lives' thirds can't show it, so also lives with a third empty)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from story1 import lives, M, paired
from minimal.spec import summary
from discrete.poison import show
p, spread = M.from_bench()
base = dict(use=0, trust=1)
if sys.argv[1] == "short":
    A = lives("gated", dict(p, **base), spread, range(0, 64))
    print(show("no limit", summary(A)), flush=True)
    for r in (0.5, 1, 2, 5, 10, 20):
        L = lives("timed", dict(p, **base, run_max=r), spread, range(0, 64))
        d, i = paired(L, A)
        print(show(f"run_max {r}", summary(L)), f" vs none {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
else:
    r, secs, lo, hi = float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    A = lives("gated", dict(p, **base), spread, range(lo, hi), secs)
    L = lives("timed", dict(p, **base, run_max=r), spread, range(lo, hi), secs)
    print(show("no limit", summary(A)), flush=True)
    print(show(f"run_max {r}", summary(L)), flush=True)
    d, i = paired(L, A)
    print(f"difference {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]")
