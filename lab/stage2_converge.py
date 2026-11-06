"""stage2_converge.py: does the fast model settle as the tick shrinks? D33 found plain moving by -.17 (base) and -.22 (bank) from
10 ms to 5 ms; the user's rule (2026-11-06) re-validates final results at 1 ms. Plain, base and bank, at 10, 5, 2.5 and 1 ms, the
whole tick halved everywhere as in D33 (stage2_checks.set_tick), 100 pairs, seeds 66400-66499 x 2, each step paired against 10 ms.
If the steps' differences shrink towards a limit, 10 ms is a biased but consistent stand-in; if they keep growing, something in the
model or body is counted in ticks (D34's list) and must be put in seconds first. Prediction (written first): base moves
-.17, -.25, -.30; bank similar.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_converge.py > lab/v/stage2_converge.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import time
from concurrent.futures import ProcessPoolExecutor
from stage2_checks import _fine, efficiency
from stage2_run import pdiff
from stage2_lang import arms as S, worlds as WW

SEEDS = range(66400, 66500)
DTS = (0.01, 0.005, 0.0025, 0.001)

if __name__ == "__main__":
    text = WW.W["plain"]["text"]
    res = {}
    for dt in DTS:
        t0 = time.time()
        with ProcessPoolExecutor(7) as ex:
            for arm in ("circuit", "bank"):
                res[arm, dt] = list(ex.map(_fine, [(text, arm, s, c, dt) for s in SEEDS for c in S.COL], chunksize=4))
        print(f"done {dt * 1000:g} ms in {time.time() - t0:.0f} s", flush=True)
    for arm in ("circuit", "bank"):
        for dt in DTS:
            line = f"plain {arm:8s} {dt * 1000:4g} ms {efficiency(res[arm, dt]):+.3f}"
            if dt != DTS[0]:
                d, lo, hi = pdiff(res[arm, dt], res[arm, DTS[0]])
                line += f"  against 10 ms {d:+.3f} [{lo:+.3f},{hi:+.3f}]"
            print(line, flush=True)
    for dt in DTS:
        d, lo, hi = pdiff(res["bank", dt], res["circuit", dt])
        print(f"plain bank - base at {dt * 1000:4g} ms {d:+.3f} [{lo:+.3f},{hi:+.3f}]", flush=True)
