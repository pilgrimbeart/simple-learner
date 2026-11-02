"""grow_arena.py: recruitment in the arena (arena.py; QUESTIONS.md, the plan, 4): steering grown. B told the colour
(anatomy: tails are always food), learning off, and beside it the grower:

- the gap: a chase (a drive, begun by a tail sighted) that ends with no bite: frustration, a leaky count (tau_f) of
  such chases;
- grow: frustration past `nf` grows one recruit (the declared primitive) linking the food pair's two sensors, a and b
  (which is left the brain doesn't know), to the motors: g = s gain (Na - Nb) / (Na + Nb), each a leaky count (tau_s)
  of its sensor's pulses, makes motor 0 fire 1 + g times its rate and motor 1 1 - g; which way, s, it doesn't know;
- experiment: it tries s = 0 (as it was), +1, -1, each for `trial` s, judging each by the food pair's pulses a second
  (how much food it saw: catches are too few to judge by, steer_probe.py), then keeps the best (every operation once,
  as grow.py's all=1);
- the right s depends on the life's wiring (which sensor is left, which thruster turns which way): half the lives
  each, so no fixed brain can have it.

    python grow_arena.py [SEEDS] [seconds=300] [n=10] [kinds=grow,told] [k=v ...]
    (k: nf, tau_f, trial (s), gain, tau_s; nf=1e9: never grows, just counts chases)"""
import math
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import arena as AR
from discrete import model as M
from units import TICK

OPTS = (0, 1, -1)


class Steer(AR.AdaptB):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.N = np.zeros(2)                            # the food pair's two sensors' leaky counts
        self.fr = 0.0
        self.was_driving, self.bit = False, False
        self.chases = self.caught = 0                   # watching
        self.recruit = None                             # dict(i: option index, start, got: its food pulses, score)
        self.s = 0
        self.grew = None

    def stimulate(self, sensor, at):
        if sensor // 2 == self.food:
            self.N[sensor % 2] += 1
            if self.recruit is not None:
                self.recruit["got"] += 1
        super().stimulate(sensor, at)

    def taste(self, value, at):
        super().taste(value, at)
        if value > 0:
            self.bit = True

    def _chase_ended(self, caught):
        p = self.p
        self.chases += 1
        self.caught += caught
        if not caught:
            self.fr += 1.0
        if self.recruit is None and self.fr > self.p.get("nf", 3.0):
            self.grew = self.t
            self.recruit = dict(i=0, start=self.t, got=0, score={})

    def step(self):
        p = self.p
        bias = (self.N[0] - self.N[1]) / (self.N.sum() + 1e-9)
        g = self.s * p.get("gain", 0.1) * bias
        p["g0"], p["g1"] = 1 + g, 1 - g
        self.N *= 1 - TICK / p.get("tau_s", 0.2)
        self.fr *= 1 - TICK / p.get("tau_f", 50.0)
        r = self.recruit
        if r is not None and len(r["score"]) < len(OPTS) and self.t - r["start"] >= p.get("trial", 15.0):
            r["score"][r["i"]] = r["got"] / (self.t - r["start"])
            r["start"], r["got"] = self.t, 0
            r["i"] = r["i"] + 1 if len(r["score"]) < len(OPTS) else max(r["score"], key=r["score"].get)
            self.s = OPTS[r["i"]]
        out = super().step()
        driving = self.t - self.last_drive < p["hold"]
        if driving and not self.was_driving:
            self.bit = False
        if self.was_driving and not driving:
            self._chase_ended(int(self.bit))
        self.was_driving = driving
        return out


_init = AR.Robot.__init__


def _robot(self, rng, seed, p, spread, t, kind="B"):
    _init(self, rng, seed, p, spread, t, "told" if kind == "grow" else kind)
    if kind == "grow":
        q = dict(self.brain.p, **{k: v for k, v in GROW.items()})
        food = self.brain.food
        self.brain = Steer(seed, q)
        self.brain.food = food
        self.kind = "grow"
        # watching: the s that steers towards the tail (as arena.Tracker does)
        a_left = self.sensor[("blue", "left")] % 2 == 0
        right = 1 if self.motor["right"] == 0 else -1
        self.right_s = right if a_left else -right


GROW = {}
AR.Robot.__init__ = _robot


def run(job):
    seed, seconds, n, kinds, kw = job
    GROW.update(kw)
    A = AR.Arena(seed, n, kinds)
    for _ in range(int(seconds / TICK)):
        A.step()
    out = []
    for r, died in [(r, A.t) for r in A.robots] + A.dead:
        age = died - r.born
        if age >= 20:
            b = r.brain
            out.append(dict(kind=r.kind, ate=r.ate / age * 10, lost=r.lost / age * 10, age=age,
                            chases=getattr(b, "chases", 0) / age * 10, caught=getattr(b, "caught", 0),
                            n=getattr(b, "chases", 0), grew=getattr(b, "grew", None),
                            s=getattr(b, "s", None), right=getattr(r, "right_s", None),
                            done=b.recruit is not None and len(b.recruit["score"]) == len(OPTS)
                            if hasattr(b, "recruit") else False))
    return out


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    args = [a for a in sys.argv[1:] if "=" not in a]
    kw = dict(a.split("=") for a in sys.argv[1:] if "=" in a)
    kinds = tuple(kw.pop("kinds", "grow,told").split(","))
    seconds, n = float(kw.pop("seconds", 300)), int(kw.pop("n", 10))
    g = {k: float(v) for k, v in kw.items()}
    seeds = range(*(int(x) for x in (args[0] if args else "0:16").split(":")))
    with ProcessPoolExecutor() as ex:
        rows = [x for res in ex.map(run, [(s, seconds, n, kinds, g) for s in seeds]) for x in res]
    for k in kinds:
        x = [r for r in rows if r["kind"] == k]
        ate = np.array([r["ate"] for r in x])
        boot = [ate[np.random.default_rng(i).integers(len(ate), size=len(ate))].mean() for i in range(1000)]
        print(f"{k:8s}: {len(x)} robots, ate {ate.mean():.2f} [{np.percentile(boot, 2.5):.2f}, "
              f"{np.percentile(boot, 97.5):.2f}] a 10 s, lost {np.mean([r['lost'] for r in x]):.2f}, age "
              f"{np.mean([r['age'] for r in x]):.0f} s, chases {np.mean([r['chases'] for r in x]):.1f} a 10 s, "
              f"caught {sum(r['caught'] for r in x) / max(1, sum(r['n'] for r in x)):.0%} of chases", flush=True)
        if k == "grow":
            gr = [r for r in x if r["grew"] is not None]
            done = [r for r in gr if r["done"]]
            print(f"  grew in {len(gr)} of {len(x)} (median at {np.median([r['grew'] for r in gr]) if gr else 0:.0f} s"
                  f" of life... ), finished trials {len(done)}; of those kept the right way "
                  f"{sum(r['s'] == r['right'] for r in done)}, none {sum(r['s'] == 0 for r in done)}, "
                  f"wrong {sum(r['s'] == -r['right'] for r in done)}", flush=True)
