"""ctrnn.py: can sideways sensing emerge? (QUESTIONS.md, step 3; the user, 2026-11-01: time is where a small brain
computes.) A small continuous-time network (Beer 2003), evolved by CMA-ES in the real body's loop, told which eye is
food (so only foraging is asked of it: compare B told the colour, 2.54, and D21's yardstick). Nothing about scanning,
phase or holding is designed in: N leaky nodes, fully connected, each its own time constant (2 ticks to 5 s), the
eyes' pulses kicking every node, motors 0 and 1 firing at rates set by nodes 0 and 1. Noise on every node.

    python ctrnn.py evolve [GENS] [n=6 lam=16 seeds=8 tag=...]   # writes v/ctrnn_TAG.json
    python ctrnn.py judge FILE                                     # held out, 50000-50063 x 2
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from units import TICK  # noqa: E402

V = "/home/pilgrim/git/simple-learner/lab/v"
NOISE = 0.05                                            # each node's noise, per root second


def params(n):
    """name -> (start, lo, hi); lo > 0 means a log scale (minimal.search.encode)."""
    p = {}
    for i in range(n):
        p[f"tau{i}"] = (0.2, 2 * TICK, 5.0)
        p[f"b{i}"] = (0.0, -8.0, 8.0)
        for e in ("f", "p"):
            p[f"{e}{i}"] = (0.0, -4.0, 4.0)             # a pulse's kick to node i, from the food (f) or poison (p) eye
        for j in range(n):
            p[f"w{i}_{j}"] = (0.0, -8.0, 8.0)           # node j's output into node i
    p["r0"] = (30.0, 3.0, 150.0)                        # each motor's top rate, per s
    p["r1"] = (30.0, 3.0, 150.0)
    return p


class Net:
    def __init__(self, seed, q, n, food_sensor):
        self.n, self.food = n, food_sensor
        self.tau = np.array([q[f"tau{i}"] for i in range(n)])
        self.b = np.array([q[f"b{i}"] for i in range(n)])
        self.kf = np.array([q[f"f{i}"] for i in range(n)])
        self.kp = np.array([q[f"p{i}"] for i in range(n)])
        self.W = np.array([[q[f"w{i}_{j}"] for j in range(n)] for i in range(n)])
        self.r = np.array([q["r0"], q["r1"]])
        self.rng = np.random.default_rng(seed + 515)
        self.y = self.rng.normal(0, 0.1, n)
        self.phase = self.rng.random(2)
        self.seen = [0, 0]

    def stimulate(self, sensor, at):
        self.seen[sensor] += 1

    def taste(self, value, at):
        pass

    def drive(self, sensor):
        return 1.0

    def step(self):
        F, P = self.seen[self.food], self.seen[1 - self.food]
        self.seen = [0, 0]
        o = 1 / (1 + np.exp(-(self.y + self.b)))
        self.y += TICK / self.tau * (-self.y + self.W @ o) + self.kf * F + self.kp * P \
            + NOISE * math.sqrt(TICK) * self.rng.standard_normal(self.n)
        self.phase += self.r * o[:2] * TICK
        beats = np.floor(self.phase).astype(int)
        self.phase -= beats
        return [0] * beats[0] + [1] * beats[1]


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    q, n, seed, poison, seconds = job
    lf = Life(seed, poison, brain=lambda s: None)
    food = lf.sensor[next(c for c in lf.sensor if c != poison)]
    lf.brain = Net(seed, q, n, food)
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    return l


def lives(ex, qs, n, seeds, seconds=100.0):
    jobs = [(q, n, s, c, seconds) for q in qs for s in seeds for c in ("red", "blue")]
    out = list(ex.map(life, jobs, chunksize=2))
    k = 2 * len(seeds)
    return [out[i * k:(i + 1) * k] for i in range(len(qs))]


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from minimal.search import cmaes
    from minimal.spec import summary
    from discrete.poison import show
    from discrete.tune import robust
    cmd = sys.argv[1]
    kv = dict(a.split("=") for a in sys.argv[2:] if "=" in a)
    with ProcessPoolExecutor(int(kv.get("workers", 7))) as ex:
        if cmd == "evolve":
            gens = int(next((a for a in sys.argv[2:] if "=" not in a), 60))
            n, lam, ns, tag = int(kv.get("n", 6)), int(kv.get("lam", 16)), int(kv.get("seeds", 8)), kv.get("tag", "a")
            P = params(n)
            log = open(f"{V}/ctrnn_{tag}.log", "a")

            def say(s):
                print(s, flush=True); log.write(s + "\n"); log.flush()
            final, best, hist = cmaes(lambda p: p, P, gens=gens, lam=lam, seeds=ns, sigma=float(kv.get("sigma", 0.2)),
                                      evaluate=lambda qs, seeds, seconds: lives(ex, qs, n, list(seeds), seconds),
                                      judge=robust, log=say, first_seed=int(kv.get("first", 20000)),
                                      start=json.load(open(kv["start"]))["best"] if "start" in kv else None)
            json.dump({"n": n, "final": final, "best": best[1], "best_mean": best[0], "history": hist},
                      open(f"{V}/ctrnn_{tag}.json", "w"), indent=1)
            for name, q in (("final", final), ("best", best[1])):
                L = lives(ex, [q], n, list(range(50000, 50064)))[0]
                say(show(f"ctrnn {tag} {name} held out", summary(L)))
        elif cmd == "judge":
            d = json.load(open(sys.argv[2]))
            L = lives(ex, [d[kv.get("which", "final")]], d["n"], list(range(50000, 50064)))[0]
            print(show(f"ctrnn {sys.argv[2]}", summary(L)))
