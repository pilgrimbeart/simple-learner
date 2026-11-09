"""rprop_wobble_signal.py: does a drive's own outcome see what its wobble costs? lab/v/rprop_short.log: in plain at 100 s v7's wobble
(.3 at birth, .15 by 100 s) costs 1.3 of base's 2.47, yet its peak test (the sum of d (e^2 - sd^2), two standard errors) fired about
once. Fixed wobbles (no moves, no peak test) in plain, 100 s, fresh seeds 82930-82959; each drive's wobble e, pulses and length recorded.
Per arm: the life's score, drives per life, pulses per drive; within the sd .3 arm, the regression of pulses on |e| and the peak test's
signal to noise per drive. Main session, night of 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_wobble_signal.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import adaptive as A
import rprop9 as R9


class Rec(R9.SZ9):
    def step(self):
        n0 = self.drives
        e, t0 = self.e, self.start
        out = super().step()
        if self.drives > n0:
            self.rec.append((e, self.pulses, self.t - t0, self.t))
        return out


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    sd, seed, first = j
    kw = {"n_max": 10 ** 9, "Dmax": 0.3, "D0": max(sd, 1e-6), "sd_min": sd, "sd_max": sd, "Dmin": 1e-6}
    lf = A.make(S.world_of(R.PLAIN), seed, first, kw, cls=Rec)
    lf.brain.rec = []
    lf.brain.S1 = 0.0
    lf.brain.p["nomove"] = 1
    b = lf.brain
    orig = b.step

    def step():
        b.S1 = 0.0                                      # never moves: the wobble alone
        return orig()
    b.step = step
    l = S.live(lf, 100.0)
    g = [x - COST * y for x, y, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l)), b.rec


if __name__ == "__main__":
    SDS = (0.0, 0.05, 0.1, 0.2, 0.3)
    seeds = range(82930, 82960)
    I = R.boot(len(seeds), 20000)
    out = {}
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for sd in SDS:
            out[sd] = list(ex.map(job, [(sd, s, c) for s in seeds for c in R.COL], chunksize=2))
    R._save("rprop_wobble_signal", out)
    e0 = M.boot_eff([x[0] for x in out[0.0]], I)
    print("== plain, 100 s, 30 pairs, a fixed wobble, never moving", flush=True)
    for sd in SDS:
        e = M.boot_eff([x[0] for x in out[sd]], I)
        lo, hi = np.percentile(e[1] - e0[1], [2.5, 97.5])
        rec = np.array([r for x in out[sd] for r in x[1]])
        print(f"  sd {sd:.2f}: score {e[0]:.3f}, minus sd 0 {e[0] - e0[0]:+.3f} [{lo:+.3f},{hi:+.3f}]; drives a life "
              f"{len(rec) / len(out[sd]):.1f}, pulses a drive {rec[:, 1].mean():.2f} (sd {rec[:, 1].std():.2f}), length a drive "
              f"{rec[:, 2].mean():.2f} s", flush=True)
        if sd > 0:
            ae = np.abs(rec[:, 0])
            k = np.polyfit(ae / sd, rec[:, 1], 1)[0]
            dc = (rec[:, 1] - rec[:, 1].mean()) * (rec[:, 0] ** 2 - sd ** 2)
            print(f"      within: pulses on |e|/sd slope {k:+.3f}; the peak test's mean/sd per drive {dc.mean() / dc.std():+.3f}, so "
                  f"drives to two standard errors about {4 / (dc.mean() / dc.std()) ** 2:.0f}", flush=True)
