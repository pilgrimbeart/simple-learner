import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import bench
step = float(sys.argv[1])
build, supply = CIRCUITS["learn_hold"]
net = build(np.random.default_rng(5_050_011))
pulses = [("poison", 1.0), ("poison", 1.5), ("poison", 4.0), ("food", 4.3), ("poison", 4.6),
          ("poison", 7.0), ("poison", 7.2), ("poison", 7.4)]
t, V, p = bench(net, 10.0, ["c0", "c1", "q", "w"], supply, pulses, step)
for tt in (0.9, 1.2, 1.4, 1.7, 2.5, 3.9, 4.2, 4.5, 4.8, 6.9, 7.1, 7.3, 7.6, 9.9):
    i = np.searchsorted(t, tt)
    print(f"t {tt:4.1f} c0 {V['c0'][i]:.2f} c1 {V['c1'][i]:.2f} q {V['q'][i]:.2f} w {V['w'][i]:.2f}")
print("min q", V["q"].min(), "min w", V["w"].min())
