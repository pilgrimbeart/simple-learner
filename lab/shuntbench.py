import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import bench
step = float(sys.argv[1])
build, supply = CIRCUITS["learn_hold"]
net = build(np.random.default_rng(5_050_011), roam=False)
# latch state at rest decides which eye is shunted; pulse each eye in turn, 20 pulses 50 ms apart
pulses = [(0, 2.0 + 0.05 * k) for k in range(20)] + [(1, 6.0 + 0.05 * k) for k in range(20)]
t, V, p = bench(net, 10.0, ["c0", "c1", "h", "s0", "s1"] + list(dict.fromkeys(net.motor)), supply, pulses, step)
for a, b, lab in ((0.5, 1.9, "rest"), (2.0, 3.0, "eye0"), (6.0, 7.0, "eye1")):
    k = (t >= a) & (t < b)
    print(f"{lab}: c0 {V['c0'][k].mean():.2f} c1 {V['c1'][k].mean():.2f} h max {V['h'][k].max():.2f} mean {V['h'][k].mean():.2f}  s0 max {V['s0'][k].max():.2f} s1 max {V['s1'][k].max():.2f}")
