import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from discrete.circuits import learn_hold
from discrete.life import bench
kw = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
n = learn_hold(None, **kw)
t, V, P = bench(n, 12.0, ["h", "a2", "g2", "rbase", "m1"], step=2e-5)
h = V["h"]
up = np.flatnonzero((h[1:] > 2.5) & (h[:-1] <= 2.5))
print("roam starts at", np.round(t[up], 2), " h>2V share", round(float(np.mean(h > 2)), 3), " g2 range", V["g2"].min().round(2), V["g2"].max().round(2), " a2 max", V["a2"].max().round(2), f" power {P*1e9:.0f} nW parts {n.parts()}")
