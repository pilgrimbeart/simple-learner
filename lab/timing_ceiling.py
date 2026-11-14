"""timing_ceiling.py: is timing's plateau near half a ceiling? The designed brain told the slot length but not its phase (ladders.py's
designed arm), on the same lives as a saved grownet_pair.py run, its share of the gap computed against that run's starting and told
brains. Main session, 2026-11-13.

    SECS=3000 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/timing_ceiling.py PICKLE"""
import os
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R

if __name__ == "__main__":
    rows = pickle.load(open(sys.argv[1], "rb"))
    secs = float(os.environ.get("SECS", 3000))
    rungs = sorted({j[0] for j, _ in rows})
    seeds = sorted({j[3] for j, _ in rows})
    jobs = [(N, s, c) for N in rungs for s in seeds for c in L.COL]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        res = list(ex.map(L.job, [(L.timing(N), "designed", {"lad": "time", "size": N}, s, c, secs) for N, s, c in jobs], chunksize=2))
    I = R.boot(len(seeds))
    print(f"== timing's ceiling: the designed brain told the slot length, not the phase; {len(seeds)} pairs, {secs:.0f} s; share of the gap [95%]")
    for N in rungs:
        def get(arm, P=None):
            x = [r for (nn, a, p, s, c), r in rows if nn == N and a == arm and (P is None or p == P)]
            return L.scored(x, secs, I)
        b, t = get("circuit"), get("vtold")
        d = L.scored([r for (nn, s, c), r in zip(jobs, res) if nn == N], secs, I)
        net = get("net10kc60", 2240)
        g = t[1] - b[1]
        line = f"  rung {N}: designed {np.median((d[1] - b[1]) / g):+.2f} [{np.percentile((d[1] - b[1]) / g, 2.5):+.2f},{np.percentile((d[1] - b[1]) / g, 97.5):+.2f}]"
        line += f" | growing brain {np.median((net[1] - b[1]) / g):+.2f}"
        print(line, flush=True)
