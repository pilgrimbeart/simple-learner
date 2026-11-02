import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from discrete.policies import life
from minimal.spec import efficiency, gain

def left_is_motor0(seed):
    from creature import Life
    lf = Life(seed, None, brain=lambda s: None) if False else None
    return None

def wiring(seed):
    from creature import Life
    from discrete.policies import Policy
    lf = Life(seed, None, brain=lambda s: Policy(s, "straight", rate=1))
    return lf.motor["left"] == 0

base = dict(scan=16, drive=160, hold=0.05)
seeds = list(range(4000, 4016))
W = {s: wiring(s) for s in seeds}
bodies = {"standard": 1.0, "left x1.25": 1.25, "right x1.25": 0.8}
def run(ex, name, mk):
    out = []
    for b, a in bodies.items():
        jobs = [("hold_drive" if "knob" not in mk(s, a) else "lockin", mk(s, a), s, 100, None, {"asymmetry": a}) for s in seeds]
        L = list(ex.map(life, jobs))
        out.append(f"{b} {efficiency(L):.2f}/{gain(L):.1f}")
    print(f"{name:28s}", "  ".join(out), flush=True)
with ProcessPoolExecutor(3) as ex:
    run(ex, "fixed", lambda s, a: base)
    run(ex, "oracle trim", lambda s, a: dict(base, balance=a ** (-0.5 if W[s] else 0.5)))
    for w, T, r in ((0.15, 4, 0.01), (0.15, 4, 0.02), (0.25, 4, 0.02), (0.15, 10, 0.02)):
        run(ex, f"lockin w{w} T{T} r{r}", lambda s, a, w=w, T=T, r=r: dict(base, balance=1.0, knob="balance", wobble=w, period=T, rate=r, lo=0.5, hi=2.0))
