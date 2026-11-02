"""pursuit.py: the arms race in the arena (QUESTIONS.md, the plan, 4, candidate a). Every robot the tracker with the
escape grower (grow_escape.py, judged bite by bite); escape breaks bites, which frustrates the biter (a good taste
ended by nothing it did). First, certify: is there a pursuit worth growing? Half the arena also respond to a bite
ending (good taste stopping) by firing, for `dur` s at `rate` a second: left / right (one thruster, by side: the
left thruster turns it right), both, or m0 / m1 (by motor). Escape's firing takes precedence.

    python pursuit.py [SEEDS] [mode=left] [dur=0.2] [rate=50] [add=0] [prand=0] [seconds=300]
    (add=1: beats added to the brain's own; prand=r: the control, bursts at random moments, r a second)
    paired by arena: the pursuers' net (eaten - lost) minus the plain escape growers'"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import grow_escape as G
import arena as AR
from units import TICK

PUR = {}


class Pursuer(G.Grower):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.good_now = self.biting = False
        self.ended, self.pphase = -1e9, 0.0
        self.crng = np.random.default_rng(seed + 424_242)   # (the random control's own draws)
        self.ends = 0                                   # watching

    def taste(self, value, at):
        super().taste(value, at)
        if value > 0:
            self.good_now = True

    def step(self):
        if PUR.get("prand"):                            # prand=r: the control, triggered at random, r a second
            if self.crng.random() < PUR["prand"] * TICK:
                self.ended = self.t
        elif self.biting and not self.good_now:         # a bite just ended
            self.ended = self.t
            self.ends += 1
        self.biting, self.good_now = self.good_now, False
        out = super().step()
        escaping = self.op != "none" and self.t - self.last_pain < G.GROW.get("dur", 0.5)
        if not escaping and self.t - self.ended < PUR.get("dur", 0.2):
            self.pphase += PUR.get("rate", 50.0) * TICK
            k = int(self.pphase)
            self.pphase -= k
            mode = PUR.get("mode", "left")
            ms = {"left": [1 - self.p["right_motor"]], "right": [self.p["right_motor"]], "both": [0, 1],
                  "m0": [0], "m1": [1]}[mode]
            beats = [m for m in ms for _ in range(k)]
            return out + beats if PUR.get("add") else beats     # add=1: its beats added to the brain's own
        return out


_init = AR.Robot.__init__                               # (grow_escape's: makes "grow")


def _robot(self, rng, seed, p, spread, t, kind="B"):
    _init(self, rng, seed, p, spread, t, "grow" if kind == "pursue" else kind)
    if kind == "pursue":
        food = self.brain.food
        self.brain = Pursuer(seed, dict(self.brain.p))
        self.brain.food = food
        self.kind = "pursue"


AR.Robot.__init__ = _robot


def run(job):
    seed, seconds, kw = job
    PUR.update(kw)
    A = AR.Arena(seed, 10, ("pursue", "grow"))
    for _ in range(int(seconds / TICK)):
        A.step()
    return [(r.kind, r.ate / (d - r.born) * 10, (r.lost + AR.THRUST * r.firings) / (d - r.born) * 10, d - r.born,
             getattr(r.brain, "ends", 0) / (d - r.born))
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
    d = np.array([net(r, "pursue") - net(r, "grow") for r in res])
    boot = [d[np.random.default_rng(i).integers(len(d), size=len(d))].mean() for i in range(2000)]
    rows = [x for r in res for x in r]
    for k in ("pursue", "grow"):
        x = [r for r in rows if r[0] == k]
        print(f"{k:8s}: ate {np.mean([r[1] for r in x]):.3f}, lost {np.mean([r[2] for r in x]):.3f} a 10 s, "
              f"age {np.mean([r[3] for r in x]):.0f} s, bites ended {np.mean([r[4] for r in x]):.2f} a s", flush=True)
    print(f"{kw}: net, pursue - grow {d.mean():+.3f} [{np.percentile(boot, 2.5):+.3f}, {np.percentile(boot, 97.5):+.3f}]", flush=True)
