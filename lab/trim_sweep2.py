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
    for w, r, rw in ((0.025, 0.002, "pulse"), (0.05, 0.002, "pulse"), (0.05, 0.005, "pulse"), (0.1, 0.002, "pulse"), (0.05, 0.02, "meal"), (0.1, 0.02, "meal")):
        run(ex, f"approach {rw} w{w} r{r}", lambda s, w=w, r=r, rw=rw: dict(base, balance=1.0, knob="balance", wobble=w, period=1, rate=r, lo=0.5, hi=2.0, reward=rw, dither="approach"))
