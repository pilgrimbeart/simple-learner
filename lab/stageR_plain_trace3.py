"""stageR_plain_trace3.py: does the balance learner (lab/drivebal.py, inherited by the bank) drift over a 10,000 s plain life? Its setting x
(the log ratio of the two thrusters' gains, ideal 0 in plain's symmetric body) each 1000 s, over 8 lives (seeds 81400-81403 x red/blue,
1.25 ms), and how often its jitter is on. Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stageR_plain_trace3.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import rivals as RV


def one(job):
    seed, first = job
    from stage2_lang import arms as S
    lf = RV.make(S.world_of(R.PLAIN), seed, first)
    S.live(lf, 10000.0)
    return lf.brain.trace, lf.brain.drives


if __name__ == "__main__":
    jobs = [(s, c) for s in range(81400, 81404) for c in R.COL]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        out = list(ex.map(one, jobs))
    print("t (s)   x in each of 8 lives (0 is balanced)          mean |x|")
    for t0 in range(0, 10001, 1000):
        xs = [min(tr, key=lambda e: abs(e[0] - t0))[1] for tr, _ in out]
        print(f"{t0:6d}  " + " ".join(f"{x:+.2f}" for x in xs) + f"   {np.mean(np.abs(xs)):.2f}")
    print("drives per life:", [d for _, d in out])
