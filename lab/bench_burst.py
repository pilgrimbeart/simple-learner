import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from hunger import learn_hunger
from discrete.life import bench
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
n = learn_hunger(None, **kw)
pulses = [("food", 0.5)] + [(e, 2.0) for e in (0,)] + [(e, 4.0 + 0.04 * k) for k in range(10) for e in (0,)] \
         + [(1, 6.0)] + [(1, 7.0 + 0.04 * k) for k in range(10)]
t, V, p = bench(n, 9.0, ["m0", "m1", "h"], pulses=pulses, step=1e-4)
def count(v, a, b):
    w = v[(t >= a) & (t < b)]; arm, c = True, 0
    for x in w:
        if arm and x > 2.0: c += 1; arm = False
        elif x < 1.0: arm = True
    return c
print(f"scan {count(V['m0'], 1, 2) :.0f}/s; motor B after one pulse: eye0 {count(V['m1'], 2, 3)}, eye1 {count(V['m1'], 6, 7)}; "
      f"in and after 10 pulses over 0.4 s: eye0 {count(V['m1'], 4, 6)}, eye1 {count(V['m1'], 7, 9)}; motor A then {count(V['m0'], 4, 4.4)/0.4:.0f}/s {count(V['m0'], 7, 7.4)/0.4:.0f}/s")
