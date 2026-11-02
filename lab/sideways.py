"""sideways.py: does a brain sense across? For each first food pulse from a block, the block's offset across the eyes'
corridor, and whether the creature eats that block within 1 s. Steering by when pulses come would eat off-centre
blocks nearly as often as centred ones; driving straight eats only those within the mouth's 1 mm.

    python sideways.py b | ctrnn FILE [which]
"""
import json, sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import world
from units import TICK

BINS = [0, 0.5e-3, 1e-3, 1.5e-3, 2e-3]


def life(job):
    from creature import Life
    kind, arg, seed, poison = job
    lf = Life(seed, poison, brain=lambda s: None)
    food = lf.sensor[next(c for c in lf.sensor if c != poison)]
    if kind == "b":
        from discrete import model as M
        p, sd = M.from_bench()
        q = M.drawn(p, sd, seed)
        q["V_H"] = 99.0                                  # told the colour: the bit never flips
        br = M.Model(seed, q)
        br.food = food
    else:
        import ctrnn
        d = json.load(open(arg[0]))
        br = ctrnn.Net(seed, d[arg[1]], d["n"], food)
    lf.brain = br
    fk = world.COLOURS.index(next(c for c in lf.sensor if c != poison))
    watch = {}                                           # block -> (offset, tick seen, its place)
    out = []
    orig = br.stimulate

    def stim(sensor, at):
        orig(sensor, at)
        if sensor != food:
            return
        b = lf.body
        head, f = b.head(), b.forward()
        n_ = np.array([-f[1], f[0]])
        d = np.array([b.wrap(p - head) for p in b.xy])
        along, off = d @ f, d @ n_
        m = np.flatnonzero((b.kind == fk) & (along > 0) & (along < world.RANGE) & (np.abs(off) < world.EAT + world.BLOCK))
        if len(m):
            i = int(m[np.argmin(along[m])])
            if i not in watch:
                watch[i] = (abs(off[i]), along[i], lf.t, lf.body.xy[i].copy())
    br.stimulate = stim
    while lf.t < 10000:
        lf.step()
        for i in list(watch):
            o, a, t0, xy = watch[i]
            if not np.allclose(lf.body.xy[i], xy):
                out.append((o, a, 1)); del watch[i]
            elif lf.t - t0 > 1.0 / TICK:
                out.append((o, a, 0)); del watch[i]
    return out


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    kind = sys.argv[1]
    arg = (sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "best") if kind == "ctrnn" else None
    with ProcessPoolExecutor(1) as ex:
        R = [r for L in ex.map(life, [(kind, arg, s, c) for s in range(50000, 50032) for c in ("red", "blue")]) for r in L]
    R = np.array(R)
    print(kind, arg, f"{len(R)} sightings")
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        k = (R[:, 0] >= lo) & (R[:, 0] < hi)
        near = k & (R[:, 1] < 7.5e-3)
        print(f"  offset {lo*1e3:.1f}-{hi*1e3:.1f} mm: eaten within 1 s {R[k, 2].mean():.0%} of {k.sum()}"
              f"   (seen nearer than 7.5 mm: {R[near, 2].mean():.0%} of {near.sum()})")
