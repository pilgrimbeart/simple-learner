"""Last third's gain rate (food - COST poison per SPAN), each arm and paired differences, bootstrap over seeds."""
import sys, pickle, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal.spec import COST, SPAN
V = sys.argv[1]
def per(f):
    L = pickle.load(open(V + f + ".lives", "rb"))
    g = np.array([(l[2][0] - COST * l[2][1]) * SPAN / l[2][2] for l in L])
    return g[0::2] + g[1::2]
rng = np.random.default_rng(0)
def ci(x):
    b = x[rng.integers(len(x), size=(4000, len(x)))].mean(1) / 2
    return f"{x.mean()/2:+.2f} [{np.percentile(b,2.5):+.2f}, {np.percentile(b,97.5):+.2f}]"
arms = sys.argv[2:]
G = {a: per(a) for a in arms}
for a in arms: print(f"{a:40s} {ci(G[a])}")
base = arms[0]
for a in arms[1:]: print(f"  {a} - {base}: {ci(G[a]-G[base])}")
