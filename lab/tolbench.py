import sys, time, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import bench, RISE, FALL
step = float(sys.argv[1]); opts = " ".join(sys.argv[2:])
build, supply = CIRCUITS["learn_hold"]
net = build(np.random.default_rng(1 + 5_000_011))
if opts:
    orig = net.text
    net.text = lambda s: orig(s) + [".options " + opts]
def fires(x):
    armed, n = True, 0
    for v in x:
        if armed and v > RISE * supply: n += 1; armed = False
        elif v < FALL * supply: armed = True
    return n
t0 = time.time()
t, V, p = bench(net, 30.0, ["h", "m1", "m0"], supply, [], step)
print(f"step {step:g} [{opts}]: m0 {fires(V['m0'])} m1 {fires(V['m1'])} points {len(t)} wall {time.time()-t0:.0f}s")
