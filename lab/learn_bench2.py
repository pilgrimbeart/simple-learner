import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from discrete.circuits import learn_hold
from discrete.life import bench
kw = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
n = learn_hold(None, **kw)
nodes = ["s0", "s1", "b0", "b1", "j0", "j1", "h", "w"]
t, V, P = bench(n, 0.6, nodes, pulses=[(1, 0.3), (0, 0.45)], step=2e-6)
for tt in (0.29, 0.3001, 0.3005, 0.301, 0.302, 0.3024, 0.3027, 0.303, 0.305, 0.31, 0.35, 0.44, 0.4501, 0.451, 0.4526, 0.46, 0.5, 0.55, 0.6):
    k = np.searchsorted(t, tt)
    print(f"t {tt:.4f}  " + "  ".join(f"{x} {V[x][k]:.2f}" for x in nodes))
