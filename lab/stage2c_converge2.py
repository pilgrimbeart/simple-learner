"""stage2c_converge2.py: does the bank settle in alternate? lab/v/stage2c_halve.log (seconds mode, 100 pairs a step): the bank in
alternate went 1.28, 1.43, 1.37, 1.46, 1.66 from 10 ms to 0.625 ms, the last halving +.21 [+.06,+.36], while base and the other worlds
held within noise. Here alternate and plain, base and bank, seconds mode, at 2.5, 1.25, 0.625 and 0.3125 ms, 400 pairs a step (half-width
about .05), fresh seeds each step: 68000-68399, 68400-68799, 68800-69199, 69200-69599. Prediction (mine, written first): the bank in
alternate rises a further .1 to 0.3125 ms, so it is still moving, and plain holds within .05.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2c_converge2.py > lab/v/stage2c_converge2.log"""
import sys, time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import stage2c_steps as P

STEPS = (0.0025, 0.00125, 0.000625, 0.0003125)
SEEDS = [range(68000 + 400 * i, 68400 + 400 * i) for i in range(4)]
W = ("alternate", "plain")

if __name__ == "__main__":
    res = {}
    t0 = time.time()
    for dt, seeds in zip(STEPS, SEEDS):
        res[dt] = P.run(W, seeds, dt, True)
        print(f"done {dt * 1000:g} ms ({time.time() - t0:.0f} s)", flush=True)
    I, J = P.boot(400), P.boot(400, seed=1)
    for w in W:
        for q in ("base", "bank", "bank-base"):
            vals, ds, prev = [], [], None
            for i, dt in enumerate(STEPS):
                B = I if i % 2 == 0 else J
                if q == "bank-base":
                    a, va = P.eff(res[dt][w, "bank"], B)
                    b, vb = P.eff(res[dt][w, "base"], B)
                    x, vx = a - b, va - vb
                else:
                    x, vx = P.eff(res[dt][w, q], B)
                lo, hi = np.percentile(vx, [2.5, 97.5])
                vals.append(f"{dt * 1000:g}ms {x:+.3f}[{lo:+.2f},{hi:+.2f}]")
                if prev is not None:
                    d, vd = x - prev[0], vx - prev[1]
                    dl, dh = np.percentile(vd, [2.5, 97.5])
                    ds.append(f"{d:+.3f}[{dl:+.2f},{dh:+.2f}]")
                prev = (x, vx)
            print(f"{w:10s} {q:9s} " + "  ".join(vals) + " | d: " + " ".join(ds), flush=True)
