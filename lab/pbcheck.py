import sys, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner"); sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from creature import Life
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
import periodbal as PB, world as W
from units import TICK
p, spread = M.from_bench()
for seed in range(16):
    q = dict(M.drawn(p, spread, seed), cal_every=50.0, cal_len=5.0)
    lf = Life(seed, "red", brain=lambda s: PB.PeriodBal(s, q)); f = draw(seed, THRUSTERS); vary(lf, f)
    thr = {m: t for t, m in lf.motor.items()}
    for _ in range(int(1000 / TICK)): lf.step()
    per = [0.79 * 2 * math.pi * W.DRAG / (q["scan"] * f[thr[m]] * W.TURN) for m in (0, 1)]
    b = lf.brain
    print(f"seed {seed}: T {[round(x, 2) for x in b.T]} predicted {[round(x, 2) for x in per]} n {b.n} x {b.x:+.2f} right {math.log(f[thr[1]]/f[thr[0]]):+.2f}")
