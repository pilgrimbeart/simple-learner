"""play1.py: the playing brain's D1, step 1 (PROGRAMME.md, The next phase): does a rhythm unit's own judgement of itself rank units as the
ruler does? No brain plays yet: each unit, drawn at random, drives the body alone, open loop, over many bodies (dance0.py's lives).

A rhythm unit: a square-wave oscillator of period P (s) and duty D, at a rate R (beats a second); in its on part it drives motor m at
R w_m, in its off part at R v_m. Everything drawn at random from wide ranges fixed here before any life: P log-uniform 0.2 to 20 s, D
uniform .1 to .9, R log-uniform 5 to 50 a second, each weight 0 with chance a third, else uniform 0 to 1. Its phase is the life's own.
Spins, sweeps, zigzags, straight runs, bursts and stillness are all among such units; nothing chooses them.

Its self-score: the generic predictor (D38's record, clocked by its own beats of each motor, D43): a cell a beat (did an eye pulse since
that motor's last beat?), and how much the cell k beats back tells about this one (mutual information of the two cells, bits a beat),
for each look-back k up to 64; the best k, times that motor's beats a second; the better motor. Bits a second its own movement makes the
senses predictable. It knows nothing of bodies, balance or stride.

The ruler: dance0.py's observer, bits about the balance and the stride (mutual information, 8 bins: fewer bodies a unit).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/play1.py [UNITS] [BODIES]
    .venv/bin/python lab/play1.py UNITS BODIES report"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import dance0 as D0
import stage3_random as R

SEEDS0 = 88000                                  # development seeds, fresh
ANCHORS = {"spin0": (1e9, 1.0, 12.3, (1, 0), (1, 0)), "sweeps": (16.0, 0.5, 12.3, (1, 0), (0, 1)),
           "straight": (1e9, 1.0, 50.0, (1, 1), (1, 1)), "zig2": (2.0, 0.5, 50.0, (1, .5), (.5, 1))}   # D0's, for reference


def draw_unit(n):
    rng = np.random.default_rng(1_000_003 + n)
    w = lambda: 0.0 if rng.random() < 1 / 3 else float(rng.random())
    return (float(np.exp(rng.uniform(math.log(0.2), math.log(20.0)))), float(rng.uniform(0.1, 0.9)),
            float(np.exp(rng.uniform(math.log(5.0), math.log(50.0)))), (w(), w()), (w(), w()))


def unit_fn(u):
    P, Dt, Rt, w, v = u

    def f(t, ph):
        on = ((t / P + ph) % 1.0) < Dt
        a = w if on else v
        return (Rt * a[0], Rt * a[1])
    return f


class Unit(D0.Cycle):
    def __init__(self, seed, p):
        D0.CYCLES["_unit"] = unit_fn(p["unit"])
        super().__init__(seed, {"cycle": "_unit", "dt": p["dt"]})


def job(j):
    from minimal.spec import COST
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    name, u, seed, first = j
    lf = WLife(seed, first, (lambda s: Unit(s, {"unit": u, "dt": WLife.dt})), S.world_of(D0.WORLD), seconds=True)
    l = S.live(lf, D0.SECS)
    b = lf.brain
    k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
    truth = (math.log(k[0] / k[1]), 0.5 * math.log(k[0] * k[1]) - math.log(lf.v_d), math.log(lf.v_d))
    return dict(cycle=name, seed=seed, truth=truth, pulses=np.array(b.pulses, float).reshape(-1, 2),
                beats=np.array(b.beat_log, float).reshape(-1, 2), gain=sum(a - COST * c for a, c, _ in l))


def _mi(*cols):
    """I(a; b | c) in bits from 0/1 columns a, b and optional c (a stratum per value of c), bias-corrected per stratum."""
    a, b = cols[0], cols[1]
    c = cols[2] if len(cols) > 2 else np.zeros(len(a), int)
    tot = 0.0
    for z in np.unique(c):
        s = c == z
        n = s.sum()
        J = np.array([[np.sum(s & (a == i) & (b == j)) for j in (0, 1)] for i in (0, 1)], float) / n
        pa, pb = J.sum(1), J.sum(0)
        nz = J > 0
        tot += n / len(a) * (float((J[nz] * np.log2(J[nz] / np.outer(pa, pb)[nz])).sum()) - 1 / (2 * n * math.log(2)))
    return tot


def self_score(r, T=D0.SECS, K=64, beyond=False):
    """Bits a second the unit's own beats make the eyes predictable (see the docstring). beyond: only what the cell k beats back tells
    beyond the last beat's, I(c_t; c_t-k | c_t-1), k >= 2: what its movement makes recur, not the eyes' own persistence."""
    P = np.sort(r["pulses"][r["pulses"][:, 0] < T, 0])
    best = 0.0
    for m in (0, 1):
        bm = np.sort(r["beats"][(r["beats"][:, 1] == m) & (r["beats"][:, 0] < T), 0])
        if len(bm) < K + 10:
            continue
        c = (np.diff(np.searchsorted(P, bm)) > 0).astype(int)
        top = 0.0
        for k in range(2 if beyond else 1, K + 1):
            top = max(top, _mi(c[k:], c[:-k], c[k - 1:-1]) if beyond else _mi(c[k:], c[:-k]))
        best = max(best, top * len(bm) / T)
    return best


def recurrence(r, T=D0.SECS):
    """Generic: for each motor, the period (log beats) at which its beat-clocked register recurs, and how strongly; no physics."""
    P = np.sort(r["pulses"][r["pulses"][:, 0] < T, 0])
    out = []
    for m in (0, 1):
        bm = np.sort(r["beats"][(r["beats"][:, 1] == m) & (r["beats"][:, 0] < T), 0])
        v = D0._register(bm, P)
        out += [D0._zcomb(v, np.arange(1.0, D0.KB + 1), 2.0, 127.0), float(v.max())] if len(bm) > D0.KB + 4 else [0.0, 0.0]
    return out


def ruler(rs, T=D0.SECS):
    """Bits about the balance, its size and the stride: the best of a ridge decoder on generic features (D0's, with each motor's
    recurrence period and strength) and each recurrence feature alone, by mutual information in 8 bins. Knows no physics."""
    y = np.array([r["truth"] for r in rs])
    y = np.column_stack([y[:, 0], np.abs(y[:, 0]), y[:, 1]])
    rec = np.array([recurrence(r, T) for r in rs])
    X = np.column_stack([np.array([D0.features(r, T) for r in rs]), rec])
    out = []
    for i in range(3):
        cands = [D0.decode(X, y[:, i])] + [rec[:, j] for j in range(rec.shape[1])]
        out.append(max(D0.mi(y[:, i], c, k=8) for c in cands))
    return out


def report(rows, units):
    by = {}
    for r in rows:
        by.setdefault(r["cycle"], []).append(r)
    res = []
    for name, rs in by.items():
        s = float(np.mean([self_score(r) for r in rs]))
        s2 = float(np.mean([self_score(r, beyond=True) for r in rs]))
        b = ruler(rs)
        g = float(np.mean([r["gain"] for r in rs])) / D0.SECS * 10
        res.append((name, s, b[0], b[2], g, s2, b[1]))
    res.sort(key=lambda x: -x[5])
    print("unit (P s, duty, rate, on weights, off weights) | self-score, plain and beyond the last beat, bits/s | ruler bits: balance, its size, stride | gain/10 s")
    for name, s, b0, b1, g, s2, bs in res:
        u = units[name]
        d = f"P {u[0]:6.2f} d {u[1]:.2f} R {u[2]:4.1f} on ({u[3][0]:.2f},{u[3][1]:.2f}) off ({u[4][0]:.2f},{u[4][1]:.2f})" if u[0] < 1e8 \
            else f"steady R {u[2]:4.1f} ({u[3][0]:.2f},{u[3][1]:.2f})"
        print(f"{name:9s} {d:58s} | {s:5.2f} {s2:5.2f} | {b0:.2f}, {bs:.2f}, {b1:.2f} | {g:+.2f}")
    b = np.array([max(x[2], x[6]) + x[3] for x in res])
    rk = lambda v: np.argsort(np.argsort(v))
    for lab, i in (("plain", 1), ("beyond the last beat", 5)):
        s = np.array([x[i] for x in res])
        rho = float(np.corrcoef(rk(s), rk(b))[0, 1])
        print(f"self-score {lab}: rank correlation with the ruler (balance or its size, + stride, bits) {rho:+.2f}; "
              f"the ruler's top 5 among its top 5: {len(set(np.argsort(-s)[:5]) & set(np.argsort(-b)[:5]))}")


if __name__ == "__main__":
    a = sys.argv[1:]
    n, bodies = (int(a[0]) if a else 40), (int(a[1]) if len(a) > 1 else 300)
    units = {f"u{i}": draw_unit(i) for i in range(n)} | ANCHORS
    out = f"/home/pilgrim/git/simple-learner/lab/v/play1_{n}_{bodies}.pkl"
    if len(a) > 2 and a[2] == "report":
        report(pickle.load(open(out, "rb")), units)
        sys.exit()
    import ledger
    ledger.start()
    jobs = [(name, u, s, ("red", "blue")[s % 2]) for name, u in units.items() for s in range(SEEDS0, SEEDS0 + bodies)]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=8))
    pickle.dump(rows, open(out, "wb"))
    report(rows, units)
