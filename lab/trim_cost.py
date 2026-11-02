import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from discrete.policies import judge
base = dict(scan=16, drive=160, hold=0.05)
with ProcessPoolExecutor(3) as ex:
    for e in (0, 0.025, 0.05, 0.1, 0.2):
        r = judge("hold_drive", dict(base, balance=float(np.exp(e))), range(4000, 4016), 100, ex)
        print(f"trim error {e:.3f} (log)  eff {r['eff']:.2f} gain {r['gain']:.1f}", flush=True)
