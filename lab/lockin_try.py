import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from discrete.policies import judge, Policy, life
bodies = {"standard": {}, "weak": {"strength": 0.5}, "strong": {"strength": 2.0}}
base = dict(scan=16, drive=160, hold=0.05)
tries = [("hold_drive", base)] + [("lockin", dict(base, knob="scan", wobble=w, period=T, rate=r, lo=4, hi=64))
         for w, T, r in ((0.3, 4, 0.02), (0.5, 4, 0.03), (0.3, 10, 0.02), (0.5, 2, 0.05))]
seeds = range(4000, 4008)
with ProcessPoolExecutor(2) as ex:
    for kind, p in tries:
        r = {b: judge(kind, p, seeds, 100, ex, f) for b, f in bodies.items()}
        print(kind, {k: p[k] for k in ("wobble", "period", "rate") if k in p},
              "  ".join(f"{b} {x['eff']:.2f}/{x['gain']:.1f}" for b, x in r.items()), flush=True)
