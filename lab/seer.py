"""seer.py: the seer rung (between memory and omniscience): told the place of each block the moment an eye pulses for
it (the nearest of that colour in the eye's corridor), and remembering it until it is eaten; told its pose and which
colour is food; it steers (as omni.py) to the nearest remembered food with no remembered poison on its path, and
scans with one thruster when it remembers none."""
import sys, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import world
from omni import Omni
from units import TICK


class Seer(Omni):
    def __init__(self, lf, poison, food_sensor, scan=12.0, bored=2.0, roam=0.5, **p):
        super().__init__(lf, poison, **p)
        self.food_sensor, self.scan, self.n, self.phase = food_sensor, scan, [0, 0], 0.0
        self.known = set()
        self.bored, self.roam, self.idle = bored, roam, 0.0   # nothing known for bored s: run straight roam s
        self.colour_of = {s: world.COLOURS.index(c) for c, s in lf.sensor.items()}

    def stimulate(self, sensor, at):
        self.n[sensor] += 1

    def target(self):
        b = self.lf.body
        head, f = b.head(), b.forward()
        d = np.array([b.wrap(p - head) for p in b.xy])
        along = d @ f
        side = np.abs(d[:, 0] * f[1] - d[:, 1] * f[0])
        for s in (0, 1):                                 # a pulse: the nearest block of its colour in the corridor
            if self.n[s]:
                k = self.colour_of[s]
                m = np.flatnonzero((b.kind == k) & (along > 0) & (along < world.RANGE) & (side < world.EAT + world.BLOCK))
                if len(m):
                    self.known.add(tuple(np.round(b.xy[m[np.argmin(along[m])]], 6)))
        self.n = [0, 0]
        here = {tuple(np.round(p, 6)): int(k) for p, k in zip(b.xy, b.kind)}
        self.known = {p for p in self.known if p in here}  # eaten blocks are gone (it saw itself eat them)
        bad = world.COLOURS.index(self.poison)
        foods = [np.array(p) for p in self.known if here[p] != bad]
        poisons = [b.wrap(np.array(p) - head) for p in self.known if here[p] == bad]
        best = None
        for p in sorted(foods, key=lambda p: np.hypot(*b.wrap(p - head))):
            dd = b.wrap(p - head); L = np.hypot(*dd); u = dd / max(L, 1e-9)
            if all(not (0 < q @ u < L and abs(q[0] * u[1] - q[1] * u[0]) < self.clear) for q in poisons):
                best = (dd, L); break
        return best

    def step(self):
        tg = self.target()
        if tg is None:
            self.idle += TICK
            if self.idle > self.bored:
                if self.idle > self.bored + self.roam:
                    self.idle = 0.0
                b = self.lf.body
                return [self.lf.motor["left"], self.lf.motor["right"]] if b.speed @ b.forward() < self.vmax else []
            self.phase += self.scan * TICK
            k = int(self.phase); self.phase -= k
            return [self.lf.motor["left"]] * k
        self.idle = 0.0
        b, lf = self.lf.body, self.lf
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
    lf.brain = Seer(lf, poison, lf.sensor[next(c for c in lf.sensor if c != poison)], **p)
    while lf.t < 10000:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, 10000, poison))
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
            print(show(f"seer {p}", summary(L)), flush=True)
