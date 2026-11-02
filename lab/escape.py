"""escape.py: is escape from bites worth growing? (the user, 2026-10-30: colour and thruster wiring are evolution's, so
the baseline is the Braitenberg tracker, arena.Tracker.) Scripted responses to pain, to certify the gap before a grower
looks for one: on a bad taste (being bitten), for `dur` s fire at `rate` a second
  both: both thrusters (speed away), left / right: one thruster alone (turn; the left thruster turns it right), m0 / m1: by motor,
then the tracker again. Half the arena trackers, half the scripted kind (invasion).

    python escape.py [SEEDS] [mode=both] [rate=50] [dur=0.5] [add=0] [seconds=300]"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import arena as AR
from units import TICK

ESC = {}


class Flee(AR.Tracker):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.last_pain, self.fphase = -1e9, 0.0

    def taste(self, value, at):
        super().taste(value, at)
        if value < 0:
            self.last_pain = self.t

    def step(self):
        out = super().step()
        if self.t - self.last_pain < ESC.get("dur", 0.5):
            self.fphase += ESC.get("rate", 50.0) * TICK
            k = int(self.fphase)
            self.fphase -= k
            mode = ESC.get("mode", "both")
            ms = ([self.p["left_motor"], self.p["right_motor"]] if mode == "both" else [int(mode[1])] if mode in ("m0", "m1")
                  else [self.p[mode + "_motor"]])
            beats = [m for m in ms for _ in range(k)]
            return out + beats if ESC.get("add") else beats  # add=1: its beats added to the tracker's own
        return out


_init = AR.Robot.__init__


def _robot(self, rng, seed, p, spread, t, kind="B"):
    _init(self, rng, seed, p, spread, t, "tracker" if kind == "flee" else kind)
    if kind == "flee":
        q = dict(self.brain.p, left_motor=self.motor["left"])
        food = self.brain.food
        self.brain = Flee(seed, q)
        self.brain.food = food
        self.kind = "flee"


AR.Robot.__init__ = _robot


def run(job):
    seed, seconds, kw = job
    ESC.update(kw)
    A = AR.Arena(seed, 10, ("flee", "tracker"))
    for _ in range(int(seconds / TICK)):
        A.step()
    return [(r.kind, r.ate / (d - r.born) * 10, (r.lost + AR.THRUST * r.firings) / (d - r.born) * 10, d - r.born)
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
    # paired by arena: the scripted kind's mean minus the trackers', bootstrapped over arenas
    net = lambda r, k: np.mean([x[1] - x[2] for x in r if x[0] == k])     # eaten minus lost: the belly's change
    d = np.array([net(r, "flee") - net(r, "tracker") for r in res])
    boot = [d[np.random.default_rng(i).integers(len(d), size=len(d))].mean() for i in range(2000)]
    rows = [x for r in res for x in r]
    for k in ("flee", "tracker"):
        x = [r for r in rows if r[0] == k]
        print(f"{k:8s}: ate {np.mean([r[1] for r in x]):.3f}, lost {np.mean([r[2] for r in x]):.3f} a 10 s, "
              f"age {np.mean([r[3] for r in x]):.0f} s", flush=True)
    print(f"{kw}: net (eaten - lost), flee - tracker {d.mean():+.3f} [{np.percentile(boot, 2.5):+.3f}, {np.percentile(boot, 97.5):+.3f}]")
