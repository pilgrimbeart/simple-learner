"""story1_run.py [SECONDS] [SEEDS]: the user's sighting (2026-11-02): the circuit stuck in a straight run. A run starts
after boredom and only a food pulse ends it (discrete/model.py). Long lives, each run's length, what it ate and how its
heading moved; the longest gap between meals (lab/story1.py, Gated)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from story1 import Gated, M
from units import TICK


def one(job):
    arm, seed, poison, seconds = job
    p, spread = M.from_bench()
    q = dict(M.drawn(p, spread, seed), use=0, trust=1)
    lf = Life(seed, poison, brain=lambda s: (Gated if arm == "circuit" else M.Model)(s, q))
    b = lf.brain
    if arm == "told":
        b.food, b.p["V_H"] = 1 - lf.sensor[poison], 99.0
    runs, start, st = [], None, None
    while lf.t < int(seconds / TICK):
        lf.step()
        running = b.t - b.last_drive >= b.p["hold"] and b.t - b.last_food > b.p["bored"]
        if running and start is None:
            start, st = b.t, (len(lf.meals), lf.body.heading if hasattr(lf.body, "heading") else 0.0, lf.body.pos.copy())
        elif not running and start is not None:
            runs.append((b.t - start, start, len(lf.meals) - st[0]))
            start = None
    if start is not None:
        runs.append((b.t - start, start, len(lf.meals) - st[0]))
    mt = np.array([0.0] + [t * TICK for t, _ in lf.meals] + [seconds])
    gaps = np.diff(mt)
    r = np.array([x[0] for x in runs] or [0.0])
    longest = max(runs, key=lambda x: x[0]) if runs else (0, 0, 0)
    return arm, seed, poison, len(lf.meals), float(gaps.max()), float(mt[int(gaps.argmax())]), len(runs), float(np.median(r)), longest, float(r.sum() / seconds), float((r > 60).sum())


if __name__ == "__main__":
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 15000.0
    lo, hi = (int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "50206:50210").split(":"))
    jobs = [(a, s, c, seconds) for a in ("circuit", "B", "told") for s in range(lo, hi) for c in ("blue", "red")]
    with ProcessPoolExecutor(8) as ex:
        for x in ex.map(one, jobs):
            a, s, c, m, g, gt, nr, med, lg, frac, n60 = x
            print(f"{a} {s} {c}: meals {m}, longest gap {g:.0f} s at {gt:.0f} s; runs {nr}, median {med:.1f} s, longest {lg[0]:.0f} s at {lg[1]:.0f} s eating {lg[2]}; running {frac:.0%} of life; runs over 60 s {n60:.0f}", flush=True)
