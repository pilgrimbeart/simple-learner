"""table_trace.py: why an automatic version pays where it shouldn't, or gains little (lab/table.py; discrete/NOTEBOOK.md, D28)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
import table as T
from table_rows import SWEEP
from minimal.spec import efficiency


def one(job):
    w, arm, kw, seed, seconds, first = job
    q = T.numbers(seed, kw)
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: T.arms()[arm](s, q))
    b = lf.brain
    R.setup(lf, seed)
    if hasattr(R, "taste"):
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    ticks, done, pauses, xs = int(seconds / T.TICK), 0, [], []
    while lf.t < ticks:
        t = lf.t * T.TICK
        lf.poison, R.now = R.poison(t), t
        R.tick(lf, t)
        lf.step()
        while done < len(lf.meals):
            R.ate(lf.meals[done][1])
            done += 1
        if lf.t % 500 == 0:
            pauses.append(b.p.get("pause", 0.0))
            xs.append(getattr(b, "x", 0.0))
    return dict(sweeps=getattr(b, "sweeps", 0), x=xs, pause=pauses, n=getattr(b, "n", None), on=list(getattr(b, "on_at", [])), flips=len(b.flips))


def run(w, arm, kw, seconds):
    jobs = [(w, arm, kw, s, seconds, c) for s in range(53000, 53016) for c in T.COL]
    with ProcessPoolExecutor(8) as ex:
        return list(ex.map(one, jobs))


SG = dict(SWEEP, cal_first=32.0, cal_fast=32.0, bank=192.0, gate=12.0)
L = run("plain", "sweepsg", SG, 1000.0)
print("plain sweepsg: sweeps", sorted(l["sweeps"] for l in L), "\n  final |x|", np.round(sorted(abs(l["x"][-1]) for l in L), 2).tolist())
for arm, kw in (("learnpause", {}), ("learnpause2", dict(theta=3.0, tau_p=400.0, win=1.2, down=1.0))):
    L = run("digest", arm, kw, 100.0)
    P = np.array([l["pause"] for l in L])
    print(arm, "digest: median pause each 5 s", np.round(np.median(P, 0), 2).tolist(), "\n  share of lives with the pause off, each 5 s", np.round((P == 0).mean(0), 2).tolist())
L = run("plain", "jitterg", dict(learn=1.0, eta=0.06, sd=0.15, gate=15.0), 1000.0)
print("plain jitterg: final |x|", np.round(sorted(abs(l["x"][-1]) for l in L), 2).tolist())
