import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np, arena as AR, world as W
from units import TICK
A = AR.Arena(0, 10, ("told", "tracker")); ov, touch, ticks, bites = [], 0, 0, 0
for _ in range(int(200 / TICK)):
    A.step(); ticks += 1
    P = np.array([r.body.pos for r in A.robots]); d = W.Body.wrap(P[:, None] - P[None]); dist = np.hypot(d[..., 0], d[..., 1])
    iu = np.triu_indices(len(P), 1); o = 2 * AR.RB - dist[iu]; o = o[o > 0]
    if len(o): touch += 1; ov += list(o)
ov = np.array(ov) * 1e3
print(f"touching in {touch / ticks:.0%} of ticks; overlap median {np.median(ov):.2f} mm, 99th {np.percentile(ov, 99):.2f}, max {ov.max():.2f} (disc {2*AR.RB*1e3:.0f} mm across); deaths {len(A.dead)}")
