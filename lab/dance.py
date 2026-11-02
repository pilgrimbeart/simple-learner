"""dance.py: can any dance-like policy use the beat-pulse coincidence (discrete/NOTEBOOK.md, D22)? B told the colour;
while it drives, instead of both thrusters together it beats them alternately (a zig-zag, rate zig per s, each beat
paired with a forward push from both every `push` beats), and on each food pulse adds `back` beats on the motor not
last fired (turning back, towards where the block probably is) or, with back < 0, on the motor last fired.

    python dance.py k=v,... k=v,...      # each a variant; held out 50000-50063 x 2
"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from units import TICK
from discrete import model as M


class Dance(M.Model):
    def __init__(self, seed, p, d):
        super().__init__(seed, p)
        self.d, self.zphase, self.last, self.pend, self.n = d, 0.0, 0, [], 0

    def stimulate(self, sensor, at):
        super().stimulate(sensor, at)
        if sensor == self.food and self.d.get("back", 0) and self.t - self.last_drive < self.p["hold"]:
            k = int(abs(self.d["back"]))
            self.pend += [(1 - self.last) if self.d["back"] > 0 else self.last] * k

    def step(self):
        out = super().step()
        driving = self.t - self.last_drive < self.p["hold"]
        if not driving or not self.d.get("zig"):
            self.pend = []
            return out
        self.zphase += self.d["zig"] * TICK
        k = int(self.zphase); self.zphase -= k
        res = []
        for _ in range(k):
            self.n += 1
            if self.d.get("push") and self.n % int(self.d["push"]) == 0:
                res += [0, 1]
            else:
                self.last = 1 - self.last
                res.append(self.last)
        res += self.pend
        if self.pend:
            self.last = self.pend[-1]
        self.pend = []
        return res


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    d, seed, poison = job
    lf = Life(seed, poison, brain=lambda s: None)
    food = lf.sensor[next(c for c in lf.sensor if c != poison)]
    p, sd = M.from_bench()
    q = M.drawn(p, sd, seed)
    q["V_H"] = 99.0
    br = Dance(seed, q, d)
    br.food = food
    lf.brain = br
    while lf.t < 10000:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, 10000, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / 100.0, "silicon"
    return l


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from minimal.spec import summary
    from discrete.poison import show
    with ProcessPoolExecutor(7) as ex:
        for a in sys.argv[1:]:
            d = {k: float(v) for k, v in (x.split("=") for x in a.split(",") if x)}
            L = list(ex.map(life, [(d, s, c) for s in range(50000, 50064) for c in ("red", "blue")]))
            print(show(f"dance {d}", summary(L)), flush=True)
