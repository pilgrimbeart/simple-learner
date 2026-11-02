import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from hunger import learn_hunger
from discrete.life import bench
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
n = learn_hunger(None, **kw)
# no hunger run (rh1 small keeps its PNP off); the free eye (latch-dependent) pulses at 4-5 s, 50/s
pulses = [(0, 4.0 + 0.02 * k) for k in range(50)] + [(1, 6.0 + 0.02 * k) for k in range(50)] + [("food", 0.5)]
t, V, p = bench(n, 8.0, ["m0", "m1", "h", "a"], pulses=pulses, step=1e-4)
def count(v, a, b):
    w = v[(t >= a) & (t < b)]; arm, c = True, 0
    for x in w:
        if arm and x > 2.0: c += 1; arm = False
        elif x < 1.0: arm = True
    return c
for a, b in ((1, 4), (4, 5), (5, 5.3), (6, 7), (7, 7.3), (7.3, 8)):
    print(f"{a}-{b} s: m0 {count(V['m0'], a, b) / (b - a):.0f}/s m1 {count(V['m1'], a, b) / (b - a):.0f}/s h max {V['h'][(t>=a)&(t<b)].max():.2f}")
