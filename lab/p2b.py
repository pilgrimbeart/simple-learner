"""p2b.py: P2, route B (the user, 2026-11-11: try all three routes, then abstract): evolution learns how to use play's records. The
knob is a readout of the two motors' measures (each its best period's log from its own record, D47): w0 b0 + w1 b1 + c. Nothing about
the body's physics is given: the weights are found by an outer search judged only by food, on training lives, then frozen and tested
with real play on fresh lives.

The search is cheap because a life's challenge depends on play only through the knob it sets: each training body's food from the
challenge's onset (play4's windows, both summed) is measured once at each knob on a grid, with the forager set to that knob from birth;
a readout's fitness is the mean over training lives of that food at the knob it gives, interpolated. Training: seeds 92000+ (20 bodies,
both colours); features from learning-progress play (partners:beats). Test: fresh seeds, real play, the frozen readout, against
partners (our formula) and forage.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/p2b.py train|test [PAIRS]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import play3 as P3
import play4 as P4
import stage3_random as R

GRID = np.round(np.arange(-1.6, 1.61, 0.2), 2)
TRAIN = 92000
OUT = "/home/pilgrim/git/simple-learner/lab/v/p2b_train.pkl"   # (overwritten by each training run)


def features(j):
    from stage2_lang import arms as S
    seed, first = j
    lf = P3.make("partners:beats", seed, first)
    S.live(lf, P4.SECS)
    lN = lf.brain.end_lN
    return (seed, first, None if lN is None or None in lN else (lN[0][0], lN[1][0]))


def food_at(j):
    """Food from onset (both windows, net meals) for a forager set to knob beta from birth, on this life."""
    from stage2_lang import arms as S
    seed, first, beta = j
    lf = P3.make("forage", seed, first)
    p = lf.brain.p
    p["g0"], p["g1"] = math.exp(beta / 2), math.exp(-beta / 2)
    S.live(lf, P4.SECS)
    q = lf.v_q
    lo, hi = q / lf.dt, (q + 300.0) / lf.dt
    good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
    badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
    return (seed, first, beta, good - 2.0 * badm)


def train(n=20):
    lives = [(s, c) for s in range(TRAIN, TRAIN + n) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        feats = list(ex.map(features, lives))
        foods = list(ex.map(food_at, [(s, c, float(b)) for s, c in lives for b in GRID], chunksize=4))
    F = {(s, c): f for s, c, f in feats}
    curve = {}
    for s, c, b, g in foods:
        curve.setdefault((s, c), {})[b] = g
    keys = [k for k in lives if F[k] is not None]
    B = np.array([F[k] for k in keys])
    C = np.array([[curve[k][b] for b in GRID] for k in keys])
    best = None
    for w0 in np.arange(-2, 2.01, 0.1):
        for w1 in np.arange(-2, 2.01, 0.1):
            beta = w0 * B[:, 0] + w1 * B[:, 1]
            for c in np.arange(-1, 1.01, 0.1):
                x = np.clip(beta + c, GRID[0], GRID[-1])
                fit = np.mean([np.interp(x[i], GRID, C[i]) for i in range(len(keys))])
                if best is None or fit > best[0]:
                    best = (fit, round(w0, 2), round(w1, 2), round(c, 2))
    ours = np.mean([np.interp(np.clip(B[i, 0] - B[i, 1], GRID[0], GRID[-1]), GRID, C[i]) for i in range(len(keys))])
    top = np.mean(C.max(1))
    pickle.dump(dict(B=B, C=C, keys=keys, best=best), open(OUT, "wb"))
    print(f"training lives {len(keys)} of {len(lives)} with both records; food from onset (300 s): best knob for each life {top:.1f}, "
          f"our formula {ours:.1f}, at knob 0 {np.mean(C[:, list(GRID).index(0.0)]):.1f}")
    print(f"the search's readout: w0 {best[1]:+.2f}, w1 {best[2]:+.2f}, c {best[3]:+.2f}, food {best[0]:.1f}  (ours: +1, -1, 0)")
    return best


if __name__ == "__main__":
    a = sys.argv[1:]
    import ledger
    ledger.start()
    if a[0] == "train":
        train(int(a[1]) if len(a) > 1 else 20)
