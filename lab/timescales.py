"""timescales.py: does the best hold, boredom or scan differ between weak and strong bodies? B, tolerances, bodies
(each thruster 0.5-2, the drive balanced by the oracle), seeds 0-127 x 2, grouped by strength (sqrt(left x right))."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from discrete.bodies import THRUSTERS, draw
from minimal.spec import efficiency
D = "/home/pilgrim/git/simple-learner/lab/m2/"
B = {**json.load(open(D + "B.json")), "vary": 1, "body": 1, "oracle": 1}
seeds = range(128)
k = np.array([np.sqrt(draw(s, THRUSTERS)["left"] * draw(s, THRUSTERS)["right"]) for s in seeds])
cut = np.quantile(k, [1 / 3, 2 / 3])
group = np.digitize(k, cut)                              # 0 weak, 1 middling, 2 strong
with ProcessPoolExecutor(4) as ex:
    for name, vals in (("hold", (0.1, 0.2, 0.4)), ("bored", (3.0, 6.0, 12.0)), ("scan", (8.0, 12.3, 18.0)),
                       ("drive", (30.0, 44.4, 65.0))):
        row = []
        for v in vals:
            L = cmodel4.lives({**B, name: v}, seeds, ex=ex)
            row.append([efficiency([l for i, l in enumerate(L) if group[i // 2] == g]) for g in range(3)])
        row = np.array(row)
        print(f"{name:6s}", "  ".join(f"{g}: " + " ".join(f"{x:5.2f}" for x in row[:, j]) + f" best {vals[int(np.argmax(row[:, j]))]}"
                                      for j, g in enumerate(("weak", "mid", "strong"))), flush=True)
