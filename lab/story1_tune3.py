"""story1_tune3.py: the tally written only by vouched tastes, on training seeds 0-63 x 2 (lab/story1.py, Gated)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from story1 import lives, M
from minimal.spec import summary
p, spread = M.from_bench()
for g in [dict(use=0, trust=t) for t in (0, 1, 2, 3, 5, 9)] + [dict(use=1, trust=t, window=w) for w in (0.1, 0.3, 0.6) for t in (0, 2, 5)]:
    L = lives("gated", dict(p, **g), spread, range(0, 64))
    s = summary(L)
    r = [l for l in L if l.born_right]; w_ = [l for l in L if not l.born_right]
    ff = [l.flips[0] if l.flips else np.inf for l in w_]
    print(f"{g}: eff {s['efficiency']:.2f} gain {s['gain']:.2f} last {s['last']:.2f} stranded {s['stranded']:.0%} first flip {np.median(ff):.1f} s; born right flips {np.mean([len(l.flips) for l in r]):.1f} a life; right {np.mean([l.right for l in L]):.1%}", flush=True)
