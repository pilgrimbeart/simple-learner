"""selftune.py: can B tune its own spending? (QUESTIONS.md, the plan, 2) Its knobs (hold, boredom, scan, drive and run
rates) drawn mistuned at birth; a tuner by simultaneous perturbation (SPSA; node perturbation): each epoch every knob
nudges itself by its own random sign for one half, the other way for the other half; the brain's efficiency in each
half (food - 2 poison, against what it spent: resting and its own firings, counted from taste and its motors) moves
each knob along its own nudge. Local: a knob knows its own sign and one broadcast outcome; one imperfect timer serves
both halves, so its error cancels.

With body=1, each life's thrusters drawn 0.5 to 2 and a sixth knob, the drive's balance, starting level.

    python selftune.py [SEEDS] [seconds=2000] [mistune=3] [body=0] [k=v ...]"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from units import TICK

KNOBS = ("hold", "bored", "scan", "drive", "run")
BOUNDS = dict(hold=(0.03, 1.5), bored=(1.0, 30.0), scan=(3.0, 50.0), drive=(10.0, 100.0), run=(10.0, 100.0))
LOG = dict(bal=(-1.4, 1.4))                             # the drive's balance (motor 0's rate against 1's), in the log
THRUST, REST = 0.002, 0.1                               # meals a firing costs; meals per s resting (spec.THRUST, NEED)


class Tuned(M.Model):
    """B with the tuner. tune: 0 off (fixed knobs); epoch (s, both halves), delta (each nudge, in the log), eta
    (the step, in the log per unit of efficiency difference)."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rng = np.random.default_rng(seed + 424_242)
        self.knobs = KNOBS + (("bal",) if p.get("tune_bal") else ())
        self.x = {k: np.log(self.p[k]) if k != "bal" else 0.0 for k in self.knobs}   # each knob's own setting (log)
        self.sign = {k: 1.0 for k in self.knobs}
        self.half, self.clock = 0, 0.0
        self.got = [0.0, 0.0]; self.fired = [0, 0]
        self.trace = []                                 # watching: (t, knobs) each epoch
        self._set()

    def _set(self):
        d = self.p.get("delta", 0.15) if self.p.get("tune") else 0.0
        s = 1.0 if self.half == 0 else -1.0
        for k in self.knobs:
            lo, hi = _log(k)
            v = float(np.clip(self.x[k] + s * d * self.sign[k], lo, hi))
            if k == "bal":
                self.p["g0"], self.p["g1"] = float(np.exp(v / 2)), float(np.exp(-v / 2))
            else:
                self.p[k] = float(np.exp(v))

    def taste(self, value, at):
        super().taste(value, at)
        self.got[self.half] += 1.0 if value > 0 else -2.0

    def step(self):
        if self.p.get("beta"):                          # food sightings (the eye the bit says is food) as a small
            self.got[self.half] += self.p["beta"] * self.seen[self.food]   # fraction of a meal each
        out = super().step()
        self.fired[self.half] += len(out)
        if not self.p.get("tune"):
            return out
        self.clock += TICK
        if self.clock >= self.p.get("epoch", 40.0) / 2:
            self.clock = 0.0
            if self.half == 1:                          # an epoch done: each knob moves along its own nudge
                w = self.p.get("epoch", 40.0) / 2
                eff = [g / (REST * w + THRUST * f) for g, f in zip(self.got, self.fired)]
                for k in self.knobs:
                    self.x[k] = float(np.clip(self.x[k] + self.p.get("eta", 0.05) * (eff[0] - eff[1]) * self.sign[k],
                                              *_log(k)))
                    self.sign[k] = 1.0 if self.rng.random() < 0.5 else -1.0
                self.got, self.fired = [0.0, 0.0], [0, 0]
                self.trace.append((self.t, dict(self.x)))   # (log)
            self.half = 1 - self.half
            self._set()
        return out


def _log(k):
    return LOG[k] if k in LOG else tuple(np.log(BOUNDS[k]))


def mistuned(p, seed, factor):
    """Each knob off by up to factor either way (log-uniform), drawn from the seed."""
    rng = np.random.default_rng(seed + 31_337)
    return {**p, **{k: float(np.clip(p[k] * np.exp(rng.uniform(-np.log(factor), np.log(factor))), *BOUNDS[k]))
                    for k in KNOBS}}


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    p, spread, seed, seconds, poison = job
    q = M.drawn(p, spread, seed) if p.get("vary", 1) else dict(p)
    if p.get("mistune", 1) > 1:
        q = mistuned(q, seed, p["mistune"])
    q = {k: v for k, v in q.items() if k not in ("vary", "body", "mistune")}
    q["tune_bal"] = int(bool(p.get("body")))
    lf = Life(seed, poison, brain=lambda s: Tuned(s, q))
    if p.get("body"):                                   # each life's thrusters 0.5-2 (bodies.THRUSTERS)
        from discrete.bodies import THRUSTERS, draw, vary
        vary(lf, draw(seed, THRUSTERS))
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
    seconds = kw.pop("seconds", 2000.0)
    p, spread = M.from_bench()
    arms = {"ceiling (B, fixed)": dict(p), "floor (mistuned, fixed)": dict(p, mistune=kw.get("mistune", 3.0)),
            "self-tuning": dict(p, mistune=kw.get("mistune", 3.0), tune=1, **kw)}
    if kw.get("only"):
        arms = {"self-tuning": arms["self-tuning"]}
        arms["self-tuning"].pop("only")
    for name, q in arms.items():
        L = lives(q, spread, range(lo, hi), seconds)
        s = summary(L)
        last = [l[2] for l in L]
        print(show(name, s), f"| last third food {np.mean([t[0] for t in last]) / last[0][2] * 10:.2f} poison "
              f"{np.mean([t[1] for t in last]) / last[0][2] * 10:.2f} per 10 s", flush=True)
        pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                            f"lab/v/tune_{name.split()[0]}_body{int(kw.get('body', 0))}.lives", "wb"))
