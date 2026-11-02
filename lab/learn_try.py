import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import itertools
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge_poison
seeds = range(7000, 7012)
tries = []
for base in (("reflex_hold", dict(scan=32, k=8, hold=0.1)), ("hold_drive", dict(scan=16, drive=160, hold=0.05))):
    for n, roam in itertools.product((1, 2), (None, (1.0, 0.5), (2.0, 1.0), (0.5, 0.5))):
        p = dict(base[1], learn="toggle", n=n)
        if roam:
            p.update(bored=roam[0], roam=roam[1], roam_rate=80)
        tries.append((base[0], p))
with ProcessPoolExecutor(3) as ex:
    for kind, p in tries:
        r = judge_poison(kind, p, seeds, 100, ex)
        print(f"{kind:12s} n{p['n']} roam {p.get('bored')}/{p.get('roam')}  eff {r['eff']:5.2f} gain {r['gain']:5.1f} food {r['food']:5.1f} poison {r['poison']:4.1f} last {r['last']:4.1f} stranded {r['stranded']:4.0%} job {r['job']}", flush=True)
