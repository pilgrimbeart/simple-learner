"""alert.py: candidate (c) of the plan's step 4 (QUESTIONS.md), certified first: is there a response to a recent bite
that pays? A bite suggests a hunter near. Every robot the tracker with the escape grower (grow_escape.py); half also,
for `T` s after a bite ends (pain stopping), unless escaping or chasing (driving):
  run: both thrusters at B's running rate (keep moving), still: nothing (keep still, scanning stopped).

    python alert.py [SEEDS] [mode=run] [T=3] [seconds=300]   paired by arena: net, alert minus plain escape growers"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import grow_escape as G
import arena as AR
from units import TICK

AL = {}


class Alert(G.Grower):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.was_hurting, self.until, self.aphase = False, -1e9, 0.0
        self.crng = np.random.default_rng(seed + 424_242)   # (the random control's own draws)
        self.ends, self.on = 0, 0                       # watching: bites ended, ticks responding

    def step(self):
        out = super().step()
        if AL.get("always"):                            # always=1: the control, the response whatever the past
            self.until = 1e18
        elif AL.get("prand"):                           # prand=r: the control, triggered at random, r a second
            if self.crng.random() < AL["prand"] * TICK:
                self.until = self.t + AL.get("T", 3.0)
        elif self.was_hurting and not self.hurting:     # a bite ended
            self.until = self.t + AL.get("T", 3.0)
            self.ends += 1
        self.was_hurting = self.hurting
        escaping = self.op != "none" and self.t - self.last_pain < G.GROW.get("dur", 0.5)
        driving = self.t - self.last_drive < self.p["hold"]
        if self.t < self.until and not escaping and not driving:
            self.on += 1
            if AL.get("mode", "run") == "still":
                return []
            self.aphase += self.p["run"] * TICK
            k = int(self.aphase)
            self.aphase -= k
            return [0, 1] * k
        return out


_init = AR.Robot.__init__


def _robot(self, rng, seed, p, spread, t, kind="B"):
    _init(self, rng, seed, p, spread, t, "grow" if kind == "alert" else kind)
    if kind == "alert":
        food = self.brain.food
        self.brain = Alert(seed, dict(self.brain.p))
        self.brain.food = food
        self.kind = "alert"


AR.Robot.__init__ = _robot


def run(job):
    seed, seconds, kw = job
    AL.update(kw)
    A = AR.Arena(seed, 10, ("alert", "grow"))
    for _ in range(int(seconds / TICK)):
        A.step()
    return [(r.kind, r.ate / (d - r.born) * 10, (r.lost + AR.THRUST * r.firings) / (d - r.born) * 10, d - r.born,
             getattr(r.brain, "ends", 0) / (d - r.born), getattr(r.brain, "on", 0) * TICK / (d - r.born))
            for r, d in [(r, A.t) for r in A.robots] + A.dead if d - r.born >= 20]


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    args = [a for a in sys.argv[1:] if "=" not in a]
    kw = dict(a.split("=") for a in sys.argv[1:] if "=" in a)
    seconds = float(kw.pop("seconds", 300))
    kw = {k: (v if k == "mode" else float(v)) for k, v in kw.items()}
    seeds = range(*(int(x) for x in (args[0] if args else "0:16").split(":")))
    with ProcessPoolExecutor() as ex:
        res = list(ex.map(run, [(s, seconds, kw) for s in seeds]))
    net = lambda r, k: np.mean([x[1] - x[2] for x in r if x[0] == k])
    d = np.array([net(r, "alert") - net(r, "grow") for r in res])
    boot = [d[np.random.default_rng(i).integers(len(d), size=len(d))].mean() for i in range(2000)]
    rows = [x for r in res for x in r]
    for k in ("alert", "grow"):
        x = [r for r in rows if r[0] == k]
        print(f"{k:8s}: ate {np.mean([r[1] for r in x]):.3f}, lost {np.mean([r[2] for r in x]):.3f} a 10 s, "
              f"age {np.mean([r[3] for r in x]):.0f} s, bites ended {np.mean([r[4] for r in x]):.2f} a s, "
              f"responding {np.mean([r[5] for r in x]):.0%} of the time", flush=True)
    print(f"{kw}: net, alert - grow {d.mean():+.3f} [{np.percentile(boot, 2.5):+.3f}, {np.percentile(boot, 97.5):+.3f}]", flush=True)
