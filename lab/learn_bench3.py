import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from discrete.circuits import learn_hold
from discrete.life import bench
n = learn_hold(None)
nodes = ["s0", "s1", "s0b", "s1b", "c0", "c1", "h"]
t, V, P = bench(n, 1.0, nodes, pulses=[(0, 0.9)], step=1e-6)
for tt in (0.89, 0.900002, 0.900005, 0.90001, 0.90002, 0.90005, 0.9001, 0.9003, 0.901, 0.9026, 0.91):
    k = np.searchsorted(t, tt)
    print(f"t {tt:.6f}  " + "  ".join(f"{x} {V[x][k]:.2f}" for x in nodes))
