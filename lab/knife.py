"""knife.py: how steep is the score in the balance knob? (D52's knife-edge, the reason for the muscle-like body.) The starting brain with
its balance knob set to the right value plus an error, on plain bodies (right: 0) and lopsided ones (right: the told balance, the
body's own: bodyladder.make's toldbody), for both bodies (MUSCLE=1 for the new). 300 s lives, efficiency in the last third.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 [MUSCLE=1] .venv/bin/python lab/knife.py [PAIRS]"""
import math
import os
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import bodyladder as BL
import ladders as L
import stage3_random as R

ERRS = (0.0, 0.03, 0.1, 0.2, 0.4)
SEEDS0 = 86000


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    body, err, sign, seed, first = j
    text = L.PLAIN if body == "plain" else BL.WORLDS["thr"][0]
    lf = BL.make(text, "toldbody", seed, first)        # (on a plain body the told balance is 0)
    p = lf.brain.p
    right = math.log(p["g0"] / p["g1"]) if body == "lopsided" else 0.0
    b = right + sign * err
    p["g0"], p["g1"] = math.exp(b / 2), math.exp(-b / 2)
    l = S.live(lf, 300.0)
    g = [a - COST * c for a, c, _ in l]
    sp = spent(l)
    return (0.0, 0.0, g[2], sp * l[2][2] / sum(t for _, _, t in l))      # (ladders.scored reads the last third from 2 and 3)


if __name__ == "__main__":
    import ledger
    ledger.start()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seeds = range(SEEDS0, SEEDS0 + n)
    I = R.boot(n)
    print(f"== {'muscle-like' if os.environ.get('MUSCLE') == '1' else 'world.py'} body: efficiency in the last third against the knob's error, {n} pairs, 300 s")
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for body in ("plain", "lopsided"):
            line = f" {body:8s}"
            for err in ERRS:
                signs = (1.0,) if err == 0 else (1.0, -1.0)
                res = [list(ex.map(job, [(body, err, sg, s, c) for s in seeds for c in L.COL])) for sg in signs]
                e = [L.scored(r, 300.0, I) for r in res]
                m = float(np.mean([x[0] for x in e]))
                line += f" | {err:.2f}: {m:+.2f}"
            print(line, flush=True)
