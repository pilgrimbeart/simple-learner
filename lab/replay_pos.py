"""replay_pos.py REC POISON: a recorded life's firings replayed through the same body, its path printed."""
import sys, pickle, collections, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from creature import Life
r = pickle.load(open(sys.argv[1], "rb"))
by = collections.defaultdict(list)
for t, f in r["fired"]:
    by[t].append(f)
class Stub:
    def stimulate(self, *a): pass
    def taste(self, *a): pass
    def step(self): return [lf.motor[f] for f in by[lf.t]]
lf = Life(r["seed"], sys.argv[2], brain=lambda s: Stub())
path = []
while lf.t < 10000:
    lf.step()
    path.append(lf.body.pos.copy())
print("meals match:", [(int(a), b) for a, b in lf.meals] == r["meals"])
b = lf.body
print({k: getattr(b, k) for k in vars(b) if k in ("heading", "angle", "theta", "vel", "spin", "omega")})
for t in range(48, 100, 4):
    p = path[t * 100]
    print(t, "s", np.round(p * 1000, 1))
