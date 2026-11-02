import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import itertools
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from discrete.circuits import learn_hold
from discrete.life import bench

def check(a):
    kw, seed = a
    n = learn_hold(None if seed is None else np.random.default_rng(seed), roam=False, **kw)
    # which eye is free at first is decided by start-up; pulse both eyes, then two poisons, then both again
    pul = [(0, 2.0), (1, 2.5), ("poison", 3.0), ("poison", 3.1), (0, 4.0), (1, 4.5), ("poison", 6.0), (0, 7.0), (1, 7.5)]
    t, V, P = bench(n, 8.0, ["h", "c0"], pulses=pul, step=1e-5)
    h, c0 = V["h"], V["c0"]
    jump = lambda t0: float(h[np.searchsorted(t, t0 + 0.004)] - h[np.searchsorted(t, t0 - 0.001)])
    j = [jump(x) for x in (2.0, 2.5, 4.0, 4.5, 7.0, 7.5)]
    b1, b2, b3 = (c0[np.searchsorted(t, x)] > 0.4 for x in (1.9, 3.9, 6.9))
    free = [jump for jump in j]
    ok = (b1 != b2) and (b2 == b3)            # two poisons flip it, one doesn't
    on = [max(j[0], j[1]), max(j[2], j[3]), max(j[4], j[5])]
    off = [min(j[0], j[1]), min(j[2], j[3]), min(j[4], j[5])]
    return kw, seed, ok, min(on), max(off), P

if __name__ == "__main__":
    grid = [dict(rl=rl, rx=rx, rk=rk) for rl, rx, rk in itertools.product((5e7, 1e8, 2e8), (5e7, 1e8, 2e8), (5e6, 1e7, 2e7))]
    jobs = [(kw, s) for kw in grid for s in (None, 1, 2)]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(check, jobs))
    for kw in grid:
        rs = [r for r in res if r[0] == kw]
        print(f"rl {kw['rl']:.0e} rx {kw['rx']:.0e} rk {kw['rk']:.0e}  toggles right {sum(r[2] for r in rs)}/3  free eye lifts h >= {min(r[3] for r in rs):.2f} V  shorted eye <= {max(r[4] for r in rs):.2f} V  power {np.mean([r[5] for r in rs])*1e9:.0f} nW", flush=True)
