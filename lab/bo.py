"""bo.py: the yardstick for self-tuning B's spending (QUESTIONS.md, the plan, 2): the best use of the brain's own
information (its meals, its food sightings, its own firings), with unlimited computation. Each window (W s) it runs
one setting of the five knobs and records the window's efficiency; a Gaussian process over the knobs (in the log, a
length scale per knob) models efficiency from every window so far; the next setting is chosen by Thompson sampling
(a draw from the posterior over candidate settings, its best taken), so it explores while unsure and settles as it
learns. Godlike in computation, not in information: a yardstick, never a brain.

    python bo.py [SEEDS] [seconds=10000] [mistune=3] [k=v ...]   (k: W, ell, sf, sn, beta, ncand)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from discrete import model as M
from selftune import KNOBS, BOUNDS, THRUST, REST, mistuned
from units import TICK

LO = np.log([BOUNDS[k][0] for k in KNOBS])
HI = np.log([BOUNDS[k][1] for k in KNOBS])


def kernel(a, b, ell, sf):
    d = (a[:, None, :] - b[None, :, :]) / ell
    return sf ** 2 * np.exp(-0.5 * (d ** 2).sum(-1))


class BO(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rng = np.random.default_rng(seed + 777_777)
        self.X, self.y = [], []
        self.x = np.log([self.p[k] for k in KNOBS])     # the setting now (log)
        self.clock, self.got, self.fired = 0.0, 0.0, 0
        self.trace = []
        self._apply()

    def _apply(self):
        for k, v in zip(KNOBS, self.x):
            self.p[k] = float(np.exp(v))

    def taste(self, value, at):
        super().taste(value, at)
        self.got += 1.0 if value > 0 else -2.0

    def _next(self):
        p = self.p
        X, y = np.array(self.X), np.array(self.y)
        ell = p.get("ell", 0.5) * np.ones(len(KNOBS))
        sf, sn = p.get("sf", 0.5), p.get("sn", 1.0)
        mu = y.mean()
        n = int(p.get("ncand", 400))
        best = X[np.argmax(self._post_mean(X, X, y - mu, ell, sf, sn))]
        cand = np.vstack([LO + (HI - LO) * self.rng.random((n // 2, len(KNOBS))),   # anywhere, and near the best
                          np.clip(best + 0.2 * self.rng.standard_normal((n - n // 2, len(KNOBS))), LO, HI)])
        K = kernel(X, X, ell, sf) + sn ** 2 * np.eye(len(X))
        L = np.linalg.cholesky(K)
        Ks = kernel(cand, X, ell, sf)
        a = np.linalg.solve(L.T, np.linalg.solve(L, y - mu))
        m = Ks @ a
        v = np.linalg.solve(L, Ks.T)
        C = kernel(cand, cand, ell, sf) - v.T @ v + 1e-9 * np.eye(n)
        w, U = np.linalg.eigh(C)
        draw = m + U @ (np.sqrt(np.maximum(w, 0)) * self.rng.standard_normal(n))
        return cand[np.argmax(draw)]

    @staticmethod
    def _post_mean(Xs, X, yc, ell, sf, sn):
        K = kernel(X, X, ell, sf) + sn ** 2 * np.eye(len(X))
        return kernel(Xs, X, ell, sf) @ np.linalg.solve(K, yc)

    def step(self):
        self.got += self.p.get("beta", 0.0) * self.seen[self.food]
        out = super().step()
        self.fired += len(out)
        self.clock += TICK
        W = self.p.get("W", 40.0)
        if self.clock >= W:
            self.X.append(self.x.copy())
            self.y.append(self.got / (REST * W + THRUST * self.fired))
            self.clock, self.got, self.fired = 0.0, 0.0, 0
            self.x = self._next()
            self._apply()
            self.trace.append((self.t, {k: float(np.exp(v)) for k, v in zip(KNOBS, self.x)}))
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    p, spread, seed, seconds, poison = job
    q = M.drawn(p, spread, seed) if p.get("vary", 1) else dict(p)
    if p.get("mistune", 1) > 1:
        q = mistuned(q, seed, p["mistune"])
    q = {k: v for k, v in q.items() if k not in ("vary", "body", "mistune")}
    lf = Life(seed, poison, brain=lambda s: BO(s, q))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.trace = lf.brain.trace
    l.start = {k: q[k] for k in KNOBS}
    return l


def lives(p, spread, seeds, seconds, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(life, [(p, spread, s, seconds, c) for s in seeds for c in ("red", "blue")]))


if __name__ == "__main__":
    import pickle
    from minimal.spec import summary
    from discrete.poison import show
    args = [a for a in sys.argv[1:] if "=" not in a]
    lo, hi = (int(x) for x in (args[0] if args else "50000:50016").split(":"))
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
    seconds = kw.pop("seconds", 10000.0)
    p, spread = M.from_bench()
    L = lives(dict(p, mistune=kw.pop("mistune", 3.0), **kw), spread, range(lo, hi), seconds)
    print(show(f"Bayesian optimiser {kw}", summary(L)), flush=True)
    pickle.dump(L, open("/home/pilgrim/git/simple-learner/"
                        "lab/v/tune_bo.lives", "wb"))
