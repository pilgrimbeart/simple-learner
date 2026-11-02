"""bo2.py: the yardstick for self-tuning (QUESTIONS.md, the plan, 2): the best use of the brain's own information (its
meals, its food sightings, its own firings) with unlimited computation; godlike in computation, never in
information, and never a brain. Each window (W s) it runs one setting of the knobs and records the window's
efficiency; a Gaussian process (scikit-learn: a length scale per knob and the noise, fitted from the life's own
windows every `refit` windows) models efficiency over the knobs; the next setting is chosen by Thompson sampling, so it
explores while unsure and settles as it learns.

Knobs: B's five spending numbers (in the log), drawn up to `mistune` times off at birth; with body=1 each life's
thrusters drawn 0.5 to 2 (bodies.THRUSTERS) and a sixth knob, the drive's balance (log of motor 0's rate against 1's),
starting level.

    python bo2.py ARM [SEEDS] [seconds=10000] [body=0] [k=v ...]   ARM: bo, floor or ceiling
    (k: W, beta, refit, ncand, mistune)"""
import sys
import warnings
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from discrete import model as M
from selftune import KNOBS, BOUNDS, THRUST, REST, mistuned
from units import TICK

D = "/home/pilgrim/git/simple-learner/lab/v/"
BAL = 1.4                                               # the balance knob's range, +-, in the log (a 4:1 ratio)


class BO(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
        self.knobs = KNOBS + (("bal",) if p.get("tune_bal") else ())
        self.lo = np.array([np.log(BOUNDS[k][0]) if k != "bal" else -BAL for k in self.knobs])
        self.hi = np.array([np.log(BOUNDS[k][1]) if k != "bal" else BAL for k in self.knobs])
        n = len(self.knobs)
        self.gp = GaussianProcessRegressor(ConstantKernel(0.3, (1e-3, 10.0)) * RBF([0.7] * n, (0.05, 10.0))
                                           + WhiteKernel(1.0, (1e-3, 10.0)), normalize_y=True)
        self.rng = np.random.default_rng(seed + 777_777)
        self.X, self.y = [], []
        self.x = np.array([np.log(self.p[k]) if k != "bal" else 0.0 for k in self.knobs])
        self.clock, self.got, self.fired = 0.0, 0.0, 0
        self.trace = []
        self._apply()

    def _apply(self):
        for k, v in zip(self.knobs, self.x):
            if k == "bal":
                self.p["g0"], self.p["g1"] = float(np.exp(v / 2)), float(np.exp(-v / 2))
            else:
                self.p[k] = float(np.exp(v))

    def taste(self, value, at):
        super().taste(value, at)
        self.got += 1.0 if value > 0 else -2.0

    def _next(self):
        X, y = np.array(self.X), np.array(self.y)
        if len(X) < 3:                                  # a few wild tries first
            return self.lo + (self.hi - self.lo) * self.rng.random(len(self.knobs))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if len(X) % int(self.p.get("refit", 10)) == 0 or not hasattr(self.gp, "kernel_"):
                self.gp.optimizer = "fmin_l_bfgs_b"
            else:
                self.gp.kernel = self.gp.kernel_
                self.gp.optimizer = None
            self.gp.fit(X, y)
            best = X[np.argmax(self.gp.predict(X))]
            n = int(self.p.get("ncand", 300))
            cand = np.vstack([self.lo + (self.hi - self.lo) * self.rng.random((n // 2, len(self.knobs))),
                              np.clip(best + 0.2 * self.rng.standard_normal((n - n // 2, len(self.knobs))),
                                      self.lo, self.hi)])
            draw = self.gp.sample_y(cand, random_state=int(self.rng.integers(2 ** 31))).ravel()
        return cand[np.argmax(draw)]

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
            self.trace.append((self.t, dict(zip(self.knobs, map(float, self.x)))))
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison = job
    q = M.drawn(p, spread, seed)
    if arm != "ceiling":
        q = mistuned(q, seed, p.get("mistune", 3.0))
    q = {k: v for k, v in q.items() if k not in ("vary", "body", "mistune")}
    q["tune_bal"] = int(bool(p.get("body")))
    lf = Life(seed, poison, brain=lambda s: (BO if arm == "bo" else M.Model)(s, q))
    if p.get("body"):
        from discrete.bodies import THRUSTERS, draw, vary
        f = draw(seed, THRUSTERS)
        vary(lf, f)
        if arm == "ceiling":                            # told its body: the drive balanced for it (D13's oracle)
            thr = {m: t for t, m in lf.motor.items()}
            k0, k1 = f[thr[0]], f[thr[1]]
            lf.brain.p["g0"], lf.brain.p["g1"] = (k1 / k0) ** 0.5, (k0 / k1) ** 0.5
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.trace = getattr(lf.brain, "trace", [])
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
    tag = f"{arm}_body{int(kw.get('body', 0))}_{int(seconds)}" + "".join(
        f"_{k}{v:g}" for k, v in sorted(kw.items()) if k != "body")
    print(show(f"{tag} {kw}", summary(L)), flush=True)
    pickle.dump(L, open(D + f"y_{tag}.lives", "wb"))
