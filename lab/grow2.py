"""grow2.py: case 2 of recruitment (QUESTIONS.md, the plan, 4): a lopsided body, a correction grown with no menu holding
the answer. B (its own tolerances, its learning as designed) and beside it D16's sequence detectors (trick.py), but:

- the gap: a drive (begun by a food sighting) that ends with the hold running out and no meal: the block lost;
  frustration, a leaky count (tau_f) of such drives;
- grow where the gap is: frustration past `nf` grows `batch` detectors (the declared primitive; up to n), each over
  the events of driving: its event a the food eye or a motor's beat, its b a motor's beat or the food eye;
- credit: the failed drive is itself a (negative, `fail`) outcome, credited through the tags as taste is, as well as
  taste (food +1, poison -2): a drive's end comes far oftener than a meal.

    python grow2.py ARM [SEEDS] [seconds=10000] [body=1] [k=v ...]   ARM: grow (fail=0: taste alone), random (D16's)
    (k: n, batch, nf, tau_f, fail, p0, eta, tau_e)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from discrete import model as M
from trick import Trick, WIN
from minimal.spec import THRUST
from units import TICK


class Grown(Trick):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        n = len(self.a)
        self.a = np.where(self.r.random(n) < 1 / 3, 0, self.r.integers(2, 4, size=n))   # food eye, or a motor
        self.b = np.where(self.r.random(n) < 1 / 3, 0, self.r.integers(2, 4, size=n))
        self.alive = np.zeros(n, bool)
        self.fr = 0.0
        self.was_driving, self.ate = False, False
        self.grew = []                                  # watching: when

    def taste(self, value, at):
        super().taste(value, at)
        self.ate = self.ate or value > 0

    def step(self):
        p = self.p
        F = self.seen[self.food]
        out = M.Model.step(self)                        # B's step, then the detectors (alive only)
        driving = self.t - self.last_drive < p["hold"]
        if driving and not self.was_driving:
            self.ate = False
        if self.was_driving and not driving and not self.ate and self.last_drive > -1e8:   # the block lost
            self.fr += 1.0
            if p.get("learn", 1):
                self.w -= p.get("eta", 0.01) * p.get("fail", 0.5) * self.tag
        self.was_driving = driving
        self.fr *= 1 - TICK / p.get("tau_f", 50.0)
        if self.fr > p.get("nf", 3.0) and not self.alive.all():   # grow
            dead = np.flatnonzero(~self.alive)[: int(p.get("batch", 20))]
            self.alive[dead] = True
            self.fr = 0.0
            self.grew.append(self.t)
        ev = np.array([F > 0, 0, 0 in out, 1 in out], float)
        self.i = (self.i + 1) % self.H
        self.hist[:, self.i] = ev
        idx = (self.i - self.lag[None, :] - np.arange(WIN)[:, None]) % self.H
        seen_a = self.hist[self.a[None, :], idx].sum(0) > 0
        fire = (ev[self.b] > 0) & seen_a & self.alive
        self.tag -= TICK / p.get("tau_e", 2.0) * self.tag
        if fire.any():
            f = np.flatnonzero(fire)
            pr = np.clip(p.get("p0", 0.01) + self.w[f], 0.0, p.get("pmax", 0.9))
            did = self.r.random(len(f)) < pr
            self.tag[f] += np.where(did, 1.0 - pr, -pr)
            if p.get("learn", 1):
                self.w[f[did]] -= p.get("eta", 0.01) * p.get("lam", 2.0) * THRUST * (1.0 - pr[did])
            out = out + [int(m) for m in self.act[f[did]]]
            self.extra += int(did.sum())
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison = job
    q = dict(M.drawn(p, spread, seed), eta=p.get("eta", 0.01), p0=p.get("p0", 0.01))
    q.update({k: v for k, v in p.items() if k in ("n", "batch", "nf", "tau_f", "fail", "tau_e", "learn", "lam")})
    lf = Life(seed, poison, brain=lambda s: (Grown if arm == "grow" else Trick)(s, q))
    f = None
    if p.get("body", 1):
        from discrete.bodies import THRUSTERS, draw, vary
        f = draw(seed, THRUSTERS)
        vary(lf, f)
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    b = lf.brain
    l.extra, l.grew = b.extra, getattr(b, "grew", [])
    l.det = (b.a, b.b, b.lag, b.act, b.w.copy(), getattr(b, "alive", np.ones(len(b.a), bool)))
    if f is not None:
        thr = {m: t for t, m in lf.motor.items()}
        l.weak = int(f[thr[0]] > f[thr[1]])             # the motor of the weaker thruster
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
    seconds = kw.pop("seconds", 10000.0)
    p, spread = M.from_bench()
    L = lives(arm, dict(p, **kw), spread, range(lo, hi), seconds)
    tag = f"g2_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items()))
    print(show(tag, summary(L)), f"extra beats per 10 s {np.mean([l.extra for l in L]) * 10 / seconds:.1f}; "
          f"detectors grown (median) {np.median([l.det[5].sum() for l in L]):.0f}", flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                        f"lab/v/{tag}.lives", "wb"))
