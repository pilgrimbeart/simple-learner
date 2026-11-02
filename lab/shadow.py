"""shadow.py: shadows that compete (QUESTIONS.md, the plan, 2; the user's idea, 2026-10-29: neural Darwinism). Many
copies of the hold, each judged counterfactually from the same experience without driving: every drive (from a food
sighting until poison or the hold running out) is replayed for each shadow hold h: its drive ends at the first gap
between sightings longer than h (the block lost: the sightings after it came only because the drive went on), so it
keeps the meals before then (a poison counts -2), less the drive's extra firings until then (the drive's beat over
the scan's), at the brain's own price of energy (its running efficiency, a leaky ratio as ctune.py's). A shadow is
judged only on drives whose hold was at least its own: drawn before the drive, so the drives judging it are a fair
sample (judging longer shadows also on drives poison ended, where they'd have run on to it too, favoured long holds:
it left out the drives where a long hold wastes its firings). Each keeps a leaky
average per gap; the hold used is the best shadow's (local competition, winner takes all), and on its own random
fifth of drives twice that, so that longer shadows are judged too.

Approximation: a drive ended early is taken to have changed nothing after it (in truth the creature would have
scanned instead, and might have seen more). Off-policy for the hold only: boredom changes what is seen next.

    python shadow.py ARM [SEEDS] [seconds=10000] [k=v ...]   ARM: shadow, holdfix (the floor with hold restored)
    (k: n, explore, N, beta)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from discrete import model as M
from selftune import BOUNDS, THRUST, REST, mistuned
from units import TICK


class Shadow(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rng = np.random.default_rng(seed + 616_161)
        self.h = np.exp(np.linspace(*np.log(BOUNDS["hold"]), int(p.get("n", 16))))
        self.avg = np.zeros(len(self.h))
        self.cnt = np.zeros(len(self.h))
        self.best = int(np.argmin(abs(np.log(self.h / p["hold"]))))
        self.used = self.h[self.best]
        self.ep, self.meals = None, []
        tr = 20.0
        self.G, self.E = 0.0, REST * tr
        self.trace, self.next_log = [], 0.0

    def taste(self, value, at):
        super().taste(value, at)
        v = 1.0 if value > 0 else -2.0 if value < 0 else 0.0
        self.G += v
        if self.ep is not None and v:
            self.meals.append((self.t, v))

    def _close(self, end, cut):
        """A drive over (its sightings self.ep, its meals): each shadow's drive replayed. A shadow's drive ends at the
        first gap between sightings longer than its hold (the block lost), so it keeps only meals before then."""
        p = self.p
        lam = max(self.G / self.E, 0.1)
        c = THRUST * (2 * p["drive"] - p["scan"])
        s = np.array(self.ep)
        gaps = np.append(np.diff(s), end - s[-1])       # after each sighting: to the next, or to the drive's end
        last = np.append(np.ones(len(s) - 1, bool), False)   # gap ends in a sighting (else in the drive's end)
        stop = np.empty(len(self.h))
        for i, h in enumerate(self.h):
            k = np.flatnonzero(last & (gaps > h))       # the first gap to a sighting it wouldn't have bridged
            stop[i] = s[k[0]] + h if len(k) else min(s[-1] + h, end)
        g = np.array([m[0] for m in self.meals]) if self.meals else np.zeros(0)
        v = np.array([m[1] for m in self.meals]) if self.meals else np.zeros(0)
        kept = (g[None, :] < stop[:, None]).astype(float) @ v if len(g) else np.zeros(len(self.h))
        inc = kept - lam * c * (stop - s[0])
        ok = self.h <= self.used + 1e-12                # (only those: which drives judge a shadow mustn't hang on how
                                                        # they went, and the hold used is drawn before the drive)
        N = p.get("N", 200.0)
        self.cnt[ok] += 1
        self.avg[ok] += (inc[ok] - self.avg[ok]) / np.minimum(self.cnt[ok], N)
        seen = self.cnt >= 20
        if seen.any():
            self.best = int(np.flatnonzero(seen)[np.argmax(self.avg[seen])])
        self.ep, self.meals = None, []

    def step(self):
        p = self.p
        F, P = self.seen[self.food], self.seen[1 - self.food]
        if F and self.t + TICK - self.last_drive >= p["hold"]:      # a new drive: its hold
            self.used = self.h[self.best] * (2.0 if self.rng.random() < p.get("explore", 0.2) else 1.0)
            p["hold"] = self.used = float(min(self.used, BOUNDS["hold"][1]))
        out = super().step()
        a = TICK / 20.0
        self.G -= a * self.G
        self.E += REST * TICK + THRUST * len(out) - a * self.E
        if self.ep is not None:
            if P:
                self._close(self.t, True)
            elif not F and self.t - self.last_drive >= p["hold"]:
                self._close(self.t, False)
        if F:
            if self.ep is None:
                self.ep = []
            self.ep.append(self.t)
        if self.t >= self.next_log:
            self.next_log += 100.0
            self.trace.append((self.t, float(self.h[self.best])))
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison = job
    d = M.drawn(p, spread, seed)
    q = mistuned(d, seed, p.get("mistune", 3.0))
    if arm == "holdfix":
        q["hold"] = d["hold"]
    q = {k: v for k, v in q.items() if k not in ("vary", "body", "mistune")}
    lf = Life(seed, poison, brain=lambda s: (Shadow if arm == "shadow" else M.Model)(s, q))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.trace = getattr(lf.brain, "trace", [])
    l.hold = (d["hold"], q["hold"])
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
    lo, hi = (int(x) for x in (args[0] if args else "50000:50016").split(":"))
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:] if "=" in a)}
    seconds = kw.pop("seconds", 10000.0)
    p, spread = M.from_bench()
    L = lives(arm, dict(p, **kw), spread, range(lo, hi), seconds)
    tag = f"s_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items()))
    print(show(tag, summary(L)), flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                        f"lab/v/{tag}.lives", "wb"))
