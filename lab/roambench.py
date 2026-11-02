import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import bench, RISE, FALL
step = float(sys.argv[1]); kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:])}
build, supply = CIRCUITS["learn_hold"]
seed = int(kw.pop("seed", 0)); net = build(np.random.default_rng(seed + 5_000_011), **kw)
t, V, p = bench(net, 30.0, ["h", "g2", "a2", "m1", "m0"], supply, [], step)
def fires(x):
    armed, n = True, 0
    for v in x:
        if armed and v > RISE * supply: n += 1; armed = False
        elif v < FALL * supply: armed = True
    return n
up = V["h"] > 2.0
edges = np.flatnonzero(np.diff(up.astype(int)) == 1)
downs = np.flatnonzero(np.diff(up.astype(int)) == -1)
dur = [t[d] - t[e] for e in edges for d in downs[downs > e][:1]]
print(f"step {step:g} {kw}: roams (h>2V) {len(edges)} in 30 s at {np.round(t[edges],2)[:8]}, each {np.round(dur,3)[:8]} s; "
      f"m1 {fires(V['m1'])} m0 {fires(V['m0'])}; h max {V['h'].max():.2f}; power {p*1e9:.0f} nW")
