"""rprop_trace.py: why the self-sizing learner (lab/rprop.py) failed predictions 8 and 11 (lab/v/rprop_fresh.log). Each life's moves and
give-ups (t, x, D) and its drives. Double thruster 2000 s on seeds 81900-81904 (of test 8), plain 10,000 s on 81960-81962 (of test 11).
Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_trace.py [2]   (2: v2's stuck lives)"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import stage3_random as R
import adaptive as A
import rprop as RP
import rprop_fresh as F

JOBS = [("double", F.DOUBLE, 2000.0, s, c) for s in range(81900, 81905) for c in R.COL] + \
       [("plain", R.PLAIN, 10000.0, s, c) for s in range(81960, 81963) for c in R.COL]


JOBS2 = [("double", F.DOUBLE, 2000.0, s, c) for s, c in ((82006, "red"), (82013, "red"), (82002, "red"), (82004, "blue"),
                                                        (82000, "red"), (82005, "red"))]   # v2's stuck lives (rprop_trace.py 2)


def job(j):
    from stage2_lang import arms as S
    name, text, secs, seed, first = j
    lf = A.make(S.world_of(text), seed, first, {"n_max": 10 ** 9} if V2 else None, cls=RP.SZ)
    S.live(lf, secs)
    b = lf.brain
    return j[0], seed, first, b.drives, b.x, b.moves


V2 = sys.argv[1:] == ["2"]

if __name__ == "__main__":
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for name, seed, first, drives, x, moves in ex.map(job, JOBS2 if V2 else JOBS):
            mv = [m for i, m in enumerate(moves) if i == 0 or m[1] != moves[i - 1][1]]
            print(f"{name} {seed} {first}: drives {drives}, final x {x:+.2f}, events {len(moves)} ({len(mv)} moves); "
                  f"first 12: " + " ".join(f"{t:.0f}:{xx:+.2f}/{D:.3f}" for t, xx, D in moves[:12]), flush=True)
            print("    moves: " + " ".join(f"{t:.0f}:{xx:+.2f}" for t, xx, D in mv[:30]), flush=True)
