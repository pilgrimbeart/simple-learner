"""grow_pursuit.py: pursuit grown (QUESTIONS.md, the plan, 4, candidate a, on the disc body). Every robot the tracker
with the escape grower (grow_escape.Grower, its defaults), as pursuit.py's; half also grow a second recruit on the
taste's pathway, the same kind as escape's knob recruit but triggered the other way: a good taste ending (a bite lost)
is frustration (tau_f, nf); grown, at each bite's end it fires motor k at rate * sigmoid(w_k + e_k) for dur s, its
beats added to the brain's own, e_k its own noise (sd_k) drawn afresh each time; the taste of the next win s (+ while
biting, - while bitten) against its running mean (tau_b) moves each knob by eta (outcome - mean) e_k. Escape's firing
takes precedence. It isn't told what it is for: the same recruit as escape's, on a different change of taste.

    python grow_pursuit.py [SEEDS] [w0=-2] [eta=3] [sd_k=2] [win=1] [dur=0.5] [rate=50] [seconds=300]
    paired by arena: the growers' net (eaten - lost) minus the plain escape growers'"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import arena as AR
import grow_escape as G
from units import TICK

PG = {}


class PGrower(G.Grower):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.good_now = self.biting = False
        self.ended, self.fr2, self.grew2 = -1e9, 0.0, None
        self.w = np.full(2, PG.get("w0", -2.0))
        self.e, self.b, self.pend, self.got2 = np.zeros(2), None, None, 0.0
        self.kph = np.zeros(2)
        self.prng = np.random.default_rng(seed + 9_191_919)
        self.ends = 0

    def taste(self, value, at):
        super().taste(value, at)
        if value > 0:
            self.good_now = True
        if self.pend is not None:
            self.got2 += value

    def step(self):
        q = PG
        if self.biting and not self.good_now:           # a bite just ended
            self.ended = self.t
            self.ends += 1
            self.fr2 += 1.0
            if self.grew2 is not None and self.pend is None:
                self.e = q.get("sd_k", 2.0) * self.prng.standard_normal(2)
                self.pend, self.got2 = self.t, 0.0
        self.biting, self.good_now = self.good_now, False
        self.fr2 *= 1 - TICK / q.get("tau_f", 50.0)
        if self.grew2 is None and self.fr2 > q.get("nf", 2.0):
            self.grew2 = self.t
        out = super().step()
        win = q.get("win", 1.0)
        if self.pend is not None and self.t - self.pend >= win:
            x = self.got2 * TICK / win
            if self.b is None:
                self.b = x
            self.w += q.get("eta", 3.0) * (x - self.b) * self.e
            self.b += (x - self.b) / q.get("tau_b", 10.0)
            self.pend = None
        escaping = self.op != "none" and self.t - self.last_pain < G.GROW.get("dur", 0.5)
        if self.grew2 is not None and not escaping and self.t - self.ended < q.get("dur", 0.5):
            self.kph += q.get("rate", 50.0) / (1 + np.exp(-(self.w + self.e))) * TICK
            k = self.kph.astype(int)
            self.kph -= k
            return out + [0] * int(k[0]) + [1] * int(k[1])
        return out


_init = AR.Robot.__init__                               # (grow_escape's: makes "grow")


def _robot(self, rng, seed, p, spread, t, kind="B"):
    _init(self, rng, seed, p, spread, t, "grow" if kind == "pgrow" else kind)
    if kind == "pgrow":
        food = self.brain.food
        self.brain = PGrower(seed, dict(self.brain.p))
        self.brain.food = food
        self.kind = "pgrow"


AR.Robot.__init__ = _robot


def run(job):
    seed, seconds, kw = job
    PG.update(kw)
    A = AR.Arena(seed, 10, ("pgrow", "grow"))
    for _ in range(int(seconds / TICK)):
        A.step()
    out = []
    for r, d in [(r, A.t) for r in A.robots] + A.dead:
        age = d - r.born
        if age >= 20:
            b = r.brain
            f = 1 / (1 + np.exp(-b.w)) if r.kind == "pgrow" else np.zeros(2)
            out.append((r.kind, r.ate / age * 10, (r.lost + AR.THRUST * r.firings) / age * 10, age, getattr(b, "grew2", None), f[0], f[1]))
    return out


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    args = [a for a in sys.argv[1:] if "=" not in a]
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
    seconds = kw.pop("seconds", 300.0)
    seeds = range(*(int(x) for x in (args[0] if args else "0:16").split(":")))
    with ProcessPoolExecutor() as ex:
        res = list(ex.map(run, [(s, seconds, kw) for s in seeds]))
    net = lambda r, k: np.mean([x[1] - x[2] for x in r if x[0] == k])
    d = np.array([net(r, "pgrow") - net(r, "grow") for r in res])
    boot = [d[np.random.default_rng(i).integers(len(d), size=len(d))].mean() for i in range(2000)]
    rows = [x for r in res for x in r]
    for k in ("pgrow", "grow"):
        x = [r for r in rows if r[0] == k]
        print(f"{k:8s}: {len(x)} robots, ate {np.mean([r[1] for r in x]):.3f}, lost {np.mean([r[2] for r in x]):.3f} a 10 s, "
              f"age {np.mean([r[3] for r in x]):.0f} s", flush=True)
    g = [r for r in rows if r[0] == "pgrow"]
    both = sum(r[5] > 0.5 and r[6] > 0.5 for r in g)
    print(f"  grew in {sum(r[4] is not None for r in g)} of {len(g)}; ending with both motors above half rate in {both}, "
          f"mean rates {np.mean([r[5] for r in g]):.2f} / {np.mean([r[6] for r in g]):.2f} of full")
    print(f"{kw}: net, pursuit grower - escape grower {d.mean():+.3f} [{np.percentile(boot, 2.5):+.3f}, {np.percentile(boot, 97.5):+.3f}]", flush=True)
