"""rprop_cost.py: the price of a wobble alone in plain. The sized learner (lab/rprop.py) kept |x| under .1 in plain 10,000 s lives
(lab/v/rprop_trace.log) yet lost .20 against base (lab/v/rprop_fresh.log): is the loss its floor wobble? Arms: base; the bank with x held
at 0 and a wobble of a fixed size (the sized learner told never to move: z huge, give-ups never); and no wobble.
Plain 10,000 s, seeds 81960-81964 (of test 11, which this explains). Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_cost.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import adaptive as A
import rprop as RP

SEEDS = range(81960, 81965)
ARMS = {"base": None, "wob0": 0.0, "wob.02": 0.02, "wob.05": 0.05}


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    arm, seed, first = j
    w = S.world_of(R.PLAIN)
    if arm == "base":
        lf = S.make(w, "circuit", seed, first)
    else:
        s = ARMS[arm]
        lf = A.make(w, seed, first, {"z": 1e9, "n_max": 10 ** 9, "D0": s, "sd_min": s, "sd_max": s}, cls=RP.SZ)
    l = S.live(lf, 10000.0)
    g = [x - COST * y for x, y, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))


if __name__ == "__main__":
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        L = {a: list(ex.map(job, [(a, s, c) for s in SEEDS for c in R.COL])) for a in ARMS}
    I = R.boot(len(SEEDS), 20000)
    e = {a: M.boot_eff(L[a], I, True) for a in ARMS}
    print(f"plain 10,000 s, {len(SEEDS)} pairs, last third")
    for a in ARMS:
        row = f"  {a:7s} {e[a][0]:.3f}"
        for ref in ("base", "wob0"):
            if ref != a:
                lo, hi = np.percentile(e[a][1] - e[ref][1], [2.5, 97.5])
                row += f"   minus {ref} {e[a][0] - e[ref][0]:+.3f} [{lo:+.3f},{hi:+.3f}]"
        print(row, flush=True)
