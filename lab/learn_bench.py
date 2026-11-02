import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from discrete.circuits import learn_hold
from discrete.life import bench
kw = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
n = learn_hold(None, **kw)
pul = [("poison", 0.5), ("poison", 0.6), (0, 0.9), (1, 1.1), ("food", 1.4), ("poison", 1.6), (0, 2.0), (1, 2.2),
       ("poison", 4.0), ("poison", 4.15), (0, 4.5), (1, 4.7)]
nodes = ["s0", "s1", "h", "q", "w1", "w", "m1"]
t, V, P = bench(n, 5.0, nodes, pulses=pul, step=1e-5)
for tt in (0.4, 0.55, 0.7, 0.92, 1.0, 1.12, 1.2, 1.5, 1.7, 2.02, 2.22, 3.9, 4.1, 4.3, 4.52, 4.72, 4.9):
    k = np.searchsorted(t, tt)
    print(f"t {tt:.2f}  " + "  ".join(f"{x} {V[x][k]:.2f}" for x in nodes))
print(f"power {P*1e9:.1f} nW, parts {n.parts()}")
