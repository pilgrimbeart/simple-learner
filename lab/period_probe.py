"""period_probe.py: do sightings recur at the revolution period while scanning with one motor? A brain firing motor m
alone at B's scan rate for 60 s, on lopsided bodies; the eye pulses' interval histogram's peak against the period
the body's spin predicts (2 pi DRAG / (rate k TURN))."""
import sys, math
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from creature import Life
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
import world as W
from units import TICK

class Scan:
    def __init__(self, m, rate):
        self.m, self.rate, self.phase, self.t, self.pulses = m, rate, 0.0, 0.0, []
    def stimulate(self, sensor, at): self.pulses.append(self.t + at)
    def taste(self, value, at): pass
    def step(self):
        self.t += TICK
        self.phase += self.rate * TICK
        k = int(self.phase); self.phase -= k
        return [self.m] * k

def fundamental(d, lo=0.3, hi=4.0, w=0.04, n=6, top=0.9):
    """The shortest period T whose comb (T, 2T ... nT, each +-w, each tooth's count over the count expected by chance
    there) scores within `top` of the best."""
    d = np.asarray(d)
    def dens(x):
        return np.mean(np.abs(d - x) < w)
    Ts = np.arange(lo, hi, 0.01)
    base = lambda x: np.mean(np.abs(d - x) < 0.5) * (2 * w / 1.0) + 1e-9
    sc = np.array([np.mean([dens(k * T) / base(k * T) for k in range(1, n + 1)]) for T in Ts])
    return float(Ts[np.flatnonzero(sc >= top * sc.max())[0]])

p, _ = M.from_bench()
rate = p["scan"]
print("scan rate", rate)
for seed in range(8):
    for m in (0, 1):
        b = Scan(m, rate)
        lf = Life(seed, None, brain=lambda s: b)
        f = draw(seed, THRUSTERS); vary(lf, f)
        thr = {mm: t for t, mm in lf.motor.items()}
        k = f[thr[m]]
        for _ in range(int(60 / TICK)): lf.step()
        x = np.array(b.pulses); x = x[x > 5]
        d = (x[None, :] - x[:, None]).ravel(); d = d[(d > 0.15) & (d < 17)]
        pk = fundamental(d)
        pred = 2 * math.pi * W.DRAG / (rate * k * W.TURN)
        print(f"seed {seed} motor {m} k {k:.2f}: pulses {len(x)}, peak interval {pk:.2f} s, predicted period {pred:.2f} s")
