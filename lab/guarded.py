"""guarded.py: a world where food is often guarded (QUESTIONS.md, the plan, 4; the user's idea, 2026-10-30): each food
block, with probability g, has a poison block beside it, `d` from its centre at a random angle, moving with it when it
is eaten and re-placed beside it at a new angle when itself eaten. The rays stop at the first block, so a food block
is hidden behind its guard when approached from the guard's side. Still a random world: one statistic changed.

    python guarded.py ARM [SEEDS] [seconds=100] [g=1] [d=2.5] [k=v ...]   ARM: B (the fast model of B), told (B told the colour)"""
import math
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import world as W
from discrete import model as M
from units import MILLI, TICK


class Guarded(W.Body):
    def __init__(self, rng, poison, g=1.0, d=2.5 * MILLI):
        super().__init__(rng)
        self.p_kind = W.COLOURS.index(poison)
        self.d = d
        food = np.flatnonzero(self.kind != self.p_kind)
        guards = np.flatnonzero(self.kind == self.p_kind)
        self.guard = {}                                 # food block -> its guard
        for f, q in zip(food, guards):
            if rng.random() < g:
                self.guard[int(f)] = int(q)
        self.of = {q: f for f, q in self.guard.items()}
        for f, q in self.guard.items():
            self._beside(f, q)

    def _beside(self, f, q):
        a = self.rng.uniform(0, 2 * math.pi)
        self.xy[q] = (self.xy[f] + self.d * np.array([math.cos(a), math.sin(a)])) % W.WORLD

    def move(self):
        h0 = self.head()
        before = self.xy.copy()
        out = super().move()
        moved = np.flatnonzero((self.xy != before).any(axis=1))
        for b in moved:                                 # (eaten, re-placed by super)
            b = int(b)
            if b in self.guard:
                self._beside(b, self.guard[b])
            elif b in self.of:
                self._beside(self.of[b], b)
        return out


class Detour(M.Model):
    """B told the colour, with one memory more (scripted, to certify the world): poison seen within `win` s of food
    starts a detour instead of ending the drive: motor `m` alone at the drive's rate for ta s (swing away), both for tb
    s (pass the guard), the other alone for tc s (swing back), then B again, the food in view or not."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.det = None                                 # when the detour began

    def step(self):
        p = self.p
        F, P = self.seen[self.food], self.seen[1 - self.food]
        if self.det is None and P and self.t - self.last_food < p.get("win", 0.3):
            self.det = self.t
        if self.det is not None:
            s = self.t - self.det
            ta, tb, tc = p.get("ta", 0.1), p.get("tb", 0.2), p.get("tc", 0.1)
            if s >= ta + tb + tc:
                self.det = None
            else:
                self.seen = [0, 0]
                self.t += TICK
                self.phase += p["drive"] * TICK
                beats = int(self.phase)
                self.phase -= beats
                m = int(p.get("m", 0))
                if s < ta:
                    return [m] * beats
                if s < ta + tb:
                    return [0, 1] * beats
                return [1 - m] * beats
        return super().step()


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison = job
    q = M.drawn(p, spread, seed)
    q = {k: v for k, v in q.items() if k not in ("g", "d")}
    q.update({k: p[k] for k in ("win", "ta", "tb", "tc", "m") if k in p})
    lf = Life(seed, poison, brain=lambda s: (Detour if arm == "detour" else M.Model)(s, q))
    if arm in ("told", "detour"):                                   # told which colour is food, learning off (D13's ceiling)
        lf.brain.food = lf.sensor[[c for c in W.COLOURS if c != poison][0]]
        lf.brain.p["step"] = 0.0
    if p.get("g", 1.0) > 0 and poison is not None:
        lf.body = Guarded(np.random.default_rng(seed + 4_040_404), poison, p.get("g", 1.0), p.get("d", 2.5) * MILLI)
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.flips = len(lf.brain.flips)
    return l


def lives(arm, p, spread, seeds, seconds, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(life, [(arm, p, spread, s, seconds, c) for s in seeds for c in ("red", "blue")]))


if __name__ == "__main__":
    import pickle
    from minimal.spec import summary
    from discrete.poison import show
    arm = sys.argv[1]
    args = [a for a in sys.argv[2:] if "=" not in a]
    lo, hi = (int(x) for x in (args[0] if args else "50000:50032").split(":"))
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:] if "=" in a)}
    seconds = kw.pop("seconds", 100.0)
    p, spread = M.from_bench()
    L = lives(arm, dict(p, **kw), spread, range(lo, hi), seconds)
    tag = f"w_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items()))
    print(show(tag, summary(L)), flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                        f"lab/v/{tag}.lives", "wb"))
