"""gsearch.py: can tuning B's knobs recover the guarded world? (certifying it as a recruitment case) Random search,
log-uniform within each knob's range (the tuner's bounds, and doubt's steps x0.33 to x3), on training seeds, then the
best few judged on held-out ones.

    python gsearch.py [N=200] [g=1] [d=2.5]"""
import sys
import pickle
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from discrete import model as M
from discrete.tuner import BOUNDS, KNOBS
from guarded import lives
from minimal.spec import summary

if __name__ == "__main__":
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
    N = int(kw.pop("N", 200))
    p, spread = M.from_bench()
    rng = np.random.default_rng(1)
    rows = []
    for i in range(N):
        q = dict(p, **kw)
        for k in KNOBS:
            q[k] = float(np.exp(rng.uniform(*np.log(BOUNDS[k]))))
        for k in ("step", "fstep"):
            q[k] = p[k] * float(np.exp(rng.uniform(np.log(1 / 3), np.log(3))))
        s = summary(lives("B", q, spread, range(0, 16), 100.0))
        rows.append((s["efficiency"], q))
        if i % 20 == 19:
            print(i + 1, "best so far", round(max(r[0] for r in rows), 2), flush=True)
    rows.sort(key=lambda r: -r[0])
    print("top on training:", [round(r[0], 2) for r in rows[:5]])
    held = []
    for e, q in rows[:5]:
        L = lives("B", q, spread, range(50000, 50032), 100.0)
        held.append((summary(L)["efficiency"], q, L))
        print(f"held out: {held[-1][0]:.2f}  ({', '.join(f'{k} {q[k]:.3g}' for k in KNOBS + ('step', 'fstep'))})",
              flush=True)
    pickle.dump(held, open("/home/pilgrim/git/simple-learner/"
                           "lab/v/gsearch.pkl", "wb"))
