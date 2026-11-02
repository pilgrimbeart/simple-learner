"""seer2.py: the yardstick (QUESTIONS.md, step 3, the bounds; the user, 2026-11-01): the seer (seer.py) told each
block's place only as well as its pulses could tell it, to see how fast its 4.5 falls towards B's 2.54. Still told
its pose and which colour is food (generous: perfect path integration, the colour learned).

A pulse says only that the nearest block of its colour lies in the corridor ahead (its range unknown, its offset
across within the corridor). Each pulse gives an estimate of the block's place: its range off by a factor
exp(N(0, rerr)) (rerr=inf: drawn evenly along the corridor, a single pulse's knowledge), its offset across exact or
(lat=1) drawn evenly across the corridor; with avg=1 the estimates of one block are averaged (evidence accumulating
over its pulses), else the first is kept. Reaching an estimate without eating drops it (the creature can see it
again). An eaten block is forgotten (it tasted it)."""
import sys, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import world
from seer import Seer


class Seer2(Seer):
    def __init__(self, lf, poison, food_sensor, rerr=0.0, lat=0.0, avg=1.0, seed=0, **p):
        super().__init__(lf, poison, food_sensor, **p)
        self.rerr, self.lat, self.avg = rerr, lat, avg
        self.r = np.random.default_rng(seed + 4242)
        self.est = {}                                   # block index -> [its place when seen, sum of estimates, n]

    def target(self):
        b = self.lf.body
        head, f = b.head(), b.forward()
        n_ = np.array([-f[1], f[0]])
        d = np.array([b.wrap(p - head) for p in b.xy])
        along = d @ f
        off = d @ n_
        for s in (0, 1):
            if self.n[s]:
                k = self.colour_of[s]
                m = np.flatnonzero((b.kind == k) & (along > 0) & (along < world.RANGE) & (np.abs(off) < world.EAT + world.BLOCK))
                if len(m):
                    i = int(m[np.argmin(along[m])])
                    for _ in range(self.n[s]):
                        if math.isinf(self.rerr):
                            r = self.r.uniform(0.0, world.RANGE)
                        else:
                            r = along[i] * math.exp(self.r.normal(0.0, self.rerr))
                        W = world.EAT + world.BLOCK
                        if self.lat == 0.5:             # lat=0.5: a split eye: which half, not where within it
                            o = np.sign(off[i]) * self.r.uniform(0, 1) * W
                        elif self.lat == 0.25:          # lat=0.25: four strips across
                            q = min(int((off[i] + W) / (W / 2)), 3)
                            o = -W + (q + self.r.uniform(0, 1)) * W / 2
                        else:
                            o = self.r.uniform(-1, 1) * W if self.lat else off[i]
                        e = head + r * f + o * n_
                        if i in self.est and np.allclose(self.est[i][0], b.xy[i]):
                            if self.avg:        # averaged in the world frame (wrapped near the first estimate)
                                first = self.est[i][1] / self.est[i][2]
                                self.est[i][1] += first + b.wrap(e - first)
                                self.est[i][2] += 1
                        else:
                            self.est[i] = [b.xy[i].copy(), e, 1]
        self.n = [0, 0]
        for i in list(self.est):                        # eaten (moved elsewhere): forgotten
            if not np.allclose(self.est[i][0], b.xy[i]):
                del self.est[i]
        bad = world.COLOURS.index(self.poison)
        foods, poisons = [], []
        for i, (_, s, n) in self.est.items():
            dd = b.wrap(s / n - head)
            if np.hypot(*dd) < world.EAT:               # reached the estimate, and nothing eaten: dropped below
                continue
            (poisons if b.kind[i] == bad else foods).append(dd)
        self.est = {i: v for i, v in self.est.items() if np.hypot(*b.wrap(v[1] / v[2] - head)) >= world.EAT}
        best = None
        for dd in sorted(foods, key=lambda q: np.hypot(*q)):
            L = np.hypot(*dd); u = dd / max(L, 1e-9)
            if all(not (0 < q @ u < L and abs(q[0] * u[1] - q[1] * u[0]) < self.clear) for q in poisons):
                best = (dd, L); break
        return best


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    p, seed, poison = job
    lf = Life(seed, poison, brain=lambda s: None)
    lf.brain = Seer2(lf, poison, lf.sensor[next(c for c in lf.sensor if c != poison)], seed=seed, **p)
    while lf.t < 10000:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, 10000, poison))
    l.power, l.firings = 0.0, SPAN * len(lf.firings) / 100.0
    return l


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from minimal.spec import summary
    from discrete.poison import show
    with ProcessPoolExecutor(4) as ex:
        for a in sys.argv[1:]:
            p = {k: float(v) for k, v in (x.split("=") for x in a.split(",") if x)}
            L = list(ex.map(life, [(p, s, c) for s in range(50000, 50064) for c in ("red", "blue")]))
            print(show(f"seer2 {p}", summary(L)), flush=True)
