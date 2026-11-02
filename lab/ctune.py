"""ctune.py: the local tuner without a coordinator (QUESTIONS.md, the plan, 2; D15): continuous-time node perturbation
(Fiete and Seung, 2006). No epochs, no shared clock, no accountant holding halves:

- each knob wiggles at its own random moments (on average every `wig` s) to a new random offset of +-delta;
- one outcome node: a leaky tally of what taste brings (food 1, poison -2, food sightings beta each) over a leaky
  tally of what is spent (resting and the brain's own firings), both with time constant tau_r: an efficiency rate;
- its own slower average (tau_b); the difference ("better than usual") is broadcast;
- each knob keeps a trace of its own offset (tau_r, so it matches what the outcome remembers) and moves along it by
  eta x broadcast x trace (every 0.1 s).

Annealing (anneal=T s): wiggles start wild (1 + `wild` times delta) and calm with a leaky "youth" node of the brain's
own (time constant T); an imperfect internal clock of development, not a reference from the body.

    python ctune.py [SEEDS] [seconds=10000] [body=0] [k=v ...]   (k: delta, eta, wig, tau_r, tau_b, beta, anneal, wild)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from discrete import model as M
from selftune import KNOBS, BOUNDS, THRUST, REST, mistuned
from units import TICK

LOG = dict(bal=(-1.4, 1.4))


def _log(k):
    return LOG[k] if k in LOG else tuple(np.log(BOUNDS[k]))


class CTuned(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rng = np.random.default_rng(seed + 525_252)
        self.knobs = ("hold",) if p.get("hold_only") else KNOBS + (("bal",) if p.get("tune_bal") else ())
        self.x = {k: np.log(self.p[k]) if k != "bal" else 0.0 for k in self.knobs}
        self.off = {k: 0.0 for k in self.knobs}         # each knob's own wiggle now
        self.tr = {k: 0.0 for k in self.knobs}          # and its trace
        self.G, self.E = 0.0, REST * p.get("tau_r", 20.0)   # outcome node: leaky gain and leaky spending
        self.base = None                                # its slower average
        self.youth = 1.0
        self.slow = 0
        self.when = {k: self.rng.exponential(p.get("wig", 20.0)) for k in self.knobs}
        self.got = 0.0
        self.trace = []
        self.next_log = 0.0
        self._set()

    def _set(self):
        for k in self.knobs:
            v = float(np.clip(self.x[k] + self.off[k], *_log(k)))
            if k == "bal":
                self.p["g0"], self.p["g1"] = float(np.exp(v / 2)), float(np.exp(-v / 2))
            else:
                self.p[k] = float(np.exp(v))

    def taste(self, value, at):
        super().taste(value, at)
        self.got += 1.0 if value > 0 else -2.0

    def step(self):
        p = self.p
        self.got += p.get("beta", 0.02) * self.seen[self.food]
        out = super().step()
        if not p.get("tune", 1):
            return out
        tr, tb = p.get("tau_r", 20.0), p.get("tau_b", 200.0)
        a = TICK / tr
        self.G += self.got - a * self.G
        self.E += REST * TICK + THRUST * len(out) - a * self.E
        self.got = 0.0
        R = self.G / self.E
        self.base = R if self.base is None else self.base + (TICK / tb) * (R - self.base)
        d = R - self.base
        self.slow += 1
        if self.slow < 10:                              # knobs, traces and wiggles move every 0.1 s
            return out
        self.slow, dt = 0, 10 * TICK
        if p.get("anneal"):
            self.youth -= dt / p["anneal"] * self.youth
        delta = p.get("delta", 0.3) * (1.0 + p.get("wild", 3.0) * self.youth if p.get("anneal") else 1.0)
        now, moved = self.t, False
        for k in self.knobs:
            self.tr[k] += (dt / tr) * (self.off[k] - self.tr[k])
            self.x[k] = float(np.clip(self.x[k] + p.get("eta", 0.03) * dt * d * self.tr[k], *_log(k)))
            if now >= self.when[k]:                     # its own moment
                self.off[k] = delta * self.rng.uniform(-1.0, 1.0)
                self.when[k] = now + self.rng.exponential(p.get("wig", 20.0))
                moved = True
        self._set()
        if self.t >= self.next_log:
            self.next_log += 100.0
            self.trace.append((self.t, dict(self.x)))
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    p, spread, seed, seconds, poison = job
    q = mistuned(M.drawn(p, spread, seed), seed, p.get("mistune", 3.0))
    q = {k: v for k, v in q.items() if k not in ("vary", "body", "mistune")}
    q["tune_bal"] = int(bool(p.get("body")))
    lf = Life(seed, poison, brain=lambda s: CTuned(s, q))
    if p.get("body"):
        from discrete.bodies import THRUSTERS, draw, vary
        vary(lf, draw(seed, THRUSTERS))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.trace = lf.brain.trace
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
    L = lives(dict(p, **kw), spread, range(lo, hi), seconds)
    tag = f"c_body{int(kw.get('body', 0))}_{int(seconds)}" + "".join(
        f"_{k}{v:g}" for k, v in sorted(kw.items()) if k != "body")
    print(show(f"{tag}", summary(L)), flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                        f"lab/v/{tag}.lives", "wb"))
