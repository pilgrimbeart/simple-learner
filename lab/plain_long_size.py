"""plain_long_size.py: how large is the old bank's loss in plain over a long life? 10 pairs said -.40 on seeds 81400-81409 and -.08 on
81600-81609 (lab/v/stageR_scale.log, lab/v/adaptive_fresh.log). 30 more pairs, fresh seeds 81700-81729 x red/blue, 10,000 s, 1.25 ms,
last third, base against the old bank; then all 50 pairs pooled. Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/plain_long_size.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import adaptive_fresh as F

if __name__ == "__main__":
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        L = {a: list(ex.map(F.job, [(R.PLAIN, 10000.0, a, s, c) for s in range(81700, 81730) for c in R.COL])) for a in ("base", "old")}
    R._save("plain_long_size", L)
    S, Fr = R._load("Rscale")["plain"], R._load("adaptive_fresh")["plain", 10000.0]
    sets = {"new 30 pairs": L, "pooled 50 pairs": {"base": S["base"] + Fr["base"] + L["base"], "old": S["written"] + Fr["old"] + L["old"]}}
    for name, D in sets.items():
        I = R.boot(len(D["base"]) // 2, 20000)
        b, k = M.boot_eff(D["base"], I, True), M.boot_eff(D["old"], I, True)
        lo, hi = np.percentile(k[1] - b[1], [2.5, 97.5])
        print(f"{name}: base {b[0]:.3f}, old bank {k[0]:.3f}, old - base {k[0] - b[0]:+.3f} [{lo:+.3f},{hi:+.3f}]", flush=True)
