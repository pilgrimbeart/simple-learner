import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge_poison
seeds = range(7100, 7124)
tries = []
for kind, base in (("reflex_hold", dict(scan=32, k=8, hold=0.1)), ("hold_drive", dict(scan=16, drive=160, hold=0.05))):
    R = dict(base, bored=3.0, roam=1.0, roam_rate=20)
    tries += [(kind, dict(R, learn="toggle", n=n, blame=b)) for n, b in ((1, "any"), (1, "held"), (2, "any"), (2, "held"))]
with ProcessPoolExecutor(3) as ex:
    for kind, p in tries:
        r = judge_poison(kind, p, seeds, 100, ex)
        print(f"{kind:11s} n{p['n']} blame {p['blame']:4s} eff {r['eff']:5.2f} gain {r['gain']:4.1f} food {r['food']:4.1f} poison {r['poison']:3.1f} last {r['last']:3.1f} str {r['stranded']:3.0%} {r['job']}", flush=True)
