"""stage2_converge_bank.py: which of the bank's parts falls at 1 ms? lab/v/stage2_converge.log: base settles (10 ms 2.70, 2.5 ms 2.43,
1 ms 2.45) but the bank keeps falling (2.75, 2.43, 2.25), so at 1 ms bank - base is -.20 [-.29,-.11] in plain. Each part switched
off in turn (universal.py's switches), and the bank told the colour (vtold), at 10 ms and 1 ms, plain, 100 pairs, seeds 66500-66599 x 2.
The part whose removal closes the 1 ms drop holds something counted in ticks. Prediction (written first): the pause (pausek), whose
evidence counts tastes within 1.2 s and whose est shrinks per taste, and so depends on how meals split across ticks.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_converge_bank.py > lab/v/stage2_converge_bank.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import time
from concurrent.futures import ProcessPoolExecutor
from stage2_checks import set_tick, efficiency, sim
from stage2_run import pdiff
from stage2_lang import arms as S, worlds as WW

SEEDS = range(66500, 66600)
DTS = (0.01, 0.001)
VARIANTS = (("bank", {}), ("bank", {"pausek": 0}), ("bank", {"jit": 0}), ("bank", {"eye": 0}), ("bank", {"bankk": 0}),
            ("bank", {"trustk": 0}), ("vtold", {}), ("circuit", {}))


def job(j):
    text, arm, kw, seed, first, dt = j
    if sim.WLife.dt != dt:
        set_tick(dt)
    return S.live(S.make(S.world_of(text), arm, seed, first, kw=dict(kw)))


if __name__ == "__main__":
    text = WW.W["plain"]["text"]
    res = {}
    for dt in DTS:
        t0 = time.time()
        with ProcessPoolExecutor(7) as ex:
            for i, (arm, kw) in enumerate(VARIANTS):
                res[i, dt] = list(ex.map(job, [(text, arm, tuple(kw.items()), s, c, dt) for s in SEEDS for c in S.COL], chunksize=4))
        print(f"done {dt * 1000:g} ms in {time.time() - t0:.0f} s", flush=True)
    for i, (arm, kw) in enumerate(VARIANTS):
        d, lo, hi = pdiff(res[i, 0.001], res[i, 0.01])
        name = arm + (" " + " ".join(f"{k}={v}" for k, v in kw.items()) if kw else "")
        print(f"plain {name:18s} 10 ms {efficiency(res[i, 0.01]):+.3f}  1 ms {efficiency(res[i, 0.001]):+.3f}  1 ms - 10 ms {d:+.3f} [{lo:+.3f},{hi:+.3f}]", flush=True)
