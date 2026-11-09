"""adaptive_x.py: born wobbling then quiet (lab/adaptive.py, a0 1, re-arming off) costs .43 in plain at 10,000 s, never wobbling nothing
(lab/v/adaptive_plain10k_*.log). Is it the balance setting x, learned while wobbling and then frozen (yes: lab/v/adaptive_x.log), and does the learner's own measure (food
pulses seen a drive) rise as meals fall (lab/v/adaptive_x3.log)? x at the end of 2000 s plain lives,
and the last third's efficiency, for a0 = 1 and a0 = 0; the scaling test's seeds. Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/adaptive_x.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import adaptive as A


def job(j):
    from minimal.spec import COST
    from stage2_lang import arms as S
    a0, avg, seed, first = j
    lf = A.make(S.world_of(R.PLAIN), seed, first, {"a0": a0, "rearm": 0, "avg": avg})
    l = S.live(lf, 2000.0)
    b = lf.brain
    c = b.a * b.x + (1 - b.a) * b.xbar if avg == 1 else (b.x if avg == 0 or abs(b.S1) > 2 * np.sqrt(max(b.S2, 1e-12)) else b.x0)
    return (l[2][0] - COST * l[2][1]) / l[2][2], c, b.b or 0.0


if __name__ == "__main__":
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for a0, avg in ((1.0, 2), (1.0, 0), (0.0, 0)):
            out = list(ex.map(job, [(a0, avg, s, c) for s in range(81400, 81410) for c in R.COL]))
            e, x, pb = (np.array(v) for v in zip(*out))
            print(f"a0 {a0} avg {avg}: last third's gain per second {e.mean():.3f}; |the gains' centre| at the end {np.abs(x).mean():.3f}; "
                  f"the learner's own measure (food pulses a drive, its running mean) {pb.mean():.2f}", flush=True)
            if a0:
                print("   corr(|x|, gain) %+.2f; corr(|x|, pulses a drive) %+.2f; corr(pulses a drive, gain) %+.2f" % (
                    np.corrcoef(np.abs(x), e)[0, 1], np.corrcoef(np.abs(x), pb)[0, 1], np.corrcoef(pb, e)[0, 1]))
