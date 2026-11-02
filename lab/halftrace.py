import sys, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from creature import Life
from discrete import model as M
from discrete.bodies import SPREAD, THRUSTERS, draw, vary
from units import TICK
class Scan:
    def __init__(self, m, rate): self.m, self.rate, self.phase, self.t, self.pulses, self.lf = m, rate, 0.0, 0.0, [], None
    def stimulate(self, sensor, at): self.pulses.append((self.t + at, self.lf.body.heading, sensor, *self.lf.body.pos))
    def taste(self, v, at): pass
    def step(self):
        self.t += TICK; self.phase += self.rate * TICK; k = int(self.phase); self.phase -= k
        return [self.m] * k
p, spread = M.from_bench(); seed = 50027
q = M.drawn(p, spread, seed)
b = Scan(0, q["scan"])
lf = Life(seed, None, brain=lambda s: b); b.lf = lf
vary(lf, draw(seed, {**SPREAD, **THRUSTERS}))
for _ in range(int(120 / TICK)): lf.step()
P = np.array(b.pulses); t, hd = P[:, 0], P[:, 1]
# revolution from heading
T = 2 * math.pi / ((hd[-1] - hd[0]) / (t[-1] - t[0])) if hd[-1] != hd[0] else 0
print(f"pulses {len(P)}; period from heading {abs(T):.2f} s")
d = t[None, :] - t[:, None]; dh = (hd[None, :] - hd[:, None]) % (2 * math.pi)
for lag in (abs(T) / 2, abs(T)):
    m = np.abs(d - lag) < 0.05
    h, _ = np.histogram(np.degrees(dh[m]), bins=12, range=(0, 360))
    print(f"lag {lag:.2f} s: pairs {m.sum()}, heading difference histogram (30 deg bins) {h.tolist()}")
pos = P[:, 3:5]
print("position spread during sweep (mm):", np.round(1000 * pos.std(0), 2))
