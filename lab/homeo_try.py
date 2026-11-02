import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge
bodies = {"standard": {}, "weak": {"strength": 0.5}, "strong": {"strength": 2.0}}
base = dict(scan=16, drive=160, hold=0.05)
tries = [("hold_drive", base)] + [("homeo", dict(base, knob="scan", gain=g, memory=10, target=21)) for g in (0.05, 0.1, 0.15)]
seeds = range(4000, 4008)
with ProcessPoolExecutor(2) as ex:
    for kind, p in tries:
        r = {b: judge(kind, p, seeds, 60, ex, f) for b, f in bodies.items()}
        print(kind, p.get("gain"), "  ".join(f"{b} {x['eff']:.2f}/{x['gain']:.1f}" for b, x in r.items()), flush=True)
