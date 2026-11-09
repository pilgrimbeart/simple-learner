"""stageR_plain_trace.py: the scaling test found every bank arm, the written one included, surely below base in plain at 10,000 s
(-.40 [-.60,-.20], lab/v/stageR_scale.log), where at 100 s it is +.08. When does the loss appear? Main session, 2026-11-08.

Plain, base against the written bank, the scaling test's seeds (81400-81409 x red/blue), 1.25 ms, last third, lives of 300, 1000 and 3000 s
(10,000 s from the scaling test itself).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stageR_plain_trace.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import stageR_scale as X


def job(j):
    secs, arm, seed, first = j
    X.SECS = secs
    return X.job((R.PLAIN, arm, seed, first))


if __name__ == "__main__":
    I = R.boot(len(X.SEEDS), 20000)
    D = R._load(X.KEY)["plain"]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for secs in (300.0, 1000.0, 3000.0, 10000.0):
            if secs == 10000.0:
                L = {a: D[a] for a in ("base", "written")}
            else:
                L = {a: list(ex.map(job, [(secs, arm, s, c) for s in X.SEEDS for c in R.COL])) for a, arm in (("base", "circuit"), ("written", "bank"))}
            b, k = M.boot_eff(L["base"], I, True), M.boot_eff(L["written"], I, True)
            lo, hi = np.percentile(k[1] - b[1], [2.5, 97.5])
            print(f"{secs:6.0f} s  base {b[0]:.3f}  written {k[0]:.3f}  written - base {k[0] - b[0]:+.3f} [{lo:+.3f},{hi:+.3f}]", flush=True)
