"""teach.py: stage 1's first experiment (PROGRAMME.md), who teaches the raw material? Main session, 2026-11-09. Predictions first:
lab/v/teach_predictions.md. On the sequence ladder (lab/ladders.py), raw material P units, a unit one letter (a one-bit memory and its tally).
  bank   all at once: the bank with a ring of every length 2..M (Count(L, good), lab/rivals.py), P = M(M+1)/2 with the default's one
  grow   a few at a time: one ring that grows a unit when its confirmed letters keep being contradicted, up to P
  events stage 2 step A: several registers, each moved by its own kind of event (good meals, trusted tastes, own clocks)
  record the last P letters revealed, and a comparing unit for each look-back k up to P/2 (the user agreed, 2026-11-09)

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/teach.py [PAIRS] [ARMS, e.g. bank,grow,record] [LADDER] [Ps, e.g. 40,80]"""
import math
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R

PS = (4, 8, 16, 32, 64)
_C = {}


def grow_cls():
    D = L.designed_cls()

    class Grow(D):
        """One ring of letters, starting at one unit. Each position holds a letter and a tally (as the designed brain); a position is
        confirmed by a vouched good since its last flip. A vouched bad at a confirmed position adds 1 to frustration F, which leaks
        (tau, s). At F >= theta the ring takes one more unit, if the material has one, its letters copied round. No length is told."""

        def __init__(self, seed, p):
            super().__init__(seed, dict(p, lad="seq", size=1))
            self.P, self.F, self.tF, self.grew = int(p["P"]), 0.0, 0.0, []
            self.conf = [False]

        def taste(self, value, at):
            p = self.p
            c = self.g % self.n
            if self.vouched():
                if value > 0:
                    self.tally[c] = max(-1, self.tally[c] - 1)
                    self.conf[c] = True
                else:
                    if self.conf[c]:
                        self.F = self.F * math.exp(-(self.t - self.tF) / p.get("tau_f", 60.0)) + 1.0
                        self.tF = self.t
                    self.tally[c] += 1
                    if self.tally[c] >= 1:
                        self.bits[c], self.tally[c], self.conf[c] = 1 - self.bits[c], 0, False
                        self.flips.append(self.t)
                    if self.F >= p.get("theta_f", 2.0) and self.n < self.P:
                        n = self.n + 1
                        self.bits = [self.bits[j % self.n] for j in range(n)]
                        self.tally, self.conf, self.n, self.F = [0] * n, [False] * n, n, 0.0
                        self.grew.append((self.t, n))
            if value > 0:
                self.g += 1
            self.food = self.bits[self.g % self.n]
    return Grow


def record_cls():
    D = L.designed_cls()

    class Record(D):
        """The last P letters revealed, each at its good-meal count, and a comparing unit for each look-back k up to P/2: a newly revealed
        letter adds an agreement or a disagreement to every k whose letter k back is known. Follows the letter k back for the best k."""

        def __init__(self, seed, p):
            super().__init__(seed, dict(p, lad="seq", size=1))
            self.P = int(p["P"])
            self.rec = {}
            K = max(1, self.P // 2)
            self.agree, self.dis = [0] * (K + 1), [0] * (K + 1)
            self.k = 0

        def taste(self, value, at):
            if self.vouched():
                letter = self.food if value > 0 else 1 - self.food
                g = self.g
                if self.rec.get(g) != letter:
                    self.rec[g] = letter
                    for k in range(1, len(self.agree)):
                        b = self.rec.get(g - k)
                        if b is not None:
                            if b == letter:
                                self.agree[k] += 1
                            else:
                                self.dis[k] += 1
                    for old in [h for h in self.rec if h <= g - self.P]:
                        del self.rec[old]
                    best, self.k = 0, 0
                    for k in range(1, len(self.agree)):
                        s = self.agree[k] - 4 * self.dis[k]
                        if self.agree[k] and s > best:
                            best, self.k = s, k
            if value > 0:
                self.g += 1
            if self.k:                                  # a vote of every copy of this step's letter in the record (k, 2k, ... back, and this step's own),
                v, last = 0, None                       # so one misread can't outvote the rest; ties to the most recent
                for h in range(int(self.g), int(self.g) - int(self.P), -int(self.k)):
                    b = self.rec.get(h)
                    if b is not None:
                        v += 1 if b else -1
                        last = b if last is None else last
                if last is not None:
                    self.food = 1 if v > 0 else 0 if v < 0 else last
            elif self.g in self.rec:
                self.food = self.rec[self.g]
    return Record


def events_cls():
    D = L.designed_cls()
    KINDS = ("good", "taste", 1.0, 2.0, 4.0)        # what moves each register: good meals, any trusted taste, the brain's own clocks (s)

    class Events(D):
        """Stage 2, step A: several registers, each moved by its own kind of event, each P/5 units with look-back comparators up to half its
        length (the record arm's unit). A trusted taste reveals one letter to every register, at its current step. Follows the best register
        and look-back, by a vote of every copy of this step's letter. A clock starts at a random phase and drifts (.02 of a cycle per cycle)."""

        def __init__(self, seed, p):
            super().__init__(seed, dict(p, lad="seq", size=1))
            self.P = int(p["P"])
            r = np.random.default_rng([int(seed), 13])
            self.crng = r
            Pr = max(2, self.P // len(KINDS))
            self.regs = [dict(kind=k, Pr=Pr, rec={}, agree=[0] * (Pr // 2 + 1), dis=[0] * (Pr // 2 + 1),
                              ph=(r.uniform(0, k) if not isinstance(k, str) else 0.0), tl=0.0) for k in KINDS]
            self.nt, self.best = 0, None

        def index(self, R):
            k = R["kind"]
            if k == "good":
                return int(self.g)
            if k == "taste":
                return int(self.nt)
            c = (self.t - R["tl"]) / k
            if c > 0:
                R["ph"] += self.crng.normal(0.0, 0.02 * k * math.sqrt(c))
                R["tl"] = self.t
            return int(math.floor((self.t + R["ph"]) / k))

        def vote(self, R, i, k):
            """What register R, read k back, says this step's letter is: its own letter if revealed, else a vote of the three most recent
            copies k, 2k, ... back (one misread can't outvote two), ties to the most recent; None if it has none."""
            rec = R["rec"]
            if i in rec:
                return rec[i]
            got = [b for b in (rec.get(h) for h in range(i - k, i - R["Pr"], -k)) if b is not None][:3]
            if not got:
                return None
            v = sum(1 if b else -1 for b in got)
            return 1 if v > 0 else 0 if v < 0 else got[0]

        def predict(self):
            if self.best is None:
                return
            R, k = self.best
            b = self.vote(R, self.index(R), k)
            if b is not None:
                self.food = b

        def taste(self, value, at):
            if self.vouched():                          # every register and look-back scored on what it would have predicted for this taste,
                letter = self.food if value > 0 else 1 - self.food      # as the bank's rivals are; then the letter recorded
                bs, best = 0, None
                for R in self.regs:
                    i = self.index(R)
                    for k in range(1, len(R["agree"])):
                        b = self.vote(R, i, k)
                        if b is not None:
                            if b == letter:
                                R["agree"][k] += 1
                            else:
                                R["dis"][k] += 1
                        sc = R["agree"][k] - 4 * R["dis"][k]
                        if R["agree"][k] and sc > bs:
                            bs, best = sc, (R, k)
                    rec = R["rec"]
                    rec[i] = letter
                    for old in [h for h in rec if h <= i - R["Pr"]]:
                        del rec[old]
                self.best = best
                self.nt += 1
            if value > 0:
                self.g += 1
            if self.best is None and self.vouched() and value < 0:
                self.food = 1 - self.food
            self.predict()
    return Events


def lock_cls():
    E = events_cls()
    T0 = (3.0, 6.0, 12.0, 24.0)                     # the adaptive clocks' starting periods (s): a bank, as Scheirer's resonators

    class Lock(E):
        """Stage 2, step B: the free-running clocks replaced by adaptive ones (Large & Kolen 1994): a surprise (a trusted bad) pulls each
        clock's phase towards it (alpha) and its period by the error over the beats since its last surprise (eta), so its beats come to
        fall at the world's changes. Each still drifts (.02 a cycle). Registers: good meals, trusted tastes, and one per clock."""

        def __init__(self, seed, p):
            super().__init__(seed, p)
            r = self.crng
            Pr = max(2, self.P // (2 + len(T0)))
            self.regs = [dict(kind=k, Pr=Pr, rec={}, agree=[0] * (Pr // 2 + 1), dis=[0] * (Pr // 2 + 1)) for k in ("good", "taste")]
            for T in T0:
                T = T * float(np.exp(r.normal(0, 0.1)))
                self.regs.append(dict(kind=("lock", T), Pr=Pr, rec={}, agree=[0] * (Pr // 2 + 1), dis=[0] * (Pr // 2 + 1),
                                      T=T, a=r.uniform(-T, 0), n=0, tl=0.0))

        def advance(self, R):
            if R["kind"] in ("good", "taste"):
                return
            c = (self.t - R["tl"]) / R["T"]
            if c > 0:
                R["a"] += self.crng.normal(0.0, 0.02 * R["T"] * math.sqrt(c))
                R["tl"] = self.t
            while self.t >= R["a"] + R["T"]:            # beats passed: the anchor moves on a beat at a time
                R["a"] += R["T"]
                R["n"] += 1

        def index(self, R):
            if R["kind"] in ("good", "taste"):
                return super().index(R)
            self.advance(R)
            return R["n"]

        def surprise(self):
            p = self.p
            for R in self.regs[2:]:
                self.advance(R)
                e = self.t - R["a"]                     # time since the current beat began
                if e > R["T"] / 2:                      # nearer the next beat: it came early
                    e -= R["T"]
                R["T"] = float(np.clip(R["T"] + p.get("eta_l", 0.3) * e, 1.0, 60.0))
                R["a"] += p.get("alpha_l", 0.7) * e
                if e < 0 and self.t >= R["a"]:          # pulled forward past now: the next beat has begun
                    pass

        def taste(self, value, at):
            if value < 0 and self.vouched():
                self.surprise()
            super().taste(value, at)
    return Lock


def rings(M):
    import rivals as RV
    return lambda r, src: [(RV.Count(n, src["good"]), 1) for n in range(2, M + 1)]


def M_of(P):
    return max(m for m in range(1, 20) if m * (m + 1) // 2 <= P)


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S, fast
    from stage2_lang.sim import WLife
    import rivals as RV
    import table as T
    text, arm, P, seed, first, secs = j
    t0 = time.perf_counter()
    w = S.world_of(text)
    if arm == "bank":
        M = M_of(P)
        lf = RV.make(w, seed, first, {"rivals": rings(M), **RV.occam(max(M - 1, 1))})
    elif arm in ("grow", "record"):
        if arm not in _C:
            _C[arm] = fast.fast_cls(grow_cls() if arm == "grow" else record_cls())
        q = T.numbers(seed, {"P": P})
        q["P"] = P
        lf = WLife(seed, first, (lambda s: _C[arm](s, q)), w, seconds=True)
    elif arm in ("events", "lock"):
        from stage2_lang.seconds import seconds_cls          # its clocks change the colour between tastes, so not the compiled step
        if arm not in _C:
            _C[arm] = seconds_cls(events_cls() if arm == "events" else lock_cls())
        q = T.numbers(seed, {"P": P})
        q["P"] = P
        lf = WLife(seed, first, (lambda s: _C[arm](s, q)), w, seconds=True)
        lf.tell = lambda W: W.brain.predict()
    else:
        return L.job((text, arm, {}, seed, first, secs))
    l = S.live(lf, secs)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    n = getattr(lf.brain, "n", None) if arm == "grow" else None
    if arm in ("events", "lock"):
        n = (lf.brain.best[0]["kind"], lf.brain.best[1]) if lf.brain.best else None
        if arm == "lock" and n and isinstance(n[0], tuple):
            n = (f"lock{n[0][1]:.0f}>{lf.brain.best[0]['T']:.1f}", n[1])
    return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l), sum(a + b for a, b, _ in l), time.perf_counter() - t0, n)


def run(pairs=20, dt=2.5, workers=7, seed0=L.SEEDS0 + 1000, arms=("bank", "grow"), name="seq", Ps=PS):
    I = R.boot(pairs)
    seeds = range(seed0, seed0 + pairs)
    print(f"== teach: {name} ladder, {pairs} pairs, {dt} ms, seeds {seed0}+; x [95%] against base and told; * solved (surely above .5); "
          f"grow's final ring lengths (median, range)", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for size, secs in L.LADDERS[name]["rungs"]:
            text = L.LADDERS[name]["world"](size)
            run1 = lambda arm, P=0: list(ex.map(job, [(text, arm, P, s, c, float(secs)) for s in seeds for c in COL]))
            b, t = L.scored(run1("circuit"), secs, I), L.scored(run1("vtold"), secs, I)
            g0 = t[0] - b[0]
            print(f"-- rung {size}, {secs} s: base {b[0]:.2f} told {t[0]:.2f}", flush=True)
            for arm in arms:
                line = f"   {arm:5s}|"
                for P in Ps:
                    res = run1(arm, P)
                    e = L.scored(res, secs, I)
                    if size == 1:
                        line += f" P{P} {e[0] - b[0]:+.2f} [{R.ci(e[1] - b[1])[0]:+.2f},{R.ci(e[1] - b[1])[1]:+.2f}]"
                    else:
                        lo, hi = R.ci((e[1] - b[1]) / (t[1] - b[1]))
                        line += f" P{P} {(e[0] - b[0]) / g0:+.2f} [{lo:+.2f},{hi:+.2f}]{'*' if lo > .5 else ' '}"
                    if arm == "grow":
                        ns = [x[6] for x in res]
                        line += f" n{int(np.median(ns))}({min(ns)}-{max(ns)})"
                    if arm in ("events", "lock"):
                        from collections import Counter
                        line += " " + ",".join(f"{a}" for a, _ in Counter(str(x[6][0]) if x[6] else "-" for x in res).most_common(2))
                    line += " |"
                print(line, flush=True)


COL = L.COL

if __name__ == "__main__":
    a = sys.argv[1:]
    run(int(a[0]) if a else 20, arms=tuple(a[1].split(",")) if len(a) > 1 else ("bank", "grow"), name=a[2] if len(a) > 2 else "seq",
        Ps=tuple(int(x) for x in a[3].split(",")) if len(a) > 3 else PS)
