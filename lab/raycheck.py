import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import arena_watch as V
from arena import Arena, _fan, LEFT, HIT, R
import world as W
A = Arena(0, 10, ("told", "tracker"))
worst, hits = 0.0, 0
for t in range(3000):
    A.step()
    if t % 50: continue
    for r in A.robots:
        others = [d for o in A.robots if o is not r for d in o.discs()]
        xy = np.array([c for c, _ in others]); kind = np.array([k for _, k in others])
        for ang in (LEFT, -LEFT):
            a = _fan(xy, kind, r.body.head(), r.body.heading, ang, R, W.RANGE, W.REACH, HIT)
            s = [0.0, 0.0]
            for _, d, k in V.rays(A, r, ang):
                if k >= 0: s[k] += HIT / (1 + (d / W.REACH) ** 2); hits += 1
            worst = max(worst, abs(np.minimum(s, 1) - a).max())
print("largest difference", worst, "ray hits", hits)
