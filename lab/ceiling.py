"""The ceiling: the oracle policy (told from birth which sensor sees food) over its settings, poison ahead dropping
the hold; and the same grid learning (toggle, n 2) if argv[1] == 'learn'."""
import sys, itertools
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.policies import judge_poison
learn = len(sys.argv) > 1 and sys.argv[1] == "learn"
seeds = range(0, 64)
roams = {"clock 3+1@20": dict(bored=3, roam=1, roam_rate=20), "give up 3@20": dict(bored=3, roam=1e9, roam_rate=20, until_seen=1)}
with ProcessPoolExecutor(8) as ex:
    for (rn, r), scan, drive, hold in itertools.product(roams.items(), (8, 16, 32, 56), (40, 80, 160), (0.05, 0.1, 0.2)):
        p = dict(scan=scan, drive=drive, hold=hold, learn="toggle", avoid="drop", **r)
        p.update(dict(n=2, forget=1.5) if learn else dict(n=10**9, oracle=1))
        x = judge_poison("hold_drive", p, seeds, ex=ex)
        print(f"{rn} scan {scan:3d} drive {drive:3d} hold {hold:.2f}  eff {x['eff']:5.2f} gain {x['gain']:5.2f} food {x['food']:5.2f}"
              f" poison {x['poison']:5.2f} last {x['last']:5.2f} stranded {x['stranded']:4.0%} job {x['job']}", flush=True)
