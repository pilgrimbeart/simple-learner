"""grownet_noharm.py: the scaling test's fourth part for a growing brain: where there is nothing to learn (the plain world, the all-food
world), does it cost anything, at each size of material? Paired against the starting brain, efficiency in the whole of 100 s lives.
Main session, 2026-11-13.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/grownet_noharm.py ARM PAIRS s88000"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R
import teach as T

WORLDS = {"plain": L.PLAIN, "allfood": "(world (meta (link L7) (q H) (cap DoNoHarm) (group control)) (on tick (set poison -1)))"}

if __name__ == "__main__":
    a = sys.argv[1:]
    arm, n = a[0], int(a[1])
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 88000)
    Ps = (40, 160, 640, 2560)
    import ledger
    ledger.start()
    jobs = [(w, x, P, s, c) for w in WORLDS for x, P in [("circuit", 0)] + [(arm, P) for P in Ps] for s in range(s0, s0 + n) for c in L.COL]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        res = list(ex.map(T.job, [(WORLDS[w], x, P, s, c, 100.0) for w, x, P, s, c in jobs], chunksize=2))
    rows = list(zip(jobs, res))
    I = R.boot(n)
    print(f"== doing no harm: {arm} against the starting brain, {n} pairs, seeds {s0}+, 100 s lives, whole-life efficiency [95%]")
    for w in WORLDS:
        b = L.scored([r for (ww, x, _, _, _), r in rows if ww == w and x == "circuit"], 100.0, I)
        line = f"  {w:8s} starting {b[0]:+.2f} |"
        for P in Ps:
            e = L.scored([r for (ww, x, p, _, _), r in rows if ww == w and x == arm and p == P], 100.0, I)
            d = e[1] - b[1]
            line += f" P{P} {e[0] - b[0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}] |"
        print(line, flush=True)
