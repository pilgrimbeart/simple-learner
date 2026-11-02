"""omni.py k=v ...: the omniscient rung (QUESTIONS.md, the ladder): a brain told every block's place, its own pose,
its wiring and which colour is food; it steers to the nearest food whose straight path passes no poison, turning
with the thruster that turns it towards it (allowing for the spin still to come) and pushing with both while it
points there and goes slower than it should. A lower bound on omniscience (a better planner could do more)."""
import sys, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import world
from units import TICK


class Omni:
    def __init__(self, lf, poison, tol=0.15, vmax=0.03, k=8.0, clear=1.5e-3):
        self.lf, self.poison, self.tol, self.vmax, self.k, self.clear = lf, poison, tol, vmax, k, clear

    def stimulate(self, *a): pass
    def taste(self, *a): pass
    def drive(self, s): return 1.0

    def target(self):
        b = self.lf.body
        head = b.head()
        bad = world.COLOURS.index(self.poison) if self.poison else -1
        d = np.array([b.wrap(p - head) for p in b.xy])
        dist = np.hypot(d[:, 0], d[:, 1])
        best = None
        for i in np.argsort(dist):
            if b.kind[i] == bad:
                continue
            u = d[i] / max(dist[i], 1e-9)
            ok = True
            for j in np.flatnonzero(b.kind == bad):          # a poison near the straight path: choose another
                along = d[j] @ u
                if 0 < along < dist[i] and abs(d[j][0] * u[1] - d[j][1] * u[0]) < self.clear:
                    ok = False; break
            if ok:
                best = i; break
        return None if best is None else (d[best], dist[best])

    def step(self):
        b, lf = self.lf.body, self.lf
        tg = self.target()
        if tg is None:
            return []
        d, dist = tg
        e = (math.atan2(d[1], d[0]) - b.heading - b.spin / world.DRAG + math.pi) % (2 * math.pi) - math.pi
        if abs(e) > self.tol:
            return [lf.motor["right" if e > 0 else "left"]]
        v = b.speed @ b.forward()
        return [lf.motor["left"], lf.motor["right"]] if v < min(self.vmax, self.k * dist) else []


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    p, seed, poison = job
    lf = Life(seed, poison, brain=lambda s: None)
    lf.brain = Omni(lf, poison, **p)
    ticks = 10000
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings = 0.0, SPAN * len(lf.firings) / 100.0
    return l


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from minimal.spec import summary
    from discrete.poison import show
    with ProcessPoolExecutor(4) as ex:
        for a in sys.argv[1:]:
            p = {k: float(v) for k, v in (x.split("=") for x in a.split(",") if x)}
            L = list(ex.map(life, [(p, s, c) for s in range(50000, 50064) for c in ("red", "blue")]))
            print(show(f"omni {p}", summary(L)), flush=True)
