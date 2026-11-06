"""stage2b_noharm.py: stage 2b, part 5. Doing no harm (PROGRAMME.md): in a world with nothing to learn, the lower 95% bound of
(bank - base) stays above -.1 efficiency. Coin, rarefeast, mirror, allfood, never and costly, at 200 pairs, seeds 65600-65799 x 2, paired
over seeds (a seed's two lives together), 4000 bootstrap draws.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_noharm.py > lab/v/stage2b_noharm.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from minimal.spec import COST, spent
from stage2_lang import arms as S, worlds as WW

SEEDS = range(65600, 65800)
NAMES = ("coin", "rarefeast", "mirror", "allfood", "never", "costly")


def life(job):
    text, arm, seed, first = job
    l = S.live(S.make(S.world_of(text), arm, seed, first))
    return sum(a - COST * b for a, b, _ in l), spent(l)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n = len(SEEDS)
    k = rng.integers(0, n, (4000, n))
    I = np.concatenate((2 * k, 2 * k + 1), axis=1)
    print(f"== doing no harm, {n} pairs, seeds {SEEDS.start}-{SEEDS.stop - 1} x 2: bank - base, efficiency, 95%; passes if the lower bound > -.1", flush=True)
    with ProcessPoolExecutor(7) as ex:
        for name in NAMES:
            t = WW.W[name]["text"]
            R = {arm: np.array(list(ex.map(life, [(t, arm, s, c) for s in SEEDS for c in S.COL], chunksize=4))) for arm in ("circuit", "bank")}
            e = {a: (R[a][:, 0].sum() / R[a][:, 1].sum(), R[a][I, 0].sum(1) / R[a][I, 1].sum(1)) for a in R}
            d = e["bank"][1] - e["circuit"][1]
            d0 = e["bank"][0] - e["circuit"][0]
            lo, hi = np.percentile(d, [2.5, 97.5])
            sig = float(np.std(d) * np.sqrt(n))
            print(f"  {name:10s} base {e['circuit'][0]:+.3f}, bank {e['bank'][0]:+.3f}; bank - base {d0:+.3f} [{lo:+.3f},{hi:+.3f}]"
                  f" {'NO HARM' if lo > -0.1 else 'not shown'}; sigma of the difference {sig:.2f}, pairs for a half-width of .1 {(1.96 * sig / 0.1) ** 2:.0f}", flush=True)
