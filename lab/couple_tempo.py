"""couple_tempo.py: does coupling point at the right tempo? (D51's question for the second knob; after the half-centre on drag bodies.)
Bodies with thrusters and drag drawn (couple_search.BOTH, the quiet spell: no taste at all); the starting brain told its balance, its
tempo (every rate scaled by e^s) set at a grid of s; coupling at the interface over 50 to 400 s, as couple.py. The right tempo for this
body: log of its drag (the told tempo, bodyladder). Also the food each tempo gets once food begins (play4's windows), to see what the
right tempo is worth.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/couple_tempo.py [BODIES]"""
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import couple as C
import couple_search as CS
import play4 as P4
import stage3_random as R

GRID = np.round(np.arange(-1.0, 1.01, 0.2), 2)
SEEDS0 = 101000


def job(j):
    from stage2_lang import arms as S
    import bodyladder as BL
    seed, s = j
    lf = BL.make(CS.BOTH, "toldbody", seed, "red")
    p = lf.brain.p
    d = lf.v_d
    for r in ("scan", "drive", "run"):                  # toldbody scaled the rates by d: undo, then scale by e^s
        p[r] *= math.exp(s) / d
    rec = []
    inner_s, inner_t = lf.brain.stimulate, lf.brain.step
    pulses, beats = [], []
    clock = [0.0]

    def stim(sensor, at):
        pulses.append((clock[0] + at, sensor))
        inner_s(sensor, at)

    def step():
        out = inner_t()
        for m, at in getattr(lf.brain, "beats", None) or []:
            beats.append((clock[0] + at, m))
        clock[0] += lf.dt
        return out
    lf.brain.stimulate, lf.brain.step = stim, step
    S.live(lf, P4.SECS)
    P_, B_ = np.array(pulses, float).reshape(-1, 2), np.array(beats, float).reshape(-1, 2)
    S_, A_ = C.binned(P_, B_)
    f, pol = C.coupling(None, None, S_, A_)
    edges = np.arange(C.T0, C.T1 + C.BIN / 2, C.BIN)    # counts: each motor's beats in a bin, 0 to 3 or more (no rate rewarded for slowness)
    A4 = sum(np.minimum(np.histogram(B_[B_[:, 1] == m, 0], edges)[0], 3) * (4 ** m) for m in (0, 1)).astype(int)
    def mi(x, y, kx, ky):
        J = np.zeros((kx, ky)); np.add.at(J, (x, y), 1); n = J.sum(); P = J / n; px, py = P.sum(1), P.sum(0); nz = P > 0
        return float((P[nz] * np.log2(P[nz] / np.outer(px, py)[nz])).sum()) - ((nz.sum() - 1) - (np.count_nonzero(px) - 1) - (np.count_nonzero(py) - 1)) / (2 * n * math.log(2))
    coupc = (mi(A4[:-1], S_[1:], 16, 4) + mi(S_[:-1], A4[1:], 4, 16)) / C.BIN
    q = lf.v_q
    lo, hi = q / lf.dt, (q + 300) / lf.dt
    good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
    badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
    return dict(seed=seed, s=s, logd=math.log(d), coup=f + pol, coupc=coupc, gain=(good - 2 * badm) / 30)


if __name__ == "__main__":
    import ledger
    ledger.start()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, [(sd, float(s)) for sd in range(SEEDS0, SEEDS0 + n) for s in GRID]))
    pk_c, pk_g, logd, pk_cc = [], [], [], []
    rel_c, rel_g, rel_cc = {}, {}, {}
    for sd in range(SEEDS0, SEEDS0 + n):
        rs = sorted([r for r in rows if r["seed"] == sd], key=lambda r: r["s"])
        c = np.array([r["coup"] for r in rs])
        g = np.array([r["gain"] for r in rs])
        cc = np.array([r["coupc"] for r in rs])
        pk_cc.append(GRID[int(np.argmax(np.convolve(cc, [1 / 3] * 3, "same")[1:-1])) + 1])
        ld = rs[0]["logd"]
        pk_c.append(GRID[int(np.argmax(np.convolve(c, [1 / 3] * 3, "same")[1:-1])) + 1])
        pk_g.append(GRID[int(np.argmax(np.convolve(g, [1 / 3] * 3, "same")[1:-1])) + 1])
        logd.append(ld)
        for r in rs:
            k = round(round((r["s"] - ld) / 0.4) * 0.4, 1)
            rel_c.setdefault(k, []).append(r["coup"] - c.mean())
            rel_g.setdefault(k, []).append(r["gain"] - g.mean())
            rel_cc.setdefault(k, []).append(r["coupc"] - cc.mean())
    pk_c, pk_g, logd, pk_cc = map(np.array, (pk_c, pk_g, logd, pk_cc))
    print(f"== {n} bodies (thrusters and drag drawn), balance told, tempo e^s over {GRID[0]} to {GRID[-1]}")
    print(f"  tempo of most coupling against log drag: median error {np.median(np.abs(pk_c - logd)):.2f}, correlation {np.corrcoef(pk_c, logd)[0, 1]:+.2f}")
    print(f"  ... coupling from beat counts:            median error {np.median(np.abs(pk_cc - logd)):.2f}, correlation {np.corrcoef(pk_cc, logd)[0, 1]:+.2f}")
    print(f"  tempo of most food against log drag:     median error {np.median(np.abs(pk_g - logd)):.2f}, correlation {np.corrcoef(pk_g, logd)[0, 1]:+.2f}")
    print("  coupling (less body mean) against tempo minus log drag: " + ", ".join(f"{k:+.1f}: {np.mean(v):+.2f}" for k, v in sorted(rel_c.items()) if len(v) >= 3))
    print("  coupling from counts (less body mean) against tempo minus log drag: " + ", ".join(f"{k:+.1f}: {np.mean(v):+.2f}" for k, v in sorted(rel_cc.items()) if len(v) >= 3))
    print("  food a 10 s (less body mean) against tempo minus log drag: " + ", ".join(f"{k:+.1f}: {np.mean(v):+.2f}" for k, v in sorted(rel_g.items()) if len(v) >= 3))
