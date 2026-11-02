import sys, pickle, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import live
seed, poison = int(sys.argv[1]), sys.argv[2]
build, supply = CIRCUITS["learn_hold"]
net = build(np.random.default_rng(seed + 5_000_011))
probe = ["h", "c0", "c1", "g2", "q", "w", "s0", "s1"]
r = live(net, seed, 100.0, supply, poison=poison, probe=probe, record=True)
r["probe"] = probe
pickle.dump(r, open(f"{sys.argv[3]}", "wb"))
print(seed, poison, len(r["meals"]), r["firings"])
