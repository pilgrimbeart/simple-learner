import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from hunger import learn_hunger
from discrete.life import bench
kw = dict(a.split("=") for a in sys.argv[1:])
kw = {k: float(v) for k, v in kw.items()}
n = learn_hunger(None, **kw)
pulses = [("food", t) for t in (2.0, 2.3, 2.6)] + [("food", 20.0)] + [("food", 30.0), ("poison", 30.5)]
t, V, p = bench(n, 40.0, ["q", "u", "ub", "h", "m1"], pulses=pulses, step=5e-4)
print(f"parts {n.parts()} power {p*1e9:.0f} nW")
for s in [0.5, 1.9, 2.1, 2.8, 4, 6, 8, 10, 12, 15, 18, 19.9, 20.2, 22, 25, 28, 32, 36, 39.9]:
    i = np.searchsorted(t, s)
    w = (t > s - 0.5) & (t <= s)
    print(f"{s:5.1f}s q {V['q'][i]:.2f} u {V['u'][i]:.2f} ub {V['ub'][i]:.2f} h {V['h'][i]:.2f} (h max {V['h'][w].max():.2f}) m1 max {V['m1'][w].max():.2f}")
