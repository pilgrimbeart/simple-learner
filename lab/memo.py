"""memo.py: the short-memory rung: B's blocks (cmodel4, tolerances), told which colour is food, and knowing its own
heading (perfect path integration): having lost sight of food, it turns back to the heading where it last saw it
(within mem s), then drives; against the same without memory."""
import sys, json, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmodel4, world
D = "/home/pilgrim/git/simple-learner/lab/m2/"
B = {**cmodel4.NOMINAL, **json.load(open(D + "B.json")), "hi": 99.0}


class Memo(cmodel4.Model):
    def __init__(self, seed, lf=None, mem=0.0, tol=0.2, **p):
        super().__init__(seed, **p)
        self.lf, self.mem, self.tol = lf, mem, tol
        self.seen_at, self.seen_heading = -1e9, 0.0

    def taste(self, value, at):
        self.seen_at = -1e9                             # whatever it tasted is gone: nothing to go back for
        super().taste(value, at)

    def step(self):
        F, P = self.seen[self.food], self.seen[1 - self.food]
        b = self.lf.body
        if P:
            self.seen_at = -1e9                         # poison in view: don't go back that way
        if F:
            self.seen_at, self.seen_heading = self.t + 0.01, b.heading
        driving = self.t + 0.01 - self.last_drive < self.p["hold"]
        if self.mem and not F and not driving and 0 < self.t + 0.01 - self.seen_at < self.mem:
            self.seen = [0, 0]
            self.t += 0.01
            e = (self.seen_heading - b.heading - b.spin / world.DRAG + math.pi) % (2 * math.pi) - math.pi
            if abs(e) > self.tol:                       # turn back the short way (told its wiring: the ceiling)
                return [self.lf.motor["right" if e > 0 else "left"]]
            self.last_drive = self.t                    # pointing back: drive as if it saw it again
            return [0, 1]
        return super().step()


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    mem, seed, poison = job
    q = cmodel4.drawn(B, seed)
    lf = Life(seed, poison, brain=lambda s: None)
    lf.brain = Memo(seed, lf=lf, mem=mem, **q)
    lf.brain.food = lf.sensor[next(c for c in lf.sensor if c != poison)]
    while lf.t < 10000:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, 10000, poison))
    l.power, l.firings = 9e-9, SPAN * len(lf.firings) / 100.0
    return l


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from minimal.spec import summary
    from discrete.poison import show
    with ProcessPoolExecutor(4) as ex:
        for mem in (0.0, 0.5, 1.0, 2.0, 4.0):
            L = list(ex.map(life, [(mem, s, c) for s in range(50000, 50064) for c in ("red", "blue")]))
            print(show(f"memory {mem} s", summary(L)), flush=True)
