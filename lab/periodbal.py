"""periodbal.py: the plan's step 5, the body learned by prediction, not by outcome (D20): while B scans, one motor alone
turns it at a steady rate, so what it sees comes round again once a revolution, and a revolution's period goes as
1 / that thruster's strength. B scans with each motor in turn (the motor alternating at each scan's start); a bank of
coincidence counters per motor (a histogram of the intervals between eye pulses within one scan) finds each motor's
period (the shortest whose comb of multiples scores within `top` of the best: what recurs); the drive's balance x
(log of motor 0's rate over motor 1's) is set to log(T0 / T1), which straightens the drive (k0 g0 = k1 g1), every
`every` s once each motor has `need` intervals. The goal (keep what is chased ahead) is evolution's; the model of
this body, the life's. No jitter, no outcome.

    python periodbal.py ARM [SEEDS] [seconds=2000] [body=1] [k=v ...]
    ARM: learn, alt (alternating scans, balance fixed at 0: the alternation's own cost), fixed (B: balance 0, no
    sweeps), oracle (B told its body's balance); allbody=1: bodies varied in every factor (bodies.SPREAD too)
    (k: every, need, top, n, w, hi; cal_every, cal_len: sweeps, the brain's own experiments: every cal_every s, for
    cal_len s, it ignores what it sees and turns with one motor alone at its scan rate, the motor alternating; only
    the sweeps' pulses are counted (B's own scans are mostly shorter than a revolution, ended by a food sighting);
    stall: sweeping stops once the last 3 estimates of the balance (each after a sweep, once each motor has
    stall_need intervals) agree within `stall`: its own
    adjustment stalled, a body not changing within a life; scans=1: B's own scans counted beside the sweeps;
    merge=s: pulses closer than s counted as one event, a block's pass; pernorm=1: each sweep one vote, its pairs
    scaled to one before pooling, each lag's excess over the votes' spread: coincidences come in clumps; maxrate:
    a sweep with more eye pulses a second than this discarded (a block close by recurs twice a revolution);
    gate=m: a sweep only when frustrated, fewer than m meals since the last sweep's slot (a body that drives well
    isn't swept); bank=K: K log-spaced counters (fundamental_bank), local=1: chance from the neighbours; binary=1 (cap=c: c pulses a stage, default 1): the
    delay line as one-bit stages, pulses within a stage merged;
    scan_rate=1: B's scans at the scan rate, not scaled by
    the balance's gain g0; scan_skip, scan_min: of B's own scans only the part after
    scan_skip s counted, and only if at least scan_min s long; cal_first: the first slot's time; cal_fast: the slots' spacing while a motor has fewer than fast_need intervals)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from units import TICK

BIN, MAXLAG = 0.01, 17.0


def fundamental(h, null, lo=0.3, hi=4.0, w=0.04, n=8, top=0.84, octave=0, var=None):
    """From a histogram of intervals (bins of BIN s from 0) and what chance would give (each scan's pulses placed at
    random within it): the period whose multiples recur most beyond chance, each multiple's excess (observed less
    chance, over chance's spread, where chance expects enough) weighted top^(k-1) and summed (subharmonic summation, Hermes 1988:
    a multiple of the period loses the teeth between, a fraction of it gains empty ones)."""
    c = np.concatenate([[0.0], np.cumsum(h)])
    z = np.concatenate([[0.0], np.cumsum(null)])
    v = None if var is None else np.concatenate([[0.0], np.cumsum(var)])
    def excess(x):
        a, b = int(max(0, (x - w) / BIN)), int(min(len(h), (x + w) / BIN))
        e = z[b] - z[a] if b > a else 0.0
        if v is not None:                               # each sweep a vote (pernorm): over the votes' spread
            s2 = v[b] - v[a] if b > a else 0.0
            return ((c[b] - c[a]) - e) / np.sqrt(s2) if s2 > 0 and e > 0 else 0.0
        return ((c[b] - c[a]) - e) / np.sqrt(e) if e >= 5 else 0.0   # (as evidence: over chance's spread)
    Ts = np.arange(lo, hi, 0.01)
    sc = np.array([sum(top ** (k - 1) * excess(k * T) for k in range(1, n + 1)) for T in Ts])
    best = float(Ts[int(np.argmax(sc))])
    if not octave:
        return best
    cands = []                                          # octave=1: the best, its double and its half, by the strength
    for x in (best / 2, best, best * 2):                # of each one's own first recurrence, among combs scoring at
        if lo <= x < hi:                                # least half the best's (a wide circle shows half the period)
            j = int(round((x - lo) / 0.01))
            near = range(max(0, j - 3), min(len(Ts), j + 4))
            jj = max(near, key=lambda i: sc[i])
            if sc[jj] >= 0.5 * sc.max():
                cands.append((excess(Ts[jj]), float(Ts[jj])))
    return max(cands)[1] if cands else best


def fundamental_bank(h, null, K=64, lo=0.3, hi=4.0, n=8, top=0.84, local=0, wide=0.25, plain=0, counts=None, **_):
    """fundamental as a circuit could hold it: K coincidence counters at log-spaced lags (0.1 to MAXLAG s), each
    collecting the intervals within half a spacing of its lag; each candidate period one of the counters within
    lo..hi, scored by fixed wiring from the counters nearest its multiples (weights top^(k-1)); local=1: chance as the
    mean of the counters within a factor 1 + wide either side (lateral inhibition), not computed from the sweeps."""
    edges = np.exp(np.linspace(np.log(0.1), np.log(MAXLAG), K + 1))
    lag = np.sqrt(edges[:-1] * edges[1:])
    c = np.concatenate([[0.0], np.cumsum(h)])
    z = np.concatenate([[0.0], np.cumsum(null)])
    ix = np.clip((edges / BIN).astype(int), 0, len(h))
    cnt, exp = c[ix[1:]] - c[ix[:-1]], z[ix[1:]] - z[ix[:-1]]
    if counts is not None:                              # binary: the delay line's stages, counted directly
        cnt = counts
    if local:                                           # chance: the neighbours' mean, excluding itself
        nb = [[j for j in range(K) if j != i and abs(np.log(lag[j] / lag[i])) <= np.log(1 + wide)] or
              [j for j in (i - 1, i + 1) if 0 <= j < K] for i in range(K)]
        exp = np.array([cnt[j].mean() for j in nb])
    ex = np.where(exp >= 5, (cnt - exp) / (1.0 if plain else np.sqrt(np.maximum(exp, 1e-9))), 0.0)   # plain=1: no sqrt
    cand = [i for i in range(K) if lo <= lag[i] < hi]
    def near(x):
        return int(np.argmin(abs(np.log(lag / x))))
    sc = [sum(top ** (k - 1) * ex[near(k * lag[i])] for k in range(1, n + 1) if k * lag[i] < MAXLAG) for i in cand]
    return float(lag[cand[int(np.argmax(sc))]])


class PeriodBal(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.h = [np.zeros(int(MAXLAG / BIN)), np.zeros(int(MAXLAG / BIN))]
        self.null = [np.zeros(int(MAXLAG / BIN)), np.zeros(int(MAXLAG / BIN))]   # what chance would give
        self.var = [np.zeros(int(MAXLAG / BIN)), np.zeros(int(MAXLAG / BIN))]   # (pernorm: the votes' spread)
        self.n = [0, 0]
        self.start = 0.0
        self.lags = (np.arange(int(MAXLAG / BIN)) + 0.5) * BIN
        self.sm, self.ep, self.was_scan = 1, [], False
        self.x, self.next = 0.0, p.get("every", 20.0)
        self.T = [None, None]
        self.trace = []
        self.cal_until, self.cal_next, self.cphase = -1.0, p.get("cal_first", p.get("cal_every", 0)) if p.get("cal_every") else 1e18, 0.0
        self.stalled, self.xs, self.sweeps, self.in_sweep = False, [], 0, False
        self.meals = 0                                  # (gate: meals since the last sweep's slot)
        self.mt, self.fc = [], 0.0                      # (gate_rate: the meals' times on the foraging clock fc)
        K = int(p.get("bank", 96))                      # binary=1: a delay line of K one-bit stages at log-spaced lags
        self.edges = np.exp(np.linspace(np.log(0.1), np.log(MAXLAG), K + 1))
        self.hb = [np.zeros(K), np.zeros(K)]

    def taste(self, value, at):
        super().taste(value, at)
        if value > 0:
            self.meals += 1
            self.mt.append(self.fc)

    def content(self):
        """gate_rate=1: not frustrated if the meals of the last min(fc, 32 s) of foraging (the sweeps' time left out:
        a sweep's own fast isn't frustration) come at gate per 32 s or more."""
        if not self.p.get("gate_rate"):
            return self.meals >= self.p["gate"]
        W = min(self.fc, 32.0)
        self.mt = [m for m in self.mt if m > self.fc - 32.0]
        return W > 0 and len(self.mt) >= self.p["gate"] * W / 32.0

    def _fund(self, h, null, var=None, **kw):
        if self.p.get("bank"):                          # bank=K: the counters a circuit could hold
            return fundamental_bank(h, null, K=int(self.p["bank"]), local=self.p.get("local", 0),
                                    wide=self.p.get("wide", 0.25), plain=self.p.get("plain", 0),
                                    counts=self.hb[0 if h is self.h[0] else 1] if self.p.get("binary") else None, **kw)
        return fundamental(h, null, var=var, **kw)

    def stimulate(self, sensor, at):
        super().stimulate(sensor, at)
        if self.was_scan or self.in_sweep:
            self.ep.append(self.t + at)

    def _close(self, scan=False):
        if scan and (self.p.get("scan_skip") or self.p.get("scan_min")):   # B's own scan: its steady part only
            self.start += self.p.get("scan_skip", 0.0)  # scan_skip: the spin-up left out
            self.ep = [v for v in self.ep if v >= self.start]
            if self.t - self.start < self.p.get("scan_min", 0.0):
                self.ep = []                            # scan_min: a scan this short dropped
        if self.p.get("merge") and self.ep:            # merge=s: a pass, not a pulse: pulses closer than s one event
            ev = [self.ep[0]]
            for v in self.ep[1:]:
                if v - ev[-1] >= self.p["merge"]:
                    ev.append(v)
            self.ep = ev
        if self.p.get("maxrate") and len(self.ep) > self.p["maxrate"] * max(self.t - self.start, BIN):
            self.ep = []                                # maxrate: a sweep this dense (a block close by) discarded
        if len(self.ep) > 1 and self.p.get("binary"):    # each new pulse meets each stage a pulse occupies: one count
            x = np.array(self.ep)
            for j in range(1, len(x)):
                d = x[j] - x[:j]
                b = np.searchsorted(self.edges, d[(d > 0.1) & (d < MAXLAG)]) - 1
                b = b[(b >= 0) & (b < len(self.hb[0]))]
                c = np.bincount(b, minlength=len(self.hb[0]))   # cap=c: a stage holds up to c pulses (binary: 1)
                self.hb[self.sm] += np.minimum(c, self.p.get("cap", 1))
        if len(self.ep) > 1:
            x = np.array(self.ep)
            d = (x[None, :] - x[:, None])[np.triu_indices(len(x), 1)]
            d = d[(d > 0.1) & (d < MAXLAG)]
            E, N = max(self.t - self.start, BIN), len(x)
            ex = N * (N - 1) * np.clip(E - self.lags, 0, None) / E ** 2 * BIN
            wt = 1.0 / max(len(d), 1) if self.p.get("pernorm") else 1.0   # pernorm=1: each sweep's pairs scaled to one
            np.add.at(self.h[self.sm], (d / BIN).astype(int), wt)
            self.n[self.sm] += len(d)
            self.null[self.sm] += ex * wt
            self.var[self.sm] += ex * wt * wt
        self.ep = []

    def step(self):
        p = self.p
        out = super().step()
        if p.get("cal_every"):                          # sweeps
            if self.t >= self.cal_next and not self.stalled and p.get("gate") and self.content():
                self.cal_next += p["cal_every"]         # gate: not frustrated, no sweep this slot
                self.meals = 0
            if self.t >= self.cal_next and not self.stalled:
                fast = p.get("cal_fast") and min(self.n) < p.get("fast_need", 1000)
                self.cal_next = self.t + (p["cal_fast"] if fast else p["cal_every"])   # cal_fast: slots closer early
                self.meals = 0
                if self.was_scan:                       # (a scan of B's own cut short by the sweep)
                    self._close(scan=True)
                self.cal_until, self.sm, self.start, self.ep = self.t + p.get("cal_len", 5.0), 1 - self.sm, self.t, []
                self.was_scan, self.in_sweep = False, True
            if self.t >= self.cal_until:
                self.fc += TICK                         # the foraging clock: time not sweeping
            if self.t < self.cal_until:
                self.ep_sweep = True
                self.cphase += p["scan"] * TICK
                k = int(self.cphase)
                self.cphase -= k
                return [self.sm] * k + self._learn()
            if self.in_sweep:
                self._close()
                self.in_sweep = False
                self.sweeps += 1
                if min(self.n) >= p.get("stall_need", 2000) and p.get("stall"):
                    kw = {k: p[k] for k in ("top", "n", "w", "hi", "octave") if k in p}
                    T = [self._fund(self.h[m], self.null[m], var=self.var[m] if p.get('pernorm') else None, **kw) for m in (0, 1)]
                    self.xs = (self.xs + [float(np.log(T[0] / T[1]))])[-3:]
                    if len(self.xs) == 3 and max(self.xs) - min(self.xs) <= p["stall"]:
                        self.stalled = True
            if not p.get("scans"):                      # scans=1: B's own scans counted too
                return out + self._learn()
        driving = self.t - self.last_drive < p["hold"]
        running = not driving and self.t - self.last_food > p["bored"]
        scanning = not (driving or running)
        if scanning and not self.was_scan:              # a scan begins: the other motor
            self.sm = 1 - self.sm
            self.start = self.t
        if self.was_scan and not scanning:
            self._close(scan=True)
        self.was_scan = scanning
        if scanning and not p.get("fixed_scan"):
            if p.get("scan_rate"):                      # scan_rate=1: B's scan at its own rate, not scaled by g0
                self.cphase += p["scan"] * TICK
                k = int(self.cphase)
                self.cphase -= k
                out = [self.sm] * k
            else:
                out = [self.sm] * len(out)
        return out + self._learn()

    def _learn(self):
        p = self.p
        if p.get("learn", 1) and self.t >= self.next:
            self.next += p.get("every", 20.0)
            if min(self.n) >= p.get("need", 100):
                kw = {k: p[k] for k in ("top", "n", "w", "hi", "octave") if k in p}
                self.T = [self._fund(self.h[m], self.null[m], var=self.var[m] if p.get('pernorm') else None, **kw) for m in (0, 1)]
                self.x = float(np.clip(np.log(self.T[0] / self.T[1]), -1.4, 1.4))
                self.p["g0"], self.p["g1"] = float(np.exp(self.x / 2)), float(np.exp(-self.x / 2))
            self.trace.append((self.t, self.x, list(self.n)))
        return []


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    from discrete.bodies import THRUSTERS, draw, vary
    arm, p, spread, seed, seconds, poison = job
    q = dict(M.drawn(p, spread, seed), **{k: p[k] for k in ("every", "need", "top", "n", "w", "hi") if k in p})
    q["learn"] = 0 if arm in ("alt", "fixed", "oracle") else 1
    if arm in ("fixed", "oracle"):                      # no sweeps, B's scans as designed (motor 0)
        q = {k: v for k, v in q.items() if k not in ("cal_every",)}
        q["fixed_scan"] = 1
    lf = Life(seed, poison, brain=lambda s: PeriodBal(s, q))
    f = None
    if p.get("body", 1):
        from discrete.bodies import SPREAD
        f = draw(seed, {**SPREAD, **THRUSTERS} if p.get("allbody") else THRUSTERS)   # allbody=1: every factor varied
        vary(lf, f)
    thr = {m: t for t, m in lf.motor.items()}
    def k(m):                                           # motor m's thruster's turn, as bodies.VariedBody fires it
        t = thr[m]
        side = np.sqrt(f.get("asymmetry", 1.0)) ** (1 if t == "left" else -1)
        return f.get("strength", 1.0) * side * f.get(t, 1.0)
    right = float(np.log(k(1) / k(0))) if f else 0.0
    if arm == "oracle":
        lf.brain.p["g0"], lf.brain.p["g1"] = float(np.exp(right / 2)), float(np.exp(-right / 2))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.right = right
    l.x, l.n, l.trace, l.T = lf.brain.x, lf.brain.n, lf.brain.trace, lf.brain.T
    l.sweeps = lf.brain.sweeps
    return l


def lives(arm, p, spread, seeds, seconds, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(life, [(arm, p, spread, s, seconds, c) for s in seeds for c in ("red", "blue")]))


if __name__ == "__main__":
    import pickle
    from minimal.spec import summary
    from discrete.poison import show
    arm = sys.argv[1]
    args = [a for a in sys.argv[2:] if "=" not in a]
    lo, hi = (int(x) for x in (args[0] if args else "0:32").split(":"))
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:] if "=" in a)}
    seconds = kw.pop("seconds", 2000.0)
    p, spread = M.from_bench()
    L = lives(arm, dict(p, **kw), spread, range(lo, hi), seconds)
    tag = f"pb_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items())) + f"_{lo}-{hi}"
    x = np.array([l.x for l in L]); r = np.array([l.right for l in L])
    extra = (f"  balance vs the oracle's: median |error| {np.median(abs(x - r)):.2f}, within 0.2 {np.mean(abs(x - r) < 0.2):.0%},"
             f" correlation {np.corrcoef(x, r)[0, 1] if x.std() > 0 and r.std() > 0 else 0:.2f}; intervals per motor (median)"
             f" {np.median([min(l.n) for l in L]):.0f}; sweeps (median) {np.median([getattr(l, 'sweeps', 0) for l in L]):.0f}")
    print(show(tag, summary(L)) + extra, flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/lab/v/{tag}.lives", "wb"))
