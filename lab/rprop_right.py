"""rprop_right.py: why v3 (lab/rprop.py, Dmax .3) is below the old learner at 1000 s with random thrusters (prediction 17,
lab/v/rprop_fresh3b.log), though it balances as well in the double world. Each life's right balance (log of motor 1's thruster strength
over motor 0's, read from the thrusters' firings: watching, never fed back), its balance x over time, and its gain by thirds.
Thrusters 1000 s, seeds 82150-82159 (17's own). Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_right.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import adaptive as A
import rprop as RP
from stage2_lang.worlds import W as HAND

SEEDS = range(82150, 82160)


def job(j):
    from minimal.spec import COST
    from stage2_lang import arms as S
    arm, seed, first = j
    w = S.world_of(HAND["thrusters"]["text"])
    lf = (A.make(w, seed, first, None, cls=A.RV.RV) if arm == "old"
          else A.make(w, seed, first, {"n_max": 10 ** 9, "Dmax": 0.3}, cls=RP.SZ))
    k = {}
    fire = lf.fire

    def watch(th, gain, by_rule=False):
        k[lf.wire_m[th]] = gain
        return fire(th, gain, by_rule)
    lf.fire = watch
    l = S.live(lf, 1000.0)
    right = float(np.log(k[1] / k[0])) if 0 in k and 1 in k else float("nan")
    return arm, seed, first, right, lf.brain.trace, [a - COST * b for a, b, _ in l]


if __name__ == "__main__":
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        out = list(ex.map(job, [(a, s, c) for a in ("old", "sized3") for s in SEEDS for c in R.COL]))
    print("arm     seed  first  right   x at 100 300 500 1000 s   gain by thirds")
    for arm, seed, first, right, tr, g in out:
        xs = " ".join(f"{min(tr, key=lambda e: abs(e[0] - t0))[1]:+.2f}" for t0 in (100, 300, 500, 1000))
        print(f"{arm:7s} {seed} {first:5s} {right:+.2f}   {xs}   " + " ".join(f"{v:.2f}" for v in g), flush=True)
    for arm in ("old", "sized3"):
        e = np.array([abs(tr[-1][1] - right) for a, _, _, right, tr, _ in out if a == arm])
        print(f"{arm}: |x - right| at 1000 s mean {np.nanmean(e):.2f}, median {np.nanmedian(e):.2f}, over .15 in {np.sum(e > .15)} of {len(e)}")
