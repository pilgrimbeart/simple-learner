"""grow.py: case 1 of recruitment (QUESTIONS.md, the plan, 4): taste wired to nothing. The unwired brain is B without its
learning: either eye starts a drive (each eye's pathway "drive"), and taste goes nowhere. Beside it, per eye, the
generic grower:

- predict: a fading tag of the eye's pulses (tau_tag); at each taste, the eye's prediction moves towards the taste in
  proportion to its tag (what follows this eye?);
- notice the gap: frustration, a leaky count (tau_f) of poisons tasted while the eye was tagged and predicted bad
  (below -theta): predicted, and it happened anyway;
- grow: frustration past `nf` grows a recruit on that eye's pathway (the declared primitive; once per eye);
- experiment: the recruit knows nothing of the circuit; it tries the generic operations on its pathway (drive as it
  was, block, reverse: the eye ends a drive), each for `trial` s, judging each by the taste that follows its own eye
  (tag-weighted, per second; drive, as it was, by the eye's running rate of the same), staying with one that is the
  best so far, else trying the next (win-stay lose-shift); judge=1, by all taste instead, the whole outcome;
  all=1, every operation tried once before the best is kept;
- stop: in all-food lives no eye predicts bad, so nothing grows.

    python grow.py ARM [SEEDS] [seconds=100] [k=v ...]   ARM: grow, unwired, B   (k: tau_tag, tau_f, theta, nf, trial)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from units import TICK

OPS = ("drive", "block", "reverse")


class Unwired(M.Model):
    """B with taste wired to nothing: each eye's pathway an operation (drive: starts a drive; block: nothing; reverse:
    ends a drive)."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.op = ["drive", "drive"]

    def taste(self, value, at):
        pass

    def step(self):
        s = self.seen
        F = sum(s[k] for k in (0, 1) if self.op[k] == "drive")
        P = sum(s[k] for k in (0, 1) if self.op[k] == "reverse")
        self.food, self.seen = 0, [F, P]
        return super().step()


class Grow(Unwired):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.tag = np.zeros(2)
        self.pred = np.zeros(2)
        self.fr = np.zeros(2)
        self.follow = np.zeros(2)                       # each eye's running rate of the taste that follows it (per s)
        self.all = 0.0                                  # judge=1: the running rate of all taste (the broadcast)
        self.recruit = [None, None]                     # each: dict(i=op index, start, score)
        self.events = []                                # watching: (t, what)

    def taste(self, value, at):
        p = self.p
        v = 1.0 if value > 0 else -1.0
        self.pred += p.get("alpha", 0.3) * self.tag * (v - self.pred)
        self.follow += self.tag * v / p.get("trial", 20.0)
        self.all += v / p.get("trial", 20.0)
        if v < 0:
            self.fr += self.tag * (self.pred < -p.get("theta", 0.3))
        for k in (0, 1):
            r = self.recruit[k]
            if r is not None:
                r["got"] += v if p.get("judge") else self.tag[k] * v

    def step(self):
        p = self.p
        pulses = list(self.seen)
        out = super().step()
        self.tag = np.minimum(1.0, self.tag * (1 - TICK / p.get("tau_tag", 1.0)) + 0.2 * np.array(pulses))
        self.fr *= 1 - TICK / p.get("tau_f", 50.0)
        self.follow *= 1 - TICK / p.get("trial", 20.0)
        self.all *= 1 - TICK / p.get("trial", 20.0)
        for k in (0, 1):
            r = self.recruit[k]
            if r is None:
                if self.fr[k] > p.get("nf", 2.0):       # grow
                    self.recruit[k] = r = dict(i=1, start=self.t, got=0.0, score={0: self.all if p.get("judge") else self.follow[k]})
                    self.op[k] = OPS[1]                 # (the pathway as it was already judged, by what followed)
                    self.events.append((self.t, f"grew on eye {k}"))
                continue
            if self.t - r["start"] >= p.get("trial", 20.0):   # a trial over: score it, win-stay lose-shift
                i = r["i"]
                r["score"][i] = r["got"] / (self.t - r["start"])
                best = max(r["score"], key=r["score"].get)
                untried = [j for j in range(len(OPS)) if j not in r["score"]]
                nxt = (untried[0] if untried else best) if p.get("all") else (i if i == best else untried[0] if untried
                                                                               else best)
                if nxt != i:
                    self.events.append((self.t, f"eye {k}: {OPS[nxt]}"))
                r.update(i=nxt, start=self.t, got=0.0)
                self.op[k] = OPS[nxt]
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison = job
    q = M.drawn(p, spread, seed)
    cls = {"grow": Grow, "unwired": Unwired, "B": M.Model}[arm]
    lf = Life(seed, poison, brain=lambda s: cls(s, q))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    b = lf.brain
    l.events = getattr(b, "events", [])
    l.ops = list(getattr(b, "op", []))
    l.poison_eye = None if poison is None else lf.sensor[poison]
    return l


def lives(arm, p, spread, seeds, seconds, poison=True, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    cs = ("red", "blue") if poison else (None, None)
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(life, [(arm, p, spread, s, seconds, c) for s in seeds for c in cs]))


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
    tag = f"g_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items()))
    print(show(tag, summary(L)), flush=True)
    if arm == "grow":
        grew = [l for l in L if l.events]
        right = sum(l.ops[l.poison_eye] != "drive" and l.ops[1 - l.poison_eye] == "drive" for l in L)
        print(f"  grew in {len(grew)} of {len(L)} lives; poison eye changed and food eye kept in {right}; "
              f"final ops on the poison eye: {sorted(set(l.ops[l.poison_eye] for l in L))}")
        A = lives(arm, dict(p, **kw), spread, range(lo, hi), seconds, poison=False)
        print(f"  all-food lives: grew in {sum(bool(l.events) for l in A)} of {len(A)}")
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                        f"lab/v/{tag}.lives", "wb"))
