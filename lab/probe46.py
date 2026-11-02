"""probe46.py SEED POISON OUT: learn_avoid with the pruning's first two cuts, one life with nodes recorded, 4 s windows."""
import sys, pickle, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.prune import build
from discrete.life import live
seed, poison, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
net, supply = build("learn_avoid", {}, [(44, "short"), (43, "open")], seed)
probe = ["h", "c0", "c1", "u", "k", "s0", "s1"]
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
