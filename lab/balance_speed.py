"""balance_speed.py: how fast could the balance learner be? Against an ideal learner with the same evidence (AGENTS.md, measure in bits).
Main session, 2026-11-08.

  curve   plain, the balance x held fixed at an offset d (no wobble, no learning), 300 s lives: each drive's outcome (the food pulses seen
          during it, the learner's own measure), its mean f(d) and spread s(d), and the life's gain a second. Since f(d) ~ f0 - c d^2, a
          drive at offset d tells about the balance through f'(d) = -2 c d against s: the Fisher information a drive carries.
  track   a world with one thruster fixed at twice the other's strength (so the right |x| is ln 2 = .69), 2000 s lives: the old learner's
          and the adaptive one's |x| over time.
Seeds 81800-81819 x red/blue (fresh), 1.25 ms.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/balance_speed.py curve|track"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import adaptive as A

OFFSETS = (-0.6, -0.3, -0.15, 0.0, 0.15, 0.3, 0.6)
SEEDS = range(81800, 81820)
DOUBLE = "(world (meta (link L1) (group body)) (on fire (set gain (if (= thruster 0) 2 1))))"


class Held(A.AV):
    """The bank with its balance held at p['xheld'] and each drive's outcome logged."""
    def __init__(self, seed, p):
        super().__init__(seed, {**p, "a0": 0.0, "rearm": 0, "avg": 0})
        self.x = float(self.p["xheld"])
        self.ys = []
        self._set(self.x)

    def step(self):
        n0 = self.drives
        out = super().step()
        if self.drives > n0:
            self.ys.append(self.pulses)
        return out


def job_curve(j):
    from minimal.spec import COST
    from stage2_lang import arms as S
    d, seed, first = j
    lf = A.make(S.world_of(R.PLAIN), seed, first, {"xheld": d}, cls=Held)
    l = S.live(lf, 300.0)
    return lf.brain.ys, sum(a - COST * b for a, b, _ in l) / 300.0


def job_track(j):
    from stage2_lang import arms as S
    arm, seed, first = j
    w = S.world_of(DOUBLE)
    if arm == "old":
        lf = A.make(w, seed, first, None, cls=A.RV.RV)          # the old bank (R1: identical lives), uncompiled, its trace kept
    else:
        lf = A.make(w, seed, first, {"avg": 2})
    S.live(lf, 2000.0)
    return lf.brain.trace


if __name__ == "__main__":
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        if sys.argv[1] == "curve":
            print("offset d   drives  f(d) mean pulses a drive   s(d) spread   gain a second   (40 lives each)")
            rows = []
            for d in OFFSETS:
                out = list(ex.map(job_curve, [(d, s, c) for s in SEEDS for c in R.COL]))
                y = np.concatenate([np.array(o[0], float) for o in out])
                g = np.mean([o[1] for o in out])
                rows.append((d, y.mean(), y.std(), len(y), g))
                print(f"  {d:+.2f}   {len(y):6d}   {y.mean():.3f} +- {y.std() / np.sqrt(len(y)):.3f}   {y.std():.2f}   {g:.3f}", flush=True)
            d = np.array([r[0] for r in rows])
            f = np.array([r[1] for r in rows])
            c2, c1, c0 = np.polyfit(d, f, 2)
            s = np.mean([r[2] for r in rows])
            print(f"fit f(d) = {c0:.3f} {c1:+.3f} d {c2:+.3f} d^2; spread {s:.2f} a drive")
            for h in (0.1, 0.2, 0.3):
                # a pair of drives at +h and -h around an estimate off by u: difference -4 c h u (c = -c2), noise sqrt 2 s;
                # the offset's standard error after N drives (N/2 pairs): s / (2 |c2| h sqrt N)
                for eps in (0.05, 0.1):
                    N = (s / (2 * abs(c2) * h * eps)) ** 2
                    print(f"  ideal two-point design, trials at +-{h}: drives for a standard error of {eps} in x: {N:,.0f}")
        else:
            for arm in ("old", "adaptive"):
                tr = list(ex.map(job_track, [(arm, s, c) for s in SEEDS for c in R.COL]))
                print(f"{arm}: |x| (the right value .69), mean and spread over 40 lives")
                for t0 in (0, 100, 200, 500, 1000, 1500, 2000):
                    v = np.abs([min(t, key=lambda e: abs(e[0] - t0))[1] for t in tr])
                    print(f"  t {t0:5d} s  |x| {v.mean():.2f} (sd {v.std():.2f})", flush=True)
