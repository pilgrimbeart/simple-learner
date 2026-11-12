"""grownet_scale.py: stage 4 of the growing network (PROGRAMME.md): does its size follow what there is to learn? On the pattern lessons (the
sequence ladder: which colour is food follows a secret repeating pattern of n colours, moving on at each good meal), with material
plentiful, the blocks alive at the end of life against n, beside the bits the pattern holds (n, one a colour) and the shortest look-back
that tells every place in the pattern apart (the contexts an ideal learner needs). Predictions: lab/v/grownet_predictions.md, R10, R11.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/grownet_scale.py [PAIRS] [P] [s88000]"""
import os
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R
import teach as T

SECS = 1500.0
SIZES = tuple(int(x) for x in os.environ.get("SIZES", "2,3,5,7,11,13,17").split(","))
ARMS = tuple(os.environ.get("ARMS", "circuit,vtold,net").split(","))


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 10
    P = int(a[1]) if len(a) > 1 and a[1].isdigit() else 256
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 88000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/grownet_scale_{n}_P{P}_s{s0}.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        jobs = [(N, arm, s, c) for N in SIZES for arm in ARMS for s in range(s0, s0 + n) for c in L.COL]
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            res = list(ex.map(T.job, [(L.seq(N), arm, P, s, c, SECS) for N, arm, s, c in jobs], chunksize=2))
        pickle.dump(list(zip(jobs, res)), open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    I = R.boot(n)
    print(f"== does the network's size follow the pattern? {n} pairs, {SECS:.0f} s, P {P}; share of the gap from the starting brain to"
          f" the told one closed in the last third [95%]; blocks alive at the end on the stream chosen (median, quartiles)")
    for N in SIZES:
        e = {arm: L.scored([r for (nn, aa, _, _), r in rows if nn == N and aa == arm], SECS, I) for arm in ARMS}
        g = e["vtold"][1] - e["circuit"][1]
        line = f"  pattern of {N:2d}: starting {e['circuit'][0]:+.2f} told {e['vtold'][0]:+.2f}"
        for arm in ARMS[2:]:
            x = (e[arm][1] - e["circuit"][1]) / g
            b = [r[6][1] for (nn, aa, _, _), r in rows if nn == N and aa == arm]
            line += (f" | {arm} {(e[arm][0] - e['circuit'][0]) / (e['vtold'][0] - e['circuit'][0]):+.2f} [{np.percentile(x, 2.5):+.2f},"
                     f"{np.percentile(x, 97.5):+.2f}] blocks {np.median(b):.0f} ({np.percentile(b, 25):.0f}-{np.percentile(b, 75):.0f})")
        print(line, flush=True)
