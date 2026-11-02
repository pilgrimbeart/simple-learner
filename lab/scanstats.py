import sys, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner"); sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from creature import Life
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
import periodbal as PB, world as W
from units import TICK
p, spread = M.from_bench()
class S(PB.PeriodBal):
    def _close(self):
        self.lens = getattr(self, "lens", []) + [(self.t - self.start, len(self.ep), self.sm)]
        super()._close()
for seed in range(3):
    q = dict(M.drawn(p, spread, seed), learn=0)
    lf = Life(seed, "red", brain=lambda s: S(s, q)); f = draw(seed, THRUSTERS); vary(lf, f)
    thr = {m: t for t, m in lf.motor.items()}
    for _ in range(int(500 / TICK)): lf.step()
    L = np.array(lf.brain.lens)
    per = [0.79 * 2 * math.pi * W.DRAG / (q["scan"] * f[thr[m]] * W.TURN) for m in (0, 1)]
    print(f"seed {seed}: scans {len(L)}, length median {np.median(L[:,0]):.2f} s, 90th {np.percentile(L[:,0],90):.2f}; pulses median {np.median(L[:,1]):.0f}, "
          f"scans longer than their period {np.mean([l > per[int(m)] for l, _, m in L]):.0%}; periods {[round(x,2) for x in per]}")
