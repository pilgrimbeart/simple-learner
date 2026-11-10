"""dance0.py: the dancing brain's stage D0 (PROGRAMME.md, The next phase): count the bits. A handful of movement cycles written by hand,
each open loop (it ignores what it sees and tastes), against ordinary foraging (the starting brain). For each: how much an observer that
knows its own beats learns about the body from the eye pulses, in bits, after 10, 30 and 100 s; and the food it costs.

The body: each thruster's strength and the drag drawn afresh each life, each log-uniform between a half and twice (lab/bodyladder.py's
`both`). The things worth knowing:
  balance  log(k0 / k1), motor 0's thruster's strength over motor 1's: the knob D43 sets.
  stride   log(sqrt(k0 k1) / d): how far a beat carries the body (a beat adds k PUSH of speed, which fades at d DRAG, so it moves k PUSH /
           (d DRAG)). Strength and drag are one number to the eyes, except through the coast's time course (1 / (d DRAG), 10 to 40 ms).
  drag     log d on its own: what the eyes could say beyond the stride.

The observer (mended after the first run, lab/v/dance_predictions.md): bits as mutual information between the truth and an estimate,
each cut into 12 equal-count bins and corrected for few lives, from the better of a ridge decoder on generic features of the pulses and
beats and a physical estimator (each motor's beats a revolution from its beat-clocked register, D43). A lower bound only: a better
observer could find more, and neither knows the physics of a zigzag, a straight run or a burst.

`corridor`: where across the corridor the nearest block ahead lies (its side, in the brain's frame), every .25 s, guessed by a linear
decoder from the last .5 s of pulses and beats.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/dance0.py [BODIES] [cycles]
    .venv/bin/python lab/dance0.py 600 x report            # re-score the saved lives (lab/v/dance0_600.pkl, not in git)
    .venv/bin/python lab/dance0.py 200 CYCLES corridor"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import bodyladder as BL
import stage3_random as R

SEEDS0 = 87000                                  # development seeds, fresh
SECS = 100.0
WINDOWS = (10.0, 30.0, 100.0)
D = "(pow 2 (uniform -1 1))"
WORLD = BL.WORLDS["both"][0]                    # a, b: each thruster's strength; d: the drag factor
SCAN, DRIVE = 12.3, 50.0                        # the starting brain's scan and drive rates (discrete/results/cmos_b_bench.json), per s


def _sq(t, period, phase):
    """+1 for the first half of each period, -1 for the second (the cycle's own phase, random each life)."""
    return 1 if ((t / period + phase) % 1.0) < 0.5 else -1


# Each cycle: (rate of motor 0, rate of motor 1), per s, at moment t, given the life's phase u (0..1).
CYCLES = {
    "still": lambda t, u: (0.0, 0.0),
    "spin0": lambda t, u: (SCAN, 0.0),                                  # one motor alone at the scan's rate
    "spin1": lambda t, u: (0.0, SCAN),
    "sweeps": lambda t, u: (SCAN, 0.0) if _sq(t, 16.0, u) > 0 else (0.0, SCAN),   # 8 s on each, alternately (D20's sweeps)
    "straight": lambda t, u: (DRIVE, DRIVE),                            # both at the drive's rate: a lopsided body curves
    "burst": lambda t, u: (DRIVE, DRIVE) if ((t + u) % 1.0) < 0.1 else (0.0, 0.0),  # 0.1 s of drive, 0.9 s coasting and looking
    "zig0.5": lambda t, u: (DRIVE, DRIVE / 2) if _sq(t, 0.5, u) > 0 else (DRIVE / 2, DRIVE),
    "zig2": lambda t, u: (DRIVE, DRIVE / 2) if _sq(t, 2.0, u) > 0 else (DRIVE / 2, DRIVE),
    "zig8": lambda t, u: (DRIVE, DRIVE / 2) if _sq(t, 8.0, u) > 0 else (DRIVE / 2, DRIVE),
}


class Cycle:
    """An open-loop brain: each motor its own oscillator (random phase), at the rate its cycle says; it records its pulses and beats."""

    def __init__(self, seed, p):
        rng = np.random.default_rng(seed + 55_000_001)
        self.f, self.dt = CYCLES[p["cycle"]], p["dt"]
        self.u = rng.random()
        self.ph = rng.random(2)
        self.clock, self.t = 0.0, 0.0
        self.pulses, self.beat_log, self.beats = [], [], []

    def stimulate(self, sensor, at):
        self.pulses.append((self.clock + at, sensor))

    def taste(self, value, at):
        pass

    def step(self):
        r = self.f(self.clock, self.u)
        out, self.beats = [], []
        for m in (0, 1):
            if r[m] <= 0:
                continue
            a = self.ph[m]
            b = a + r[m] * self.dt
            for k in range(int(math.floor(a)) + 1, int(math.floor(b)) + 1):
                at = (k - a) / r[m]
                out.append(m)
                self.beats.append((m, at))
                self.beat_log.append((self.clock + at, m))
            self.ph[m] = b - math.floor(b)
        self.clock += self.dt
        self.t = self.clock
        return out


def recorder(cls):
    """Wraps the starting brain to record its pulses and beats (watching only)."""
    class Rec(cls):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.clock, self.pulses, self.beat_log = 0.0, [], []

        def stimulate(self, sensor, at):
            self.pulses.append((self.clock + at, sensor))
            super().stimulate(sensor, at)

        def step(self):
            out = super().step()
            for m, at in getattr(self, "beats", None) or []:
                self.beat_log.append((self.clock + at, m))
            from stage2_lang.sim import WLife
            self.clock += WLife.dt
            return out
    return Rec


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    cycle, seed, first = j
    w = S.world_of(WORLD)
    if cycle == "forage":
        lf = S.make(w, "circuit", seed, first, tap=recorder)
    else:
        lf = WLife(seed, first, (lambda s: Cycle(s, {"cycle": cycle, "dt": WLife.dt})), w, seconds=True)
    l = S.live(lf, SECS)
    b = lf.brain
    k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}     # motor -> its thruster's strength
    truth = (math.log(k[0] / k[1]), 0.5 * math.log(k[0] * k[1]) - math.log(lf.v_d), math.log(lf.v_d))
    gain = sum(a - COST * c for a, c, _ in l)
    return dict(cycle=cycle, seed=seed, first=first, truth=truth, pulses=np.array(b.pulses, float).reshape(-1, 2),
                beats=np.array(b.beat_log, float).reshape(-1, 2), gain=gain, spent=spent(l),
                food=sum(a for a, _, _ in l), poison=sum(c for _, c, _ in l))


# ---- where across the corridor a block lies ---------------------------------------------------------------------------------------

LOOK = 0.25                                     # s: a sample of the truth every this often
WIN, NB = 0.5, 10                               # s, bins: the observer sees the last half-second of pulses and beats, in 50 ms bins


def corridor_job(j):
    """A life, sampling every LOOK s the nearest block in the corridor ahead (any colour): which half of the corridor it is in, told in
    the brain's own frame (the side motor 0's thruster turns the body towards, since the brain doesn't know left from right)."""
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife, _look
    cycle, seed, first = j
    w = S.world_of(WORLD)
    if cycle == "forage":
        lf = S.make(w, "circuit", seed, first, tap=recorder)
    else:
        lf = WLife(seed, first, (lambda s: Cycle(s, {"cycle": cycle, "dt": WLife.dt})), w, seconds=True)
    frame = 1.0 if lf.wire_m[0] == 0 else -1.0          # thruster 0 (the left) drives motor 0, or motor 1
    samples, nxt = [], 2.0
    while lf.t * lf.dt < SECS:
        lf.step()
        if lf.t * lf.dt >= nxt:
            nxt += LOOK
            b, K = lf.body, lf
            b.forward()
            far, hit = _look(b.xy, b.alive, b.head_xy(), (b._fc, b._fs), K.WORLD, K.BLOCK, K.RANGE, K.EAT, b.across)
            if (hit >= 0).any():
                near = hit[np.argmin(np.where(hit >= 0, far, np.inf))]
                off = float(b.across[hit == near].mean())
                samples.append((lf.t * lf.dt, frame * np.sign(off) if off != 0 else 0.0))
            else:
                samples.append((lf.t * lf.dt, np.nan))
    br = lf.brain
    return dict(cycle=cycle, seed=seed, samples=np.array(samples), pulses=np.array(br.pulses, float).reshape(-1, 2),
                beats=np.array(br.beat_log, float).reshape(-1, 2))


def corridor_features(r, t):
    P, B = r["pulses"], r["beats"]
    edges = np.linspace(t - WIN, t, NB + 1)
    f = [np.histogram(P[P[:, 1] == e, 0], edges)[0] for e in (0, 1)] + [np.histogram(B[B[:, 1] == m, 0], edges)[0] for m in (0, 1)]
    f = np.concatenate(f).astype(float)
    return np.concatenate([f, np.outer(f[:2 * NB], f[2 * NB:]).ravel() / 4.0])    # pulses x beats: when it saw, against how it turned


def corridor_report(rows):
    """Bits per look about the side (mutual information of a cross-validated linear decoder's guess with the truth, bias-corrected), the
    share of looks with a block in the corridor, and so bits a second at one look per WIN (an upper figure: looks overlap)."""
    by = {}
    for r in rows:
        by.setdefault(r["cycle"], []).append(r)
    print(f"where across the corridor the nearest block lies (its side, in the brain's frame), from the last {WIN} s of pulses and beats")
    print(f"{'cycle':9s} | in view | bits a look | bits a second")
    for c, rs in by.items():
        X, y, g = [], [], []
        for k, r in enumerate(rs):
            for t, side in r["samples"]:
                if np.isfinite(side) and side != 0:
                    X.append(corridor_features(r, t)), y.append(side), g.append(k)
        n_all = sum(len(r["samples"]) for r in rs)
        X, y, g = np.array(X), np.array(y), np.array(g)
        pred = np.zeros(len(y))
        for f in range(5):                              # folds by life, so no life's looks are both fitted and judged
            te, tr = g % 5 == f, g % 5 != f
            mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
            Z = (X - mu) / sd
            w = np.linalg.solve(Z[tr].T @ Z[tr] + 10.0 * tr.sum() * np.eye(Z.shape[1]) / 100, Z[tr].T @ (y[tr] - y[tr].mean()))
            pred[te] = Z[te] @ w + y[tr].mean()
        b = mi(y, np.sign(pred) + 1e-9 * pred, k=2)
        share = len(y) / n_all
        print(f"{c:9s} | {share:7.2f} | {b:11.3f} | {b * share / WIN:13.2f}", flush=True)


# ---- the observer's features: generic, the same for every cycle -------------------------------------------------------------------

LAGS = np.geomspace(0.03, 8.0, 41)              # s: correlogram bins' edges (40 bins)
KB = 128                                        # beats: look-backs of the beat-clocked register (D43; a revolution is 5 to 80 beats)


def _corr(times, T, edges=LAGS):
    """Pairs of pulses at each lag, as excess over chance in chance's spread."""
    n = len(times)
    if n < 2:
        return np.zeros(len(edges) - 1)
    d = []
    for i in range(n):
        j = np.searchsorted(times, times[i] + edges[-1], side="right")
        d.append(times[i + 1:j] - times[i])
    d = np.concatenate(d) if d else np.zeros(0)
    c = np.histogram(d, edges)[0]
    w = np.diff(edges)
    e = n * n / T * w * np.maximum(1 - edges[:-1] / T, 0)
    return (c - e) / np.sqrt(e + 1)


def _xcorr(beats, pulses, T, edges=np.linspace(0, 0.6, 13)):
    """Pulses at each delay after a beat, excess over chance."""
    if len(beats) == 0 or len(pulses) == 0:
        return np.zeros(len(edges) - 1)
    c = np.zeros(len(edges) - 1)
    for t in beats:
        lo, hi = np.searchsorted(pulses, t), np.searchsorted(pulses, t + edges[-1])
        c += np.histogram(pulses[lo:hi] - t, edges)[0]
    e = len(beats) * len(pulses) / T * np.diff(edges)
    return (c - e) / np.sqrt(e + 1)


def _register(beats, pulses):
    """D43's record clocked by one motor's beats: a cell a beat (did an eye pulse since the last beat?), and the coincidences at each
    look-back against chance. The beats of that motor alone, wherever they come."""
    if len(beats) < KB + 4:
        return np.zeros(KB)
    cnt = np.diff(np.searchsorted(pulses, beats))
    c = (cnt > 0).astype(float)
    q = c.mean()
    out = np.zeros(KB)
    for k in range(1, KB + 1):
        e = (len(c) - k) * q * q
        out[k - 1] = ((c[k:] * c[:-k]).sum() - e) / math.sqrt(e + 1)
    return out


def _comb(v, x):
    """D20's subharmonic summation over an excess curve v at positions x (log-spaced or not): the best fundamental's log and score."""
    cands = np.geomspace(x[0] * 1.5, x[-1] / 1.5, 60)
    s = []
    for T in cands:
        js = [j * T for j in range(1, 5) if j * T <= x[-1]]
        s.append(sum(0.84 ** (j - 1) * np.interp(t, x, v) for j, t in enumerate(js, 1)) / len(js))
    s = np.array(s)
    i = int(np.argmax(s >= 0.84 * s.max())) if s.max() > 0 else int(np.argmax(s))
    return [math.log(cands[i]), s.max()]


def _bursts(times, gap=0.15):
    """Sightings: pulses within `gap` of each other one burst. Their count, and their lengths' and pulses' quartiles."""
    if len(times) < 2:
        return [0.0] * 7
    cut = np.where(np.diff(times) > gap)[0]
    starts, ends = np.r_[0, cut + 1], np.r_[cut, len(times) - 1]
    L, N = times[ends] - times[starts], ends - starts + 1
    return [math.log1p(len(starts))] + list(np.percentile(L, [25, 50, 75])) + list(np.log(np.percentile(N, [25, 50, 75])))


def features(r, T):
    P, B = r["pulses"], r["beats"]
    P, B = P[P[:, 0] < T], B[B[:, 0] < T]
    allp = np.sort(P[:, 0])
    f = [math.log1p(len(P[P[:, 1] == e]) / T) for e in (0, 1)] + [math.log1p(len(B[B[:, 1] == m]) / T) for m in (0, 1)]
    cc = _corr(allp, T)
    f += list(cc) + _comb(cc, np.sqrt(LAGS[1:] * LAGS[:-1])) + _bursts(allp)
    for m in (0, 1):
        bm = np.sort(B[B[:, 1] == m, 0])
        f += list(_xcorr(bm, allp, T))
        rg = _register(bm, allp)
        f += list(rg) + _comb(rg, np.arange(1.0, KB + 1))
    return np.array(f, float)


# ---- the decoder, and bits ---------------------------------------------------------------------------------------------------------

H_PRIOR = {}                                    # each thing's prior differential entropy (bits), from its distribution (Monte Carlo)


def _h_prior(i):
    if i not in H_PRIOR:
        rng = np.random.default_rng(1)
        a, b, d = (np.log(2.0 ** rng.uniform(-1, 1, 400000)) for _ in range(3))
        x = (a - b, 0.5 * (a + b) - d, d)[i]
        h, e = np.histogram(x, 400, density=True)
        w = np.diff(e)
        nz = h > 0
        H_PRIOR[i] = float(-(h[nz] * np.log2(h[nz]) * w[nz]).sum())
    return H_PRIOR[i]


def decode(X, y, folds=5, seed=0):
    """Cross-validated ridge regression; lambda chosen by an inner split. Returns the out-of-fold predictions."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    out = np.zeros(len(y))
    lams = 10.0 ** np.arange(-3, 4)
    for f in range(folds):
        te = idx[f::folds]
        tr = np.setdiff1d(idx, te)
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        Z = (X - mu) / sd
        ym = y[tr].mean()
        inner = tr[: len(tr) * 4 // 5], tr[len(tr) * 4 // 5:]
        best = None
        for lam in lams:
            A = Z[inner[0]]
            w = np.linalg.solve(A.T @ A + lam * len(A) * np.eye(A.shape[1]), A.T @ (y[inner[0]] - ym))
            e = np.mean((Z[inner[1]] @ w + ym - y[inner[1]]) ** 2)
            if best is None or e < best[0]:
                best = (e, lam)
        A = Z[tr]
        w = np.linalg.solve(A.T @ A + best[1] * len(A) * np.eye(A.shape[1]), A.T @ (y[tr] - ym))
        out[te] = Z[te] @ w + ym
    return out


def bits(y, yhat, i):
    mse = float(np.mean((y - yhat) ** 2))
    return max(0.0, _h_prior(i) - 0.5 * math.log2(2 * math.pi * math.e * mse)), math.sqrt(mse)


def mi(y, yhat, k=12):
    """Mutual information (bits) between the truth and an estimate, each cut into k equal-count bins, with Miller and Madow's
    correction for few lives. A lower bound on what the pulses carry (data processing), robust to an estimate's rare large slips
    (a period taken at half or double), which squared error lets swamp everything."""
    def cut(v):
        r = np.argsort(np.argsort(v, kind="stable"), kind="stable")
        return (r * k // len(v)).astype(int)
    a, b = cut(y), cut(yhat)
    n = len(y)
    J = np.zeros((k, k))
    np.add.at(J, (a, b), 1)
    P = J / n
    pa, pb = P.sum(1), P.sum(0)
    nz = P > 0
    I = float((P[nz] * np.log2(P[nz] / np.outer(pa, pb)[nz])).sum())
    bias = ((nz.sum() - 1) - (np.count_nonzero(pa) - 1) - (np.count_nonzero(pb) - 1)) / (2 * n * math.log(2))
    return max(0.0, I - bias)


def _zcomb(v, x, lo=4.0, hi=90.0):
    """The fundamental by the excess summed over all its multiples within the register, over the square root of their number: the true
    period beats its half (whose odd teeth are empty) and its multiples (fewer teeth). Candidates in the bodies' range, 4 to 90 beats a
    revolution (a sighting spans neighbouring beats, so shorter lags always show an excess). Its log."""
    c = np.geomspace(lo, hi, 200)
    s = [np.interp(np.arange(1, int(x[-1] // T) + 1) * T, x, v).sum() / math.sqrt(int(x[-1] // T)) for T in c]
    return math.log(c[int(np.argmax(s))])


def physical(r, T):
    """The estimator that knows the physics: each motor's beats per revolution N_m, from its beat-clocked register's comb (D43), goes as
    d / k_m. Balance log(N1 / N0); stride -(log N0 + log N1) / 2; drag has no estimator of its own (the stride's stands in)."""
    P, B = r["pulses"], r["beats"]
    allp = np.sort(P[P[:, 0] < T, 0])
    lN = []
    for m in (0, 1):
        bm = np.sort(B[(B[:, 1] == m) & (B[:, 0] < T), 0])
        lN.append(_zcomb(_register(bm, allp), np.arange(1.0, KB + 1)))
    return np.array([lN[1] - lN[0], -(lN[0] + lN[1]) / 2, (lN[0] + lN[1]) / 2])


NAMES = ("balance", "stride", "drag")


def report(rows):
    by = {}
    for r in rows:
        by.setdefault(r["cycle"], []).append(r)
    print("bits: mutual information with the truth, the better of two estimators (g: ridge on generic features; p: the physical one);")
    print("then the median error of that estimator (log units: .05 is 5%). The prior's sd: " +
          ", ".join(f"{n} {np.std([r['truth'][i] for r in rows]):.2f}" for i, n in enumerate(NAMES)))
    head = " | ".join(f"{n} at {', '.join(f'{int(T)}' for T in WINDOWS)} s" for n in NAMES)
    print(f"{'cycle':9s} | gain/10 s | firings/10 s | {head}")
    for c, rs in by.items():
        y = np.array([r["truth"] for r in rs])
        cells = [[] for _ in NAMES]
        for T in WINDOWS:
            X = np.array([features(r, T) for r in rs])
            ph = np.array([physical(r, T) for r in rs])
            for i in range(3):
                g = decode(X, y[:, i])
                best = max((mi(y[:, i], g), "g", g), (mi(y[:, i], ph[:, i]), "p", ph[:, i]), key=lambda z: z[0])
                e = best[2] - y[:, i]
                e = e - np.median(e) if best[1] == "p" else e      # the physical one's constant offset is calibration, not error
                cells[i].append(f"{best[0]:.1f}{best[1]} ({np.median(np.abs(e)):.2f})")
        g = np.mean([r["gain"] for r in rs]) / SECS * 10
        fi = np.mean([len(r["beats"]) for r in rs]) / SECS * 10
        print(f"{c:9s} | {g:+9.2f} | {fi:12.0f} | " + " | ".join(", ".join(x) for x in cells), flush=True)


if __name__ == "__main__":
    import ledger
    a = sys.argv[1:]
    n = int(a[0]) if a else 400
    cycles = a[1].split(",") if len(a) > 1 else ["forage"] + list(CYCLES)
    out = f"/home/pilgrim/git/simple-learner/lab/v/dance0_{n}.pkl"
    if len(a) > 2 and a[2] == "corridor":
        ledger.start()
        cyc = a[1].split(",")
        rows = []
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            for c in cyc:
                rows += list(ex.map(corridor_job, [(c, s, ("red", "blue")[s % 2]) for s in range(SEEDS0, SEEDS0 + n)], chunksize=4))
        pickle.dump(rows, open(out.replace(".pkl", "_corridor.pkl"), "wb"))
        corridor_report(rows)
        sys.exit()
    if len(a) > 2 and a[2] == "report":
        report(pickle.load(open(out, "rb")))
        sys.exit()
    ledger.start()
    seeds = range(SEEDS0, SEEDS0 + n)
    rows = []
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for c in cycles:
            rows += list(ex.map(job, [(c, s, ("red", "blue")[s % 2]) for s in seeds], chunksize=4))
            print(f"lived {c}", flush=True)
    pickle.dump(rows, open(out, "wb"))
    report(rows)
