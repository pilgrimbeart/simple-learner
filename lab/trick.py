"""trick.py: can a brain learn tricks nobody designed? (QUESTIONS.md, the plan, 3; the user's idea, 2026-10-29) B, fixed,
with a reservoir beside it: n random sequence detectors over the brain's own events (its two eyes, its two motors'
beats), each firing when its event b comes `lag` after its event a (within a 50 ms window). Each detector, when it
fires, may add a beat to its own motor, with probability p = clip(p0 + w, 0, pmax), w its memory node (born 0). Each
keeps a fading tag (tau_e) of whether it acted against its odds (+(1 - p) if it did, -p if not: REINFORCE, so the tag
averages zero whatever the meals); taste credits every tag (w += eta x value x tag; food 1, poison -2), and each
extra beat is charged at once (its cost, THRUST meals, at the brain's running price of energy, lam). Three-factor
learning on a random reservoir (Izhikevich 2007; Fremaux and Gerstner 2016): the trick to find here is steering a
lopsided body.

    python trick.py [SEEDS] [seconds=10000] [body=1] [k=v ...]   (k: n, p0, pmax, eta, tau_e, lam, maxlag, learn)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from minimal.spec import THRUST
from units import TICK

WIN = 5                                                 # ticks: a detector's window (50 ms)


class Trick(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        rng = np.random.default_rng(seed + 818_181)
        self.r = rng
        n = int(p.get("n", 200))
        L = int(p.get("maxlag", 1.0) / TICK)
        self.a = rng.integers(4, size=n)                # events: 0 food eye, 1 other eye, 2 motor 0, 3 motor 1
        self.b = rng.integers(4, size=n)
        self.lag = rng.integers(1, L, size=n)
        self.act = rng.integers(2, size=n)              # the motor it beats
        self.w = np.zeros(n)
        self.tag = np.zeros(n)
        self.H = L + WIN + 2
        self.hist = np.zeros((4, self.H))               # each event's count, a ring of ticks
        self.cum = np.zeros((4, self.H + 1))
        self.i = 0
        self.ev = np.zeros(4)
        self.extra = 0
        self.trace, self.next_log = [], 0.0

    def taste(self, value, at):
        super().taste(value, at)
        if self.p.get("learn", 1):
            v = 1.0 if value > 0 else -2.0
            self.w += self.p.get("eta", 0.05) * v * self.tag

    def step(self):
        p = self.p
        F, P = self.seen[self.food], self.seen[1 - self.food]
        out = super().step()
        ev = np.array([F > 0, P > 0, 0 in out, 1 in out], float)
        # this tick's events into the ring; a detector fires if b now and a within its window `lag` ago
        self.i = (self.i + 1) % self.H
        self.hist[:, self.i] = ev
        idx = (self.i - self.lag[None, :] - np.arange(WIN)[:, None]) % self.H    # (WIN, n)
        seen_a = self.hist[self.a[None, :], idx].sum(0) > 0
        fire = (ev[self.b] > 0) & seen_a
        decay = TICK / p.get("tau_e", 2.0)
        self.tag -= decay * self.tag
        if fire.any():
            f = np.flatnonzero(fire)
            pr = np.clip(p.get("p0", 0.05) + self.w[f], 0.0, p.get("pmax", 0.9))
            did = self.r.random(len(f)) < pr
            self.tag[f] += np.where(did, 1.0 - pr, -pr)
            if p.get("learn", 1):                       # each extra beat's cost, charged at once
                self.w[f[did]] -= p.get("eta", 0.05) * p.get("lam", 2.0) * THRUST * (1.0 - pr[did])
            out = out + [int(m) for m in self.act[f[did]]]
            self.extra += int(did.sum())
        if self.t >= self.next_log:
            self.next_log += 500.0
            self.trace.append((self.t, self.w.copy()))
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison = job
    q = {k: v for k, v in M.drawn(p, spread, seed).items() if k not in ("body",)}
    lf = Life(seed, poison, brain=lambda s: (Trick if arm == "trick" else M.Model)(s, q))
    if p.get("body", 1):
        from discrete.bodies import THRUSTERS, draw, vary
        f = draw(seed, THRUSTERS)
        vary(lf, f)
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.trace = getattr(lf.brain, "trace", [])
    l.extra = getattr(lf.brain, "extra", 0)
    if arm == "trick":
        b = lf.brain
        l.det = (b.a, b.b, b.lag, b.act)
        thr = {m: t for t, m in lf.motor.items()}
        l.weak = None if not p.get("body", 1) else int(f[thr[0]] > f[thr[1]])   # the motor of the weaker thruster
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
    tag = f"t_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items()))
    print(show(tag, summary(L)), f"extra beats per 10 s {np.mean([l.extra for l in L]) * 10 / seconds:.1f}", flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                        f"lab/v/{tag}.lives", "wb"))
