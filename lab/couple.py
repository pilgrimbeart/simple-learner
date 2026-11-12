"""couple.py: understanding as coupling (PROGRAMME.md, the guiding principle; the user, 2026-11-11). Before any mechanism: does the
coupling between senses and actions at the brain's interface peak at the right balance knob, with no reward at all?

play4's world (meals worth nothing until 400 to 600 s); the starting brain foraging with its balance knob fixed from birth at each of
17 settings (-1.6 to 1.6); measured over 50 to 400 s, all before any taste. At the interface, in bins of BIN s: S, which eyes pulsed
(4 states); A, which motors beat (4 states). Coupling in both directions, one bin apart: I(A_t; S_t+1) (actions to senses: a forward
model) + I(S_t; A_t+1) (senses to actions: a policy), plug-in on 4 x 4 tables less Miller and Madow's bias, in bits a second. Small
tables: coupling as a small local predictor can capture it.
Bodies: lopsided (each thruster a half to twice) and plain (the knob's right value 0).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/couple.py [BODIES]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import bodyladder as BL
import dance0 as D0
import play4  # noqa: F401  (the quiet spell's world text)
import play3 as P3
import stage3_random as R

GRID = np.round(np.arange(-1.6, 1.61, 0.2), 2)
BIN = 0.05
T0, T1 = 50.0, 400.0
SEEDS0 = 97000
PLAIN = f"(world {BL.M} (let q (uniform 400 600)) (on meal (if (< t q) (set worth 0))))"


def _mi(x, y, k=4):
    J = np.zeros((k, k))
    np.add.at(J, (x, y), 1)
    n = J.sum()
    P = J / n
    px, py = P.sum(1), P.sum(0)
    nz = P > 0
    I = float((P[nz] * np.log2(P[nz] / np.outer(px, py)[nz])).sum())
    bias = ((nz.sum() - 1) - (np.count_nonzero(px) - 1) - (np.count_nonzero(py) - 1)) / (2 * n * math.log(2))
    return I - bias


def binned(pulses, beats):
    edges = np.arange(T0, T1 + BIN / 2, BIN)
    S = sum(((np.histogram(pulses[pulses[:, 1] == e, 0], edges)[0] > 0).astype(int) << e) for e in (0, 1))
    A = sum(((np.histogram(beats[beats[:, 1] == m, 0], edges)[0] > 0).astype(int) << m) for m in (0, 1))
    return S, A


def coupling(pulses, beats, S=None, A=None):
    if S is None:
        S, A = binned(pulses, beats)
    fwd, pol = _mi(A[:-1], S[1:]), _mi(S[:-1], A[1:])
    return fwd / BIN, pol / BIN


def job(j):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    body, seed, beta = j
    text = P3.WORLD if body == "lopsided" else PLAIN
    q = T.numbers(seed, {"sync": 1, "g0": math.exp(beta / 2), "g1": math.exp(-beta / 2)})
    cls = D0.recorder(seconds_cls(T.Circuit))
    lf = WLife(seed, "red", (lambda s: cls(s, q)), S.world_of(text), seconds=True)
    S.live(lf, T1)
    right = 0.0
    if body == "lopsided":
        k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
        right = __import__('sigmoid_body').right_knob(k[0], k[1], __import__('table').numbers(seed, {})['drive'])      # (the right knob for whichever body is on)
    b = lf.brain
    P, B = np.array(b.pulses, float).reshape(-1, 2), np.array(b.beat_log, float).reshape(-1, 2)
    S, A = binned(P, B)
    f, p = coupling(None, None, S, A)
    return dict(body=body, seed=seed, beta=beta, right=right, fwd=f, pol=p, S=S.astype(np.int8), A=A.astype(np.int8))


def speed(rows, windows=(10, 30, 60, 100, 350)):
    """How fast coupling tells settings apart: for windows of W s (from the start of the measured span), how often the right knob's
    coupling beats a knob .4 off (each side), and how often the best of the grid is within .2 of right."""
    rs = [r for r in rows if r["body"] == "lopsided"]
    seeds = sorted({r["seed"] for r in rs})
    print("window | right beats .4 off | best of grid within .2")
    for W in windows:
        n = int(W / BIN)
        win, ok = [], []
        for s in seeds:
            c = {}
            for r in rs:
                if r["seed"] == s:
                    S, A = r["S"][:n].astype(int), r["A"][:n].astype(int)
                    c[r["beta"]] = (_mi(A[:-1], S[1:]) + _mi(S[:-1], A[1:])) / BIN
            right = [r["right"] for r in rs if r["seed"] == s][0]
            near = GRID[np.argmin(np.abs(GRID - right))]
            for d in (-0.4, 0.4):
                o = round(near + d, 2)
                if o in c:
                    win.append(c[near] > c[o])
            ok.append(abs(GRID[int(np.argmax([c[b] for b in GRID]))] - right) <= 0.2)
        print(f"{W:5.0f} s | {np.mean(win):.0%} | {np.mean(ok):.0%}", flush=True)


def report(rows):
    for body in ("lopsided", "plain"):
        rs = [r for r in rows if r["body"] == body]
        seeds = sorted({r["seed"] for r in rs})
        print(f"== {body}: {len(seeds)} bodies; coupling in bits a second (forward + policy), knob grid {GRID[0]} to {GRID[-1]}")
        peaks, rights, rel = [], [], {}
        for s in seeds:
            c = {r["beta"]: (r["fwd"] + r["pol"], r["fwd"], r["pol"]) for r in rs if r["seed"] == s}
            right = [r["right"] for r in rs if r["seed"] == s][0]
            tot = np.array([c[b][0] for b in GRID])
            sm = np.convolve(tot, [1 / 3, 1 / 3, 1 / 3], mode="same")       # a little smoothing across neighbouring knobs
            peaks.append(GRID[int(np.argmax(sm[1:-1])) + 1])
            rights.append(right)
            for b in GRID:                                                  # the curve against the knob's distance from right
                d = round(round((b - right) / 0.4) * 0.4, 1)
                rel.setdefault(d, []).append(c[b][0] - tot.mean())
        peaks, rights = np.array(peaks), np.array(rights)
        err = np.abs(peaks - rights)
        print(f"   the knob of most coupling against the right knob: median error {np.median(err):.2f}, within .2 {np.mean(err <= .2):.0%}, "
              f"within .4 {np.mean(err <= .4):.0%}; correlation {np.corrcoef(peaks, rights)[0, 1] if np.std(rights) > 0 else float('nan'):+.2f}")
        print("   coupling (less each body's mean) against knob minus right: " +
              ", ".join(f"{d:+.1f}: {np.mean(v):+.2f}" for d, v in sorted(rel.items()) if abs(d) <= 2.0 and len(v) >= 3))
        f = np.mean([r["fwd"] for r in rs]), np.mean([r["pol"] for r in rs])
        print(f"   mean forward {f[0]:.2f}, policy {f[1]:.2f} bits a second")


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 20
    out = f"/home/pilgrim/git/simple-learner/lab/v/couple_{n}.pkl"
    out = out.replace(".pkl", "_muscle.pkl") if __import__("os").environ.get("MUSCLE") == "1" else out   # (the new body's lives apart)
    if "report" in a:
        report(pickle.load(open(out, "rb")))
        sys.exit()
    if "speed" in a:
        speed(pickle.load(open(out, "rb")))
        sys.exit()
    import ledger
    ledger.start()
    jobs = [("lopsided", s, float(b)) for s in range(SEEDS0, SEEDS0 + n) for b in GRID]
    jobs += [("plain", s, float(b)) for s in range(SEEDS0, SEEDS0 + n // 2) for b in GRID]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=4))
    pickle.dump(rows, open(out, "wb"))
    report(rows)
