"""table_diag.py: where the gated sweeps' and jitter's cost in the plain world comes from (lab/table.py; discrete/NOTEBOOK.md, D28).
Sweeps never allowed, against the base brain; then lives split by what the gate did, the balance through life."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
import table as T
from table_fix import SG
from minimal.spec import efficiency

S = dict(SG, gate=12.0)


def one(job):
    w, arm, kw, seed, seconds, first = job
    q = T.numbers(seed, kw)
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: T.arms()[arm](s, q))
    b = lf.brain
    R.setup(lf, seed)
    ticks, xs, ons = int(seconds / T.TICK), [], []
    while lf.t < ticks:
        t = lf.t * T.TICK
        lf.poison, R.now = R.poison(t), t
        R.tick(lf, t)
        lf.step()
        if lf.t % 100 == 0:
            xs.append(abs(getattr(b, "x", 0.0)))
            ons.append(b.p.get("sd", 0.0) > 0)
    return dict(sweeps=getattr(b, "sweeps", 0), x=float(np.mean(xs)), on=float(np.mean(ons)))


def trace(w, arm, kw, seconds):
    jobs = [(w, arm, kw, s, seconds, c) for s in T.HELD for c in T.COL]
    with ProcessPoolExecutor(8) as ex:
        return list(ex.map(one, jobs))


for s in (100.0, 1000.0):
    base = T.run("plain", "circuit", seconds=s)
    never = T.run("plain", "sweepsg", T.HELD, dict(S, gate=1e-6), s)
    print(f"{s:.0f} s, sweeps never allowed:", T.paired(never, base), flush=True)
    L = T.run("plain", "sweepsg", T.HELD, S, s)
    print(f"{s:.0f} s, gate 12:", T.paired(L, base), flush=True)
    tr = trace("plain", "sweepsg", S, s)
    sw = np.array([t["sweeps"] for t in tr])
    d = np.array([efficiency([a]) - efficiency([b]) for a, b in zip(L, base)])
    for lo, hi in ((0, 0), (1, 1), (2, 3), (4, 999)):
        m = (sw >= lo) & (sw <= hi)
        if m.any():
            print(f"   lives with {lo}-{hi} sweeps: {m.sum()}, mean difference {d[m].mean():+.2f}, mean |x| through life {np.mean([t['x'] for t, k in zip(tr, m) if k]):.3f}", flush=True)
for s in (100.0, 1000.0):
    kw = dict(learn=1.0, eta=0.03, sd=0.15, gate=16.0, win=100.0)
    tr = trace("plain", "jitterg", kw, s)
    print(f"jitterg plain {s:.0f} s: share of time on {np.mean([t['on'] for t in tr]):.2f}; mean |x| {np.mean([t['x'] for t in tr]):.3f}", flush=True)
