"""steer_probe.py: grow_arena's Steer with s forced (force=1: the right way, -1: the wrong, 0: none) for every grow robot,
to find a judge denser than catches: per robot, chase length, the food pair's pulses a second, |bias| at a chase's end."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import grow_arena as G
import arena as AR
from units import TICK

class Probe(G.Steer):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.pulses = 0
        self.drive_ticks = 0
    def stimulate(self, sensor, at):
        if sensor // 2 == self.food:
            self.pulses += 1
        super().stimulate(sensor, at)
    def step(self):
        out = super().step()
        self.drive_ticks += self.was_driving
        return out

def run(job):
    seed, force = job
    G.GROW.update(nf=1e9)
    G.Steer_cls = Probe
    A = AR.Arena(seed, 10, ("grow", "told"))
    for r in A.robots: setup(r, force)
    seen = set(id(r) for r in A.robots)
    out = []
    for _ in range(int(300 / TICK)):
        A.step()
        for r in A.robots:
            if id(r) not in seen:
                seen.add(id(r)); setup(r, force)
    for r, died in [(r, A.t) for r in A.robots] + A.dead:
        age = died - r.born
        if r.kind == "grow" and age >= 20:
            b = r.brain
            out.append((r.ate / age * 10, b.pulses / age, b.drive_ticks * TICK / max(b.chases, 1), b.caught / max(b.chases, 1), b.chases / age * 10))
    return out

def setup(r, force):
    if r.kind == "grow" and not isinstance(r.brain, Probe):
        old = r.brain
        b = Probe(0, old.p); b.food = old.food; r.brain = b
        b.s = force * r.right_s

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as ex:
        for force in (1, 0, -1):
            rows = np.array([x for res in ex.map(run, [(s, force) for s in range(16)]) for x in res])
            m = rows.mean(0); sd = rows.std(0)
            print(f"force {force:+d}: ate {m[0]:.3f}, food pulses/s {m[1]:.2f} (sd {sd[1]:.2f}), chase s {m[2]:.3f} (sd {sd[2]:.3f}), "
                  f"caught {m[3]:.3f} (sd {sd[3]:.3f}), chases/10s {m[4]:.1f}", flush=True)
