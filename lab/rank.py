"""Policies with poison: the circuit's structure as rules, its options ranked, and the ceiling (oracle)."""
import sys, itertools
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.policies import judge_poison
seeds = range(0, 64)
base = dict(scan=56, drive=56, hold=0.08, learn="toggle", n=2, forget=1.5)
grid = []
roams = {"none": {}, "clock 3+1 @20": dict(bored=3, roam=1, roam_rate=20),
         **{f"give up {b} s @{r}": dict(bored=b, roam=1e9, roam_rate=r, until_seen=1) for b in (3, 6) for r in (20, 56)}}
avoids = {"no avoid": {}, "drop": dict(avoid="drop"), "turn 2": dict(avoid=2)}
for (rn, r), (an, a) in itertools.product(roams.items(), avoids.items()):
    grid.append((f"{rn:16s} {an:9s}", {**base, **r, **a}))
for (rn, r), (an, a) in itertools.product(roams.items(), avoids.items()):
    grid.append((f"ORACLE {rn:16s} {an:9s}", {**base, **r, **a, "n": 10**9, "oracle": 1}))
with ProcessPoolExecutor(8) as ex:
    for name, p in grid:
        r = judge_poison("hold_drive", p, seeds, ex=ex)
        print(f"{name:40s} eff {r['eff']:5.2f} gain {r['gain']:5.2f} food {r['food']:5.2f} poison {r['poison']:5.2f}"
              f" last {r['last']:5.2f} stranded {r['stranded']:4.0%} job {r['job']}", flush=True)
