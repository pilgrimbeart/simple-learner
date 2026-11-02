"""drivebal.py: the plan's step 5, a first experiment (QUESTIONS.md): a lopsided body's balance learned from every drive,
not from meals. B (its own tolerances, its learning as designed) on bodies with each thruster 0.5 to 2
(bodies.THRUSTERS); the drive's balance x (log of motor 0's rate over motor 1's) jittered afresh at each drive's start
by e (sd); the drive's outcome, the food pulses seen during it (a drive lasts while the block stays in view, so a drive
that curves off loses it sooner), against its running mean (tau_b drives), moves x by eta (outcome - mean) e (node
perturbation, as grow_escape.py's knobs; the escape's lesson: judge each try at once, against its own jitter).

    python drivebal.py ARM [SEEDS] [seconds=2000] [k=v ...]
    ARM: learn, fixed (balance 0: the floor), oracle (told its body: model.life's oracle 1, the ceiling)
    (k: eta, sd, tau_b, out: pulses | length, anti=1: paired opposite jitters, N: the jitter's sd / sqrt(1 + drives / N), rel=1: outcomes relative; x0o=1: born at the oracle's balance, a diagnostic)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from units import TICK


class DriveBal(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rng = np.random.default_rng(seed + 616_161)
        self.x, self.e, self.b = 0.0, 0.0, None
        self.was_driving, self.pulses, self.start = False, 0, 0.0
        self.drives = 0
        self.trace = []                                 # watching: (t, x) each 100 s

    def _set(self, v):
        self.p["g0"], self.p["g1"] = float(np.exp(v / 2)), float(np.exp(-v / 2))

    def step(self):
        p = self.p
        F = self.seen[self.food]
        out = super().step()
        driving = self.t - self.last_drive < p["hold"]
        if driving and not self.was_driving:            # a drive begins: its own jitter
            if p.get("anti") and self.drives % 2 == 1:   # anti=1: the next drive's jitter the last one's opposite
                self.e = -self.e
            else:
                sd = p.get("sd", 0.3) / np.sqrt(1 + self.drives / p.get("N", 1e12))   # N: jitter shrinking with drives
                self.e = sd * self.rng.standard_normal()
            self.pulses, self.start = 0, self.t
            self._set(self.x + self.e)
        if driving:
            self.pulses += F
        if self.was_driving and not driving:            # it ends: judge it
            y = self.pulses if p.get("out", 0) == 0 else self.t - self.start
            if self.b is None:
                self.b = y
            d = (y - self.b) / max(self.b, 1.0) if p.get("rel") else y - self.b   # rel=1: against its own usual
            self.x = float(np.clip(self.x + p.get("eta", 0.01) * d * self.e, -1.4, 1.4))
            self.b += (y - self.b) / p.get("tau_b", 20.0)
            self.drives += 1
            self._set(self.x)
        self.was_driving = driving
        if not self.trace or self.t - self.trace[-1][0] >= 100.0:
            self.trace.append((self.t, self.x))
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    from discrete.bodies import THRUSTERS, draw, vary
    arm, p, spread, seed, seconds, poison = job
    if arm in ("fixed", "oracle"):
        return M.life((dict(p, body=1, oracle=1 if arm == "oracle" else 0), spread, seed, seconds, poison))
    q = dict(M.drawn(p, spread, seed), **{k: p[k] for k in ("eta", "sd", "tau_b", "out", "anti", "rel", "N") if k in p})
    lf = Life(seed, poison, brain=lambda s: DriveBal(s, q))
    f = draw(seed, THRUSTERS)
    vary(lf, f)
    thr = {m: t for t, m in lf.motor.items()}
    if p.get("x0o"):                                    # (diagnostic: born at the oracle's balance)
        lf.brain.x = float(np.log(f[thr[1]] / f[thr[0]]))
        lf.brain._set(lf.brain.x)
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.right = 0.5 * np.log(f[thr[1]] / f[thr[0]]) * 2   # the oracle's x: log(g0/g1) = log(k1/k0)
    l.x, l.drives, l.trace = lf.brain.x, lf.brain.drives, lf.brain.trace
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
    lo, hi = (int(x) for x in (args[0] if args else "0:32").split(":"))
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:] if "=" in a)}
    seconds = kw.pop("seconds", 2000.0)
    p, spread = M.from_bench()
    L = lives(arm, dict(p, **kw), spread, range(lo, hi), seconds)
    tag = f"db_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items())) + f"_{lo}-{hi}"
    extra = ""
    if arm == "learn":
        x = np.array([l.x for l in L]); r = np.array([l.right for l in L])
        extra = (f"  balance vs the oracle's: correlation {np.corrcoef(x, r)[0, 1]:.2f}, slope {np.polyfit(r, x, 1)[0]:.2f};"
                 f" drives per 10 s {np.mean([l.drives for l in L]) * 10 / seconds:.1f}")
    print(show(tag, summary(L)) + extra, flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/lab/v/{tag}.lives", "wb"))
