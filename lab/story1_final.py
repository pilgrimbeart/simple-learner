"""story1_final.py: the pilot story's final judgement on seeds 50200-50327 x 2, never used to choose anything: the
circuit (a tally written only while driving, one step of trust) against the floor, the ceiling, the ideal observer and
B, paired; when it detects; its controls (lab/story1.py)."""
import pickle, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from story1 import lives, paired, table, M, ROOT
from minimal.spec import gain, efficiency
p, spread = M.from_bench()
seeds = range(50200, 50328)
A = {"unwired": ("unwired", {}), "told": ("told", {}), "bayes": ("bayes", {}), "B": ("B", {}),
     "circuit": ("gated", dict(use=0, trust=1))}
R = {}
for n, (arm, g) in A.items():
    R[n] = lives(arm, dict(p, **g), spread, seeds); table(n, R[n])
pickle.dump(R, open(f"{ROOT}/lab/v/story1_final.lives", "wb"))
for a, b in [("circuit", "told"), ("circuit", "bayes"), ("circuit", "B"), ("circuit", "unwired"), ("bayes", "told"), ("B", "told")]:
    for lab, f in (("efficiency", efficiency), ("gain", gain)):
        d, i = paired(R[a], R[b], f)
        print(f"{a} - {b} {lab}: {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]")
for n in ("bayes", "B", "circuit"):
    L = R[n]; w = [l for l in L if not l.born_right]; r = [l for l in L if l.born_right]
    t = [l.flips[0] if l.flips else np.inf for l in w]
    print(f"{n}: born wrong {len(w)}: first flip median {np.median(t):.1f} s, 90th {np.percentile(t, 90):.1f} s, never {sum(np.isinf(t))}; born right {len(r)}: {np.mean([bool(l.flips) for l in r]):.1%} ever flip, {np.mean([len(l.flips) for l in r]):.2f} flips a life; right {np.mean([l.right for l in L]):.1%}")
for c in ("all-food", "random"):
    L = lives("gated", dict(p, use=0, trust=1), spread, seeds, control=c)
    table(f"{c} circuit", L); print(f"   flips a life {np.mean([len(l.flips) for l in L]):.2f}", flush=True)
    T = lives("told", p, spread, seeds, control=c); table(f"{c} told", T)
