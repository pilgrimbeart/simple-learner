"""story2_mirror.py: does the lopsided error curve come from the scan's direction? The scan on motor 1 instead of motor 0:
the curve should flip. x1.25, seeds 51000-51063 x 2 (lab/story2_stage3.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from discrete import model as M
from discrete.bodies import vary
from minimal.spec import SPAN, Lived, thirds, efficiency
from story1 import RunLimit
from story2 import factors, paired
from units import TICK


class Mirror(RunLimit, M.Model):
    def step(self):
        driving = None
        out = super().step()
        if out and all(m == 0 for m in out):            # a scan's beats, on the other motor
            if self.t - self.last_drive >= self.p["hold"] and self.t - self.last_food <= self.p["bored"]:
                return [1] * len(out)
        return out


def life(job):
    e, seed, poison = job
    p, spread = M.from_bench()
    q = dict(M.drawn(p, spread, seed), run_max=1.0, sync=1, V_H=99.0)
    lf = Life(seed, poison, brain=lambda s: Mirror(s, q))
    b = lf.brain
    b.food = 1 - lf.sensor[poison]
    f = factors(seed, 1.25, False)
    vary(lf, f)
    thr = {m: t for t, m in lf.motor.items()}
    x = float(np.log(f[thr[1]] / f[thr[0]])) + e
    b.p["g0"], b.p["g1"] = float(np.exp(x / 2)), float(np.exp(-x / 2))
    b.p["scan"] = q["scan"]
    while lf.t < 10000:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, 10000, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / 100.0, "silicon"
    return l


def run(e):
    with ProcessPoolExecutor(8) as ex:
        return list(ex.map(life, [(e, s, c) for s in range(51000, 51064) for c in ("red", "blue")], chunksize=4))


ref = run(0.0)
print(f"scan on motor 1, x1.25: error 0: {efficiency(ref):.2f}", flush=True)
for e in (-0.2, -0.1, -0.05, 0.05, 0.1, 0.2):
    L = run(e)
    d, i = paired(L, ref)
    print(f"  error {e:+.2f}: {efficiency(L):.2f}, against none {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
