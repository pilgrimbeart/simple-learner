"""stage3_sense.py: why the bank does harm where the eyes are more sensitive (discrete/NOTEBOOK.md, D35; main session, 2026-11-07).
In g80 (SENSE x2.824, nothing else) bank - base is -.55 [-.62,-.48] on 200 pairs, and the told arm is below base too, so the loss is
in the parts the bank adds to base (lab/universal.py's U), not in choosing a colour. Each part switched off in turn (universal.py's
switches: eye, trustk, growk, pausek, jit), in g80 and plain, 100 pairs, fresh seeds 81100-81199, 1.25 ms, 100 s, in seconds mode,
on the ordinary (uncompiled) path, since the compiled one isn't proven for the switches.

Prediction, written before any of these lives: the eye filter (eye=0 closes most of the loss). Its threshold is
max(1, margin_e * rate * tau_e) pulses within tau_e: with the eye's background rate raised 2.8 times, a block's flash must be
2.8 times larger to pass, so far blocks are lost.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage3_sense.py > lab/v/stage3_sense.log"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R

SEEDS = range(81100, 81200)
VARIANTS = (("circuit", {}), ("bank", {}), ("vtold", {}), ("bank", {"eye": 0}), ("bank", {"pausek": 0}), ("bank", {"jit": 0}),
            ("bank", {"trustk": 0}), ("bank", {"growk": 0}), ("vtold", {"eye": 0}))


def init(dt):
    R._init(dt, False)
    from stage2_lang import arms as S
    S.FAST = False


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, kw, seed, first = j
    l = S.live(S.make(S.world_of(text), arm, seed, first, kw=dict(kw)), 100.0)
    return sum(a - COST * b for a, b, _ in l), spent(l)


if __name__ == "__main__":
    W, _, _ = R.worlds()
    texts = {"plain": R.PLAIN, "g80": W["g80"][0]}
    I = R.boot(len(SEEDS))
    res = {}
    t0 = time.time()
    with ProcessPoolExecutor(5, initializer=init, initargs=(0.00125,)) as ex:
        for wn, text in texts.items():
            for i, (arm, kw) in enumerate(VARIANTS):
                res[wn, i] = list(ex.map(job, [(text, arm, tuple(kw.items()), s, c) for s in SEEDS for c in R.COL], chunksize=2))
                print(f"# {wn} {arm} {kw} ({time.time() - t0:.0f} s)", flush=True)
    for wn in texts:
        b = R.eff(res[wn, 0], I)
        for i, (arm, kw) in enumerate(VARIANTS):
            e = R.eff(res[wn, i], I)
            lo, hi = np.percentile(e[1] - b[1], [2.5, 97.5])
            name = arm + (" " + " ".join(f"{k}={v}" for k, v in kw.items()) if kw else "")
            print(f"{wn:5s} {name:16s} {e[0]:+.3f}  minus base {e[0] - b[0]:+.3f} [{lo:+.3f},{hi:+.3f}]", flush=True)
