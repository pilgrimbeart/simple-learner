import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge_poison
seeds = range(7100, 7124)
R = dict(scan=16, drive=160, hold=0.05, learn="toggle", n=2, blame="any", forget=1.5, bored=3.0, roam=1.0, roam_rate=20)
tries = [R, dict(R, every=2.0, roam=0.2, roam_rate=60), dict(R, every=2.0, roam=0.5, roam_rate=20), dict(R, every=4.0, roam=1.0, roam_rate=20)]
with ProcessPoolExecutor(2) as ex:
    for p in tries:
        r = judge_poison("hold_drive", p, seeds, 100, ex)
        print(f"every {p.get('every')} roam {p['roam']} at {p['roam_rate']}  eff {r['eff']:5.2f} gain {r['gain']:4.1f} food {r['food']:4.1f} poison {r['poison']:3.1f} last {r['last']:3.1f} str {r['stranded']:3.0%} {r['job']}", flush=True)
