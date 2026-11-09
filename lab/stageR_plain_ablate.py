"""stageR_plain_ablate.py: which of the bank's parts makes it wear down over a 10,000 s plain life (lab/v/stageR_plain_trace*.log: goods
fall 18% from the first 1000 s to the last; the balance learner doesn't drift). Each part switched off in turn, as lab/stage3_sense.py
does at 100 s; plain, 10,000 s, seeds 81400-81409 x red/blue (the scaling test's own, so base and the bank are its lives), 1.25 ms,
uncompiled, last third. Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stageR_plain_ablate.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import stageR_scale as X

VARIANTS = ({"eye": 0}, {"jit": 0}, {"pausek": 0}, {"trustk": 0}, {"growk": 0})


def init(dt):
    R._init(dt, False)
    from stage2_lang import arms as S
    S.FAST = False


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    kw, seed, first = j
    l = S.live(S.make(S.world_of(R.PLAIN), "bank", seed, first, kw=dict(kw)), 10000.0)
    g = [a - COST * b for a, b, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))


if __name__ == "__main__":
    I = R.boot(len(X.SEEDS), 20000)
    D = R._load(X.KEY)["plain"]
    b = M.boot_eff(D["base"], I, True)
    k = M.boot_eff(D["written"], I, True)
    print(f"base {b[0]:.3f}; bank {k[0]:.3f}, minus base {k[0] - b[0]:+.3f}   (the scaling test's lives)")
    with ProcessPoolExecutor(7, initializer=init, initargs=(0.00125,)) as ex:
        for kw in VARIANTS:
            L = list(ex.map(job, [(tuple(kw.items()), s, c) for s in X.SEEDS for c in R.COL]))
            e = M.boot_eff(L, I, True)
            lo, hi = np.percentile(e[1] - b[1], [2.5, 97.5])
            print(f"bank {kw}: {e[0]:.3f}, minus base {e[0] - b[0]:+.3f} [{lo:+.3f},{hi:+.3f}]", flush=True)
