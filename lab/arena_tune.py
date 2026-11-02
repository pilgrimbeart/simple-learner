"""arena_tune.py: the tracker's standing policy retuned for the disc arena, firing charged (evolution's job: the same
every life). A hill-climb by invasion: half the arena the candidate, half the current best; a knob multiplied by 2 or
0.5 is kept if the candidate's net (eaten - lost to bites - firing) beats the best's surely, paired by arena.
Knobs: B's hold, bored, scan, drive, run (each a factor on the life's drawn value) and the tracker's gain.

    python arena_tune.py [SEEDS] [rounds=2] [seconds=300]   -> prints each step; saves v/arena_tune.json"""
import json, sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import arena as AR
from units import TICK

KNOBS = ("hold", "bored", "scan", "drive", "run", "gain")
_init = AR.Robot.__init__


def _robot(self, rng, seed, p, spread, t, kind="B"):
    if isinstance(kind, tuple):                         # ("tracker", factors): a tracker with its knobs scaled
        _init(self, rng, seed, p, spread, t, "tracker")
        for k, v in kind[1].items():
            if k == "gain":
                self.brain.p["gain"] = 0.1 * v
            else:
                self.brain.p[k] *= v
        self.kind = kind[2]
    else:
        _init(self, rng, seed, p, spread, t, kind)


AR.Robot.__init__ = _robot


def run(job):
    seed, seconds, a, b = job
    A = AR.Arena(seed, 10, (("tracker", a, "a"), ("tracker", b, "b")))
    for _ in range(int(seconds / TICK)):
        A.step()
    rows = [(r.kind, (r.ate - r.lost - AR.THRUST * r.firings) / (d - r.born) * 10)
            for r, d in [(r, A.t) for r in A.robots] + A.dead if d - r.born >= 20]
    return np.mean([x for k, x in rows if k == "a"]) - np.mean([x for k, x in rows if k == "b"])


def compare(ex, seeds, seconds, a, b):
    d = np.array(list(ex.map(run, [(s, seconds, a, b) for s in seeds])))
    boot = [d[np.random.default_rng(i).integers(len(d), size=len(d))].mean() for i in range(2000)]
    return d.mean(), np.percentile(boot, [2.5, 97.5])


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    args = [a for a in sys.argv[1:] if "=" not in a]
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
    seeds = range(*(int(x) for x in (args[0] if args else "0:16").split(":")))
    seconds = kw.get("seconds", 300.0)
    best = dict.fromkeys(KNOBS, 1.0)
    with ProcessPoolExecutor() as ex:
        for rnd in range(int(kw.get("rounds", 2))):
            for k in KNOBS:
                for f in (0.5, 2.0):
                    cand = dict(best, **{k: best[k] * f})
                    m, (lo, hi) = compare(ex, seeds, seconds, cand, best)
                    keep = lo > 0
                    print(f"round {rnd} {k} x{f}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]{'  kept' if keep else ''}", flush=True)
                    if keep:
                        best = cand
                        break
            print(f"best after round {rnd}: {best}", flush=True)
        m, (lo, hi) = compare(ex, range(100, 148), seconds, best, dict.fromkeys(KNOBS, 1.0))
        print(f"held out (100-147), best - tracker: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]", flush=True)
    json.dump(best, open("/home/pilgrim/git/simple-learner/lab/v/arena_tune.json", "w"))
