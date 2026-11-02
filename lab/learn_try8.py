import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge_poison
seeds = range(7100, 7124)
R = dict(scan=16, drive=160, hold=0.05, bored=3.0, roam=1.0, roam_rate=20, learn="toggle", n=2, blame="any")
tries = [dict(R, forget=f) for f in (0.5, 1.5, 5.0, 15.0)]
with ProcessPoolExecutor(3) as ex:
    for p in tries:
        r = judge_poison("hold_drive", p, seeds, 100, ex)
        print(f"forget {p['forget']:5.1f} s  eff {r['eff']:5.2f} gain {r['gain']:4.1f} food {r['food']:4.1f} poison {r['poison']:3.1f} last {r['last']:3.1f} str {r['stranded']:3.0%} {r['job']}", flush=True)
