import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from units import TICK

def one(job):
    from creature import Life
    from discrete.policies import Policy
    from discrete.bodies import vary
    kind, p, seed, seconds, body = job
    box = {}
    def mk(s):
        box["p"] = Policy(s, kind, **p); return box["p"]
    lf = Life(seed, None, brain=mk)
    if body: vary(lf, body)
    while lf.t < int(seconds / TICK): lf.step()
    return box["p"].knob_trace

bodies = {"standard": {}, "weak": {"strength": 0.5}, "strong": {"strength": 2.0}}
p = dict(scan=16, drive=160, hold=0.05, knob="scan", wobble=0.3, period=10, rate=0.02, lo=4, hi=64)
if len(sys.argv) > 1: p.update(eval(sys.argv[1]))
with ProcessPoolExecutor(2) as ex:
    for b, f in bodies.items():
        tr = list(ex.map(one, [(p.get("kind", "lockin"), p, s, 300, f) for s in range(4000, 4012)]))
        tr = np.array(tr)
        print(b, "geo-mean knob at 50/100/200/300 s:", [round(float(np.exp(np.log(tr[:, k]).mean())), 1) for k in (49, 99, 199, 297)],
              "spread at 100 s (sd of log):", round(float(np.log(tr[:, 99]).std()), 2), flush=True)
