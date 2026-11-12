"""knife_play4.py: is D52's knife-edge real? D52 measured, in play4's frame (a quiet spell, then food from 400 to 600 s; gain from onset),
that a plain body's knob off by .03 cost .9 of 4.2 (10 pairs, seeds 98000+); lab/knife.py (efficiency in the last third of 300 s lives
from birth) found .03 costing nothing. Here D52's frame on fresh seeds, both signs of each error, 20 pairs, the old body.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/knife_play4.py [PAIRS]"""
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import couple_search as CS
import play4 as P4
import stage3_random as R

ERRS = (0.0, 0.03, 0.1)
SEEDS0 = 100000


def job(j):
    from stage2_lang import arms as S
    b, seed, first = j
    lf = CS.make("forage", "plain", seed, first)
    lf.brain.p["g0"], lf.brain.p["g1"] = math.exp(b / 2), math.exp(-b / 2)
    S.live(lf, P4.SECS)
    q = lf.v_q
    lo, hi = q / lf.dt, (q + 300.0) / lf.dt
    good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
    badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
    return (good - 2.0 * badm) / 30.0


if __name__ == "__main__":
    import ledger
    ledger.start()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    I = R.boot(n)
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        base = None
        for err in ERRS:
            vals = []
            for sg in ((1.0,) if err == 0 else (1.0, -1.0)):
                vals.append(np.array(list(ex.map(job, [(sg * err, s, c) for s in range(SEEDS0, SEEDS0 + n) for c in ("red", "blue")]))))
            v = np.mean(vals, axis=0)
            if base is None:
                base = v
            d = v[I].mean(1) - base[I].mean(1)
            print(f"knob error {err:.2f}: gain from onset {v.mean():+.2f} a 10 s; against 0: {v.mean() - base.mean():+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]", flush=True)
