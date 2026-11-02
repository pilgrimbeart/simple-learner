import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from discrete.policies import life, Policy
from discrete.bodies import draw
from minimal.spec import efficiency, gain

def wiring(seed):
    from creature import Life
    lf = Life(seed, None, brain=lambda s: Policy(s, "straight", rate=1))
    return lf.motor["left"] == 0

base = dict(scan=16, drive=160, hold=0.05)
seconds = float(sys.argv[1])
seeds = list(range(6000, 6024))
A = {s: draw(s, {"asymmetry": 1.25})["asymmetry"] for s in seeds}
W = {s: wiring(s) for s in seeds}
def run(ex, name, mk):
    def job(s):
        p = mk(s)
        return (p.pop("kind", "lockin" if "knob" in p else "hold_drive"), p, s, seconds, None, {"asymmetry": A[s]})
    L = list(ex.map(life, [job(s) for s in seeds]))
    print(f"{name:34s} eff {efficiency(L):.2f} gain {gain(L):.1f}", flush=True)
with ProcessPoolExecutor(3) as ex:
    run(ex, "fixed", lambda s: dict(base))
    run(ex, "oracle trim", lambda s: dict(base, balance=A[s] ** (-0.5 if W[s] else 0.5)))
    for r, f, sl, m in ((0.005, 5, 20, 0.1), (0.002, 10, 40, 0.1), (0.005, 3, 15, 0.2)):
        run(ex, f"tumble r{r} fast{f} slow{sl} m{m}", lambda s, r=r, f=f, sl=sl, m=m: dict(base, kind="tumble", balance=1.0, knob="balance", rate=r, fast=f, slow=sl, margin=m, lo=0.7, hi=1.4))
