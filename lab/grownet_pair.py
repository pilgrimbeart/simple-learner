"""grownet_pair.py: arms of teach.py paired on the same lives, a rung at a time, saved and compared against the first arm (a tool for
confirmations on fresh seeds; teach.py's own table is unpaired). Main session, 2026-11-12.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/grownet_pair.py PAIRS LADDER RUNGS ARM:P,ARM:P,... s92000"""
import os
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R
import teach as T

if __name__ == "__main__":
    a = sys.argv[1:]
    n, lad = int(a[0]), a[1]
    rungs = [int(x) for x in a[2].split(",")]
    arms = [(x.split(":")[0], int(x.split(":")[1])) for x in a[3].split(",")]
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 92000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/grownet_pair{os.environ.get('SECS', '')}_{lad}_{a[2].replace(',', '-')}_{n}_s{s0}_{'-'.join(f"{x}{P}" for x, P in arms)}{'_muscle' if os.environ.get('MUSCLE') == '1' else ''}.pkl"
    secs = {k: float(os.environ.get("SECS", v)) for k, v in L.LADDERS[lad]["rungs"]}   # SECS: every rung this long
    if "report" not in a:
        import ledger
        ledger.start()
        jobs = [(N, arm, P, s, c) for N in rungs for arm, P in [("circuit", 0), ("vtold", 0)] + arms for s in range(s0, s0 + n) for c in L.COL]
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            res = list(ex.map(T.job, [(L.LADDERS[lad]["world"](N), arm, P, s, c, float(secs[N])) for N, arm, P, s, c in jobs], chunksize=2))
        pickle.dump(list(zip(jobs, res)), open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    I = R.boot(n)
    print(f"== paired: {lad} ladder, {n} pairs, seeds {s0}+; share of the gap closed [95%], and each arm against {arms[0][0]}")
    for N in rungs:
        e = {(arm, P): L.scored([r for (nn, aa, pp, _, _), r in rows if nn == N and aa == arm and pp == P], secs[N], I)
             for arm, P in [("circuit", 0), ("vtold", 0)] + arms}
        g = e[("vtold", 0)][1] - e[("circuit", 0)][1]
        line = f"  rung {N:2d}:"
        for arm, P in arms:
            x = (e[(arm, P)][1] - e[("circuit", 0)][1]) / g
            line += f" {arm}:{P} {np.median(x):+.2f} [{np.percentile(x, 2.5):+.2f},{np.percentile(x, 97.5):+.2f}]"
            if (arm, P) != arms[0]:
                d = (e[(arm, P)][1] - e[arms[0]][1]) / g
                line += f" (vs {arms[0][0]} {np.median(d):+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}])"
            line += " |"
        print(line, flush=True)
