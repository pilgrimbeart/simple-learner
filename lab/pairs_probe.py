"""pairs_probe.py: what happens at a touching pair (lab/pairs.py, D40): each drive that a poison pulse ends, taken apart. Watching only.
The told arm (so only driving is seen), gap 2 mm.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/pairs_probe.py [GAP mm] [SEEDS]"""
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import pairs as PR
import stage3_random as R


def frame(lf, b):
    """Block b in the creature's frame, from its mouth: (ahead, across), m."""
    B = lf.body
    w = lf.WORLD
    h = B.head_xy()
    d = (B.xy[b] - h + w / 2) % w - w / 2
    c, s = math.cos(B.heading), math.sin(B.heading)
    return d[0] * c + d[1] * s, -d[0] * s + d[1] * c


def life(gap, seed, first, secs=100.0):
    from stage2_lang import arms as S
    lf = S.make(S.world_of(PR.world(gap)), "vtold", seed, first, seconds=True)
    lf2 = lf
    from stage2_lang.seconds import seconds_cls
    b = lf.brain
    n = lf.body.n // 2
    ev, was, pend = [], False, []
    ticks = int(round(secs / lf.dt))
    eaten_at = {}
    while lf.t < ticks:
        pos0 = lf.body.xy.copy()
        lf.step()
        now = lf.t * lf.dt
        moved = np.where(np.abs(lf.body.xy - pos0).sum(1) > 1e-12)[0]
        for m in moved:
            eaten_at[int(m)] = now
        driving = b.t - b.last_drive < b.p["hold"]
        if was and b.last_drive < -1e8:                 # a poison pulse ended the drive
            fk = [k for k in range(2) if lf.wire_s[k] == b.food][0]
            best = None
            for i in range(lf.body.n):
                if lf.body.kind[i] != fk:
                    continue
                a, y = frame(lf, i)
                if 0 < a < 0.016 and abs(y) < 0.003 and (best is None or a < best[1]):
                    best = (i, a, y)
            if best:
                i, a, y = best
                pa, py = frame(lf, (i + n) % (2 * n))
                ev.append(dict(t=now, i=i, a=a, y=y, pa=pa, py=py))
        was = driving
    for e in ev:
        t2 = eaten_at.get(e["i"])
        e["got"] = False
    return ev, lf


if __name__ == "__main__":
    R._init(0.0025, False)
    a = sys.argv[1:]
    gap = float(a[0]) if a else 2.0
    seeds = [int(x) for x in a[1].split(",")] if len(a) > 1 else range(85000, 85005)
    E = []
    for s in seeds:
        for c in ("red", "blue"):
            ev, lf = life(gap, s, c)
            E += ev
    n = 2 * len(list(seeds))
    A = np.array([(e["a"], e["y"], e["pa"], e["py"]) for e in E]) * 1000
    print(f"gap {gap} mm, {n} lives: {len(E) / n:.1f} drives a life ended by a poison pulse with food ahead")
    print(f"  the food then: ahead median {np.median(A[:, 0]):.1f} mm (quartiles {np.percentile(A[:, 0], 25):.1f}, {np.percentile(A[:, 0], 75):.1f}); across |y| median {np.median(np.abs(A[:, 1])):.2f} mm; in the mouth's path (|y| < 1): {(np.abs(A[:, 1]) < 1).mean():.2f}")
    inpath = np.abs(A[:, 3]) < 1
    print(f"  its partner: in the mouth's path (|y| < 1) {inpath.mean():.2f}; beside it, seen only (1 to 2 mm) {((np.abs(A[:, 3]) >= 1) & (np.abs(A[:, 3]) < 2)).mean():.2f}; out of the corridor's sight {(np.abs(A[:, 3]) >= 2).mean():.2f}")
    print(f"  partner nearer than the food {(A[:, 2] < A[:, 0]).mean():.2f}; partner in path and nearer {(inpath & (A[:, 2] < A[:, 0])).mean():.2f}; in path and behind {(inpath & (A[:, 2] >= A[:, 0])).mean():.2f}")
    both = (np.abs(A[:, 1]) < 1) & ~inpath
    print(f"  food in the path and partner not (a drive that would have eaten clean): {both.mean():.2f}")
