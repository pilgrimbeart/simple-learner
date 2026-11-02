import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge_poison
seeds = range(7100, 7124)
R = dict(scan=32, k=8, hold=0.1, bored=3.0, roam=1.0, roam_rate=20)
tries = [dict(R, learn="toggle", n=2, blame="held")]
for tau in (0.05, 0.1, 0.2):
    tries += [dict(R, learn="trace", tau=tau, latch=True, poison_only=True)]
with ProcessPoolExecutor(3) as ex:
    for p in tries:
        r = judge_poison("reflex_hold", p, seeds, 100, ex)
        d = {k: v for k, v in p.items() if k not in R}
        print(f"{str(d):55s} eff {r['eff']:5.2f} gain {r['gain']:4.1f} food {r['food']:4.1f} poison {r['poison']:3.1f} last {r['last']:3.1f} str {r['stranded']:3.0%} {r['job']}", flush=True)
