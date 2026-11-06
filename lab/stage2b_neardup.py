"""stage2b_neardup.py: stage 2b, part 4. Planted near-duplicates: how well do the lives tell them apart?

Pairs (A, B): rewritten (the same meaning), a constant nudged, a difference in a few ticks, and two distinct pairs as controls. Each pair
lived on the same seeds 65400-65599 x 2 (200 pairs), under base, bank and unwired (a policy that ignores taste: a signature of the world
alone). For each pair and policy:
  same      lives identical (every scored meal and firing)
  d eff     efficiency B - A, paired over seeds, 95% bootstrap
  bits      evidence a life gives for B against A in its outcomes: food and poison in each third and the firing rate (7 numbers),
            Gaussian with a pooled covariance, 1/2 dmu' S^-1 dmu / ln 2, less its median under the null (A and B relabelled at random within
            each seed, 400 times); p = the share of the null at or above it. An estimate, from means only: a lower bound on what outcomes carry.
  lives     lives of each world to tell them apart at 5% each way (Wald, 3.82 bits) at that rate
  first     on 65400-65419 x 2, the first tick the wires differ (pulses and tastes the brain receives) on the same seed: median s, share none

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_neardup.py > lab/v/stage2b_neardup.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from minimal.spec import COST, spent
from stage2_lang import arms as S, worlds as WW

SEEDS = range(65400, 65600)
FD = range(65400, 65420)
WALD = 3.82
X = WW.W
PAIRS = [
    ("rewritten", "halfthrust: a constant / at the firing (identical lives)", X["halfthrust_const"]["text"], X["halfthrust_gain"]["text"]),
    ("rewritten", "unreliable / the same with uniform for chance and no stream named (equal in distribution)",
     "(world (told P) (on tick (set poison (if (chance 0.2) F P))))", "(world (let q 0.2) (told P) (on tick (set poison (if (> q (uniform 0 1)) F P))))"),
    ("rewritten", "weak / dim25 (equal in distribution, L5 against L4)", X["weak"]["text"], X["dim25"]["text"]),
    ("nudged", "swap10 / swap11 (10%)", X["swap10"]["text"], X["swap11"]["text"]),
    ("nudged", "unreliable .2 / .22", X["unreliable"]["text"], X["unreliable22"]["text"]),
    ("nudged", "DRAG x2 / x2.1 (5%)", X["drag2"]["text"], "(world (const DRAG (* 2.1 DRAG)))"),
    ("nudged", "one colour .25 / .30 as bright", X["dim25"]["text"], X["dim25"]["text"].replace("0.25", "0.3")),
    ("few ticks", "plain / poison swapped for 0.1 s at 50 s (10 ticks)", "(world)", "(world (on tick (if (and (>= t 50) (< t 50.1)) (set poison F))))"),
    ("few ticks", "the colours swap for good at 50 s / at 50.05 s (5 ticks)", X["late_swap_50"]["text"], "(world (on tick (set poison (if (< t 50.05) P F))))"),
    ("distinct", "plain / swap10", "(world)", X["swap10"]["text"]),
    ("distinct", "plain / DRAG x2", "(world)", X["drag2"]["text"]),
]
ARMS = ("circuit", "bank", "unwired")


def life(job):
    text, arm, seed, first = job
    lf = S.make(S.world_of(text), arm, seed, first)
    l = S.live(lf)
    gain = sum(a - COST * b for a, b, _ in l)
    feats = [l[i][0] for i in range(3)] + [l[i][1] for i in range(3)] + [l.firings]
    return dict(key=(tuple(lf.scored), len(lf.firings), lf.firings[-1] if lf.firings else None), gain=gain, spent=spent(l), f=np.array(feats, float))


def wires(job):
    import stage2_label as L
    return L.wire(job)


def bits_of(FA, FB, rng, nnull=400):
    """Gaussian outcome evidence a life, bits, bias-corrected by a within-seed relabelling null."""
    def stat(A, B):
        d = A.mean(0) - B.mean(0)
        C = np.cov(np.vstack((A - A.mean(0), B - B.mean(0))).T) + 1e-9 * np.eye(A.shape[1])
        return 0.5 * float(d @ np.linalg.solve(C, d)) / np.log(2)
    obs = stat(FA, FB)
    null = []
    for _ in range(nnull):
        sw = rng.random(len(FA) // 2) < 0.5
        sw = np.repeat(sw, 2)                           # a seed's two lives together
        A = np.where(sw[:, None], FB, FA)
        B = np.where(sw[:, None], FA, FB)
        null.append(stat(A, B))
    null = np.array(null)
    return max(0.0, obs - np.median(null)), float((null >= obs).mean()), obs


def main():
    rng = np.random.default_rng(0)
    print(f"== near-duplicates, seeds {SEEDS.start}-{SEEDS.stop - 1} x 2 ({len(SEEDS)} pairs); first differences on {FD.start}-{FD.stop - 1} x 2", flush=True)
    with ProcessPoolExecutor(7) as ex:
        for kind, label, ta, tb in PAIRS:
            print(f"-- {kind}: {label}", flush=True)
            for arm in ARMS:
                A = list(ex.map(life, [(ta, arm, s, c) for s in SEEDS for c in S.COL], chunksize=4))
                B = list(ex.map(life, [(tb, arm, s, c) for s in SEEDS for c in S.COL], chunksize=4))
                same = sum(a["key"] == b["key"] for a, b in zip(A, B))
                ga, sa = np.array([a["gain"] for a in A]), np.array([a["spent"] for a in A])
                gb, sb = np.array([b["gain"] for b in B]), np.array([b["spent"] for b in B])
                n = len(SEEDS)
                k = rng.integers(0, n, (2000, n))
                I = np.concatenate((2 * k, 2 * k + 1), axis=1)
                d = gb[I].sum(1) / sb[I].sum(1) - ga[I].sum(1) / sa[I].sum(1)
                d0 = gb.sum() / sb.sum() - ga.sum() / sa.sum()
                lo, hi = np.percentile(d, [2.5, 97.5])
                FA, FB = np.array([a["f"] for a in A]), np.array([b["f"] for b in B])
                if same == len(A):
                    b_, p, obs = 0.0, 1.0, 0.0
                else:
                    b_, p, obs = bits_of(FA, FB, rng)
                import stage2_label as L
                wa = list(ex.map(wires, [(ta, arm, s, c) for s in FD for c in S.COL]))
                wb = list(ex.map(wires, [(tb, arm, s, c) for s in FD for c in S.COL]))
                fd = [L.first_diff(x, y) for x, y in zip(wa, wb)]
                fds = [x * 0.01 for x in fd if x is not None]
                print(f"   {arm:8s} same {same}/{len(A)}; d eff {d0:+.3f} [{lo:+.3f},{hi:+.3f}]{' SURE' if lo > 0 or hi < 0 else ''};"
                      f" bits a life {b_:.4f} (raw {obs:.4f}, p {p:.3f}); lives to tell apart {WALD / b_ if b_ > 0 else float('inf'):.0f};"
                      f" first wire difference median {np.median(fds) if fds else float('nan'):.2f} s, none in {sum(x is None for x in fd)}/{len(fd)}", flush=True)


if __name__ == "__main__":
    main()
