import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge_poison
seeds = range(7100, 7124)
B = dict(learn="toggle", n=2, blame="held", bored=2.0, roam=1.0, roam_rate=80)
R = dict(B, scan=32, k=8, hold=0.1)
tries = [("reflex_hold", dict(R, bored=b, roam=r, roam_rate=v, avoid=a)) for b, r, v, a in
         ((3, 1, 40, 0), (3, 1, 40, 2), (3, 1, 20, 0), (3, 2, 20, 0), (4, 1, 40, 0), (2, 1, 20, 0), (3, 2, 40, 2), (5, 2, 40, 2))]
with ProcessPoolExecutor(3) as ex:
    for kind, p in tries:
        r = judge_poison(kind, p, seeds, 100, ex)
        d = {k: v for k, v in p.items() if k not in ("learn", "blame") }
        print(f"{kind:11s} {str(d):95s} eff {r['eff']:5.2f} gain {r['gain']:4.1f} food {r['food']:4.1f} poison {r['poison']:3.1f} last {r['last']:3.1f} str {r['stranded']:3.0%} {r['job']}", flush=True)
