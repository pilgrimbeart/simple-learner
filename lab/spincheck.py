"""spincheck.py: at each bite's onset on a tracker, its mode (driving or not) and its spin, signed so + is the way motor 0 turns it."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import arena as AR, world as W
from units import TICK
rows = []
for seed in range(6):
    A = AR.Arena(seed, 10, ("tracker",))
    hurt = {}
    for _ in range(20000):
        A.step()
        for r in A.robots:
            h = r.lost
            if h > hurt.get(id(r), h) and not getattr(r, "_was", False):
                sign = W.TURN if r.motor["right"] == 0 else -W.TURN   # motor 0's thruster: right turns it left (+spin)
                b = r.brain
                rows.append((b.t - b.last_drive < b.p["hold"], r.body.spin * np.sign(sign)))
            r._was = h > hurt.get(id(r), h)
            hurt[id(r)] = h
rows = np.array(rows)
d = rows[:, 0] > 0
print(f"bites {len(rows)}; driving at onset {d.mean():.0%}")
print(f"spin the way motor 0 turns, mean (rad/s): driving {rows[d, 1].mean():+.2f}, not driving {rows[~d, 1].mean():+.2f}; "
      f"share spinning motor 0's way {np.mean(rows[:, 1] > 0):.0%}")
