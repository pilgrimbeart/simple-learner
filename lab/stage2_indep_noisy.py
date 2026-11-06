"""stage2_indep_noisy.py: why noisy's excess on its eye read 10.14 a second, not 10 (lab/v/stage2_indep_worlds.log).
The world's stream replayed by my own code (table.py's NoisyEye: seed + 5_500_011, a coin, then per tick a Poisson of
10 x TICK, each pulse a uniform moment) gives the exact count injected in each life; the rest of the eye's pulses are
the body's, against SENSE x seen x dt from world.py's rays.

    .venv/bin/python lab/stage2_indep_noisy.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage2_indep_worlds as IW


def replay(seed):
    r = np.random.default_rng(seed + 5_500_011)
    e = int(r.integers(2))
    n = 0
    for _ in range(10000):
        k = int(r.poisson(10 * 0.01))
        n += k
        for _ in range(k):
            r.random()
    return e, n


def one(job):
    L = IW.one(job)
    e, n = replay(L["seed"])
    rec = L["pulses"].sum(0)
    exp = np.zeros(2)
    for c in (0, 1):
        exp[L["wire_s"][c]] = 50.0 * 0.01 * L["seen"][:, c].sum()
    return n, rec[e] - n, exp[e], rec[1 - e], exp[1 - e]


if __name__ == "__main__":
    jobs = [("noisy", k, s, c) for k in ("circuit", "bank") for s in range(64100, 64150) for c in IW.COL]
    with ProcessPoolExecutor(7) as ex:
        R = np.array(list(ex.map(one, jobs, chunksize=2)), dtype=float)
    n, real_e, exp_e, rec_o, exp_o = R.sum(0)
    lives = len(R)
    print(f"{lives} lives: injected (replayed) {n:.0f} = {n / (100 * lives):.3f}/s against 10/s (Poisson sd {np.sqrt(1000 * lives) / (100 * lives):.3f});"
          f" the noisy eye's own pulses {real_e:.0f} / expected {exp_e:.0f} = {real_e / exp_e:.4f}; other eye {rec_o / exp_o:.4f}")
    print("per life, received minus replayed is never negative:", bool((R[:, 1] >= 0).all()))
    # the same draws, the seeds' own: is 10.14 the luck of these seeds?
    m = [replay(s)[1] for s in range(64100, 64150)]
    print(f"replayed counts on these 50 seeds: mean {np.mean(m):.1f} per life (1000 expected), sd {np.std(m):.1f}")
