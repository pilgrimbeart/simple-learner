"""story1_tune2.py: the simplest forms on training seeds 0-63 x 2: a run of n poisons with no food between flips the bit
(a counter food resets); and each eye's pathway blocked, for the class comparison (lab/story1.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from story1 import lives, M
from minimal.spec import summary
p, spread = M.from_bench()
for name, arm, g in [(f"run n={n}", "B", dict(fstep=9.0, drift=0.0, V_L=0.0, step=0.5, V_H=0.5*n-0.25)) for n in (1, 2, 3)] + \
    [(f"run n={n}, no reverse", "B", dict(fstep=9.0, drift=0.0, V_L=0.0, step=0.5, V_H=0.5*n-0.25, )) for n in ()] + \
    [(f"path block t{t} c{c} w{w} tau{tau}", "path", dict(reverse=0, theta=t, cost=c, trust=w, tau=tau))
     for t in (0.5, 1.5, 2.5) for c in (1, 2) for w in (1, 3) for tau in (0, 30)]:
    s = summary(lives(arm, dict(p, **g), spread, range(0, 64)))
    print(f"{name}: eff {s['efficiency']:.2f} gain {s['gain']:.2f} last {s['last']:.2f} stranded {s['stranded']:.0%}", flush=True)
