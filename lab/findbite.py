"""findbite.py: run the arena with growers and report, for a grower with a turn kept, the ticks around a bite: heading, pain, firings."""
import sys, math
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import grow_escape as G
import arena as AR
import numpy as np
A = AR.Arena(1, 10, ("grow", "tracker"))
log = {}
for k in range(6000):
    before = {id(r): r.body.heading for r in A.robots}
    A.step()
    for r in A.robots:
        if r.kind == "grow" and getattr(r.brain, "kept", "none") in ("m0", "m1") and A.t > 30:
            log.setdefault(id(r), []).append((round(A.t, 2), r.brain.hurting, r.brain.op, round(math.degrees(r.body.heading - before.get(id(r), r.body.heading)), 1)))
for rid, L in log.items():
    on = [i for i in range(1, len(L)) if L[i][1] and not L[i - 1][1]]
    if on:
        i = on[0]
        for row in L[i - 3:i + 40:3]:
            print(row)
        print("turn over 0.5 s after the bite: %.0f degrees" % sum(x[3] for x in L[i:i + 50]))
        print("pain lasted %.2f s" % (next((j for j in range(i, len(L)) if not L[j][1]), len(L)) - i) * 1)
        break
