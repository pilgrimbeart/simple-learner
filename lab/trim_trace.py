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
    vary(lf, body)
    while lf.t < int(seconds / TICK): lf.step()
    return box["p"].knob_trace, lf.motor["left"] == 0

base = dict(scan=16, drive=160, hold=0.05, balance=1.0, knob="balance", lo=0.5, hi=2.0)
p = dict(base, **eval(sys.argv[1]))
with ProcessPoolExecutor(3) as ex:
    for a in (1.25, 0.8):
        res = list(ex.map(one, [("lockin", p, s, 200, {"asymmetry": a}) for s in range(4000, 4012)]))
        right = []
        for tr, left0 in res:
            want = -0.5 * np.log(a) if left0 else 0.5 * np.log(a)     # log balance that evens the thrust
            got = np.log(tr)
            right.append([np.sign(got[k]) == np.sign(want) for k in (24, 49, 99, 197)])
            print(f"a {a} want {want:+.2f}  got at 25/50/100/200 s", " ".join(f"{got[k]:+.2f}" for k in (24, 49, 99, 197)))
        print("right sign share at 25/50/100/200 s:", np.mean(right, axis=0), flush=True)
