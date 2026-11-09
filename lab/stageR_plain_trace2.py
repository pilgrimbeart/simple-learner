"""stageR_plain_trace2.py: what drifts in the bank over a 10,000 s plain life (lab/v/stageR_plain_trace.log: base steady near 2.45, the bank
2.35 at 1000 s, 2.06 in the last third at 10,000 s). Main session, 2026-11-08.

The written bank rebuilt from parts (lab/rivals.py RV, identical lives to the bank's, R1), with every taste logged: its sign, the pause's
estimate and count, whether pausing, the rival followed, the colour believed food, the eye-rate estimate. Per 1000 s window: goods, bads,
the share of tastes taken while pausing, the pause estimate, flips of the believed colour. Seeds 81400-81403 x red/blue, 1.25 ms.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stageR_plain_trace2.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import rivals as RV


class Logged(RV.RV):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.log = []

    def taste(self, value, at):
        super().taste(value, at)
        if value:
            self.log.append((self.t, value, self.est, self.P, self.pausing, self.act, self.food, self.rate, self.p.get("sd", 0.0)))


def one(job):
    seed, first = job
    from stage2_lang import arms as S
    lf = RV.make(S.world_of(R.PLAIN), seed, first, cls=Logged)
    S.live(lf, 10000.0)
    return lf.brain.log


if __name__ == "__main__":
    jobs = [(s, c) for s in range(81400, 81404) for c in R.COL]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        logs = list(ex.map(one, jobs))
    print("window (s)   goods  bads  pausing  est (s)  P     colour flips  eye rate  jitter sd   (sums or means over 8 lives)")
    for w0 in range(0, 10000, 1000):
        rows = [[x for x in L if w0 <= x[0] < w0 + 1000] for L in logs]
        a = np.array([x for r in rows for x in r], float)
        flips = sum(sum(1 for i in range(1, len(r)) if r[i][6] != r[i - 1][6]) for r in rows)
        print(f"{w0:5d}-{w0 + 1000:5d}  {int((a[:, 1] > 0).sum()):5d} {int((a[:, 1] < 0).sum()):5d}  {a[:, 4].mean():.3f}  "
              f"{a[:, 2].mean():6.2f}  {a[:, 3].mean():.2f}  {flips:5d}  {a[:, 7].mean():8.2f}  {a[:, 8].mean():.4f}", flush=True)
    for L in logs:
        print("  life: est at end %.2f, max est %.2f, max P %.2f" % (L[-1][2], max(x[2] for x in L), max(x[3] for x in L)))
