"""split_diag.py: what a steer does (split.py). At each steer, the nearest food block in the corridor: its offset
across (signed: + on the side steered towards), its range, and whether it is eaten within 1 s; and for B (steer=0)
at each drive beat with a food block in view, the same, by offset."""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import world
import split as SP
from units import TICK


def target(lf, fk):
    b = lf.body
    head, f = b.head(), b.forward()
    n_ = np.array([-f[1], f[0]])
    d = np.array([b.wrap(x - head) for x in b.xy])
    along, off = d @ f, -(d @ n_)                       # off: world's sign (< 0 the left, half 0)
    m = np.flatnonzero((b.kind == fk) & (along > 0) & (along < world.RANGE) & (np.abs(off) < world.EAT + world.BLOCK))
    if not len(m):
        return None
    i = int(m[np.argmin(along[m])])
    return i, off[i], along[i]


def life(job):
    from discrete import model as M
    d, seed, poison = job
    lf = SP.SplitLife(seed, poison, brain=lambda s: None)
    fc = next(c for c in lf.sensor if c != poison)
    fk = world.COLOURS.index(fc)
    p, sd = M.from_bench()
    q = M.drawn(p, sd, seed); q["V_H"] = 99.0
    br = SP.SplitB(seed, q, d); br.food = lf.sensor[fc]
    br.toward = {lf.hw[0]: lf.motor["right"], lf.hw[1]: lf.motor["left"]}
    lf.brain = br
    ev = []                                             # (t, block, off signed, range, kind)
    eaten = []                                          # (t, block index)
    orig_move = lf.body.move
    def move():
        out = orig_move()
        return out
    while lf.t < 10000:
        n0 = br.steers
        xy0 = lf.body.xy.copy()
        tg = target(lf, fk)
        lf.step()
        moved = np.flatnonzero(np.any(lf.body.xy != xy0, axis=1))   # eaten blocks reappear elsewhere
        for i in moved:
            eaten.append((lf.t, int(i)))
        if tg is not None:
            i, off, al = tg
            if br.steers > n0:
                hw = br.last_h         # wire-half steered towards
                side = -1.0 if lf.hw[0] == hw else 1.0    # world: half 0 is off < 0
                ev.append((lf.t, i, off * side, al, 1))
            elif br.t - br.last_drive < br.p["hold"] and lf.t % 5 == 0:
                ev.append((lf.t, i, abs(off), al, 0))
    out = []
    for t, i, off, al, k in ev:
        ok = any(i == j and t < te <= t + 100 for te, j in eaten)
        out.append((off, al, k, ok))
    return out


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    d = {k: (v if k == "map" else float(v)) for k, v in (x.split("=") for x in sys.argv[1].split(",") if x)}
    with ProcessPoolExecutor(7) as ex:
        R = np.array([r for L in ex.map(life, [(d, s, c) for s in range(50000, 50032) for c in ("red", "blue")]) for r in L])
    for k, name in ((1, "steers"), (0, "drive samples (|offset|)")):
        X = R[R[:, 2] == k]
        print(f"{name}: {len(X)}")
        for lo, hi in ((-2, -1), (-1, 0), (0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2.01)):
            m = (X[:, 0] * 1e3 >= lo) & (X[:, 0] * 1e3 < hi)
            if m.sum():
                rng = X[m, 1] * 1e3
                print(f"  offset {lo:+.1f}..{hi:+.1f} mm: {m.sum():5d}, eaten within 1 s {X[m, 3].mean():.0%}, range median {np.median(rng):.1f} mm")
