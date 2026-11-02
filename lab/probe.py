"""probe.py CIRCUIT SEED POISON OUT [k=v ...]: one life with its nodes recorded, then a summary in 4 s windows."""
import sys, pickle, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import hunger  # noqa: F401
from discrete.circuits import CIRCUITS
from discrete.life import live
name, seed, poison, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
params = {k: float(v) for k, v in (a.split("=") for a in sys.argv[5:])}
build, supply = CIRCUITS[name]
net = build(np.random.default_rng(seed + 5_000_011), **params)
probe = ["h", "c0", "c1", "q", "s0", "s1"] + [p for p in ("u", "ub", "g2") if p in " ".join(net.text(supply))]
r = live(net, seed, 100.0, supply, poison=poison, probe=probe, record=True)
r["probe"] = probe
pickle.dump(r, open(out, "wb"))
tr = np.array(r["trace"]); meals = r["meals"]
for t0 in range(0, 100, 4):
    a, b = t0 * 100, (t0 + 4) * 100
    seg = tr[a:b]
    m = [c[0] for t, c in meals if a <= t < b]
    nf = [sum(1 for x in r["fired"] if a <= x[0] < b and x[1] == k) for k in ("left", "right")]
    print(f"{t0:3d}s meals {''.join(m) or '-':8s} fired {nf} seen {np.mean(r['seen'][a:b]):.2f} "
          + " ".join(f"{p} {seg[:, i].min():.2f}-{seg[:, i].max():.2f}" for i, p in enumerate(probe)))
