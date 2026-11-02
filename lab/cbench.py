"""cbench.py CIRCUIT SECONDS NODES k=v...: a CMOS circuit on the bench: each node's range, motor edges per s, power."""
import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.circuits import CIRCUITS
from discrete.life import bench
name, secs, nodes = sys.argv[1], float(sys.argv[2]), sys.argv[3].split(",")
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[4:])}
b, sup = CIRCUITS[name]
n = b(None, **kw)
t, V, p = bench(n, secs, nodes, supply=sup, step=2e-4)
def edges(v):
    c, arm = 0, True
    for x in v:
        if arm and x > 2 / 3 * sup: c += 1; arm = False
        elif x < sup / 3: arm = True
    return c
half = t >= secs / 2
for k in nodes:
    print(f"{k}: {V[k][half].min():.3f}-{V[k][half].max():.3f}  edges/s {edges(V[k][half]) / (secs / 2):.1f}")
print(f"power {p * 1e9:.2f} nW, parts {n.parts()}")
