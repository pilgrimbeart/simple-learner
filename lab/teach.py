"""teach.py: stage 1's first experiment (PROGRAMME.md), who teaches the raw material? Main session, 2026-11-09. Predictions first:
lab/v/teach_predictions.md. On the sequence ladder (lab/ladders.py), raw material P units, a unit one letter (a one-bit memory and its tally).
  bank   all at once: the bank with a ring of every length 2..M (Count(L, good), lab/rivals.py), P = M(M+1)/2 with the default's one
  grow   a few at a time: one ring that grows a unit when its confirmed letters keep being contradicted, up to P
  events stage 2 step A: several registers, each moved by its own kind of event (good meals, trusted tastes, own clocks)
  record the last P letters revealed, and a comparing unit for each look-back k up to P/2 (the user agreed, 2026-11-09)

  lock   stage 2 step B: four clocks that adapt phase and period to surprises
  clocks D39: a bank of fixed clocks, only their phase set, by confirmed changes in the revealed letter

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/teach.py [PAIRS] [ARMS, e.g. bank,grow,record] [LADDER] [Ps, e.g. 40,80] [RUNGS, e.g. 2,5]
    (BELIEF=... PREDICT=... before it: lab/ledger.py)"""
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
            self.regs = [dict(kind=k, Pr=Pr, rec={}, agree=[0] * (Pr // 2 + 1), dis=[0] * (Pr // 2 + 1), nb={},
                              ph=(r.uniform(0, k) if not isinstance(k, str) else 0.0), tl=0.0) for k in KINDS]
            self.nt, self.best = 0, None
            self.dl, self.dt = self.food, 0
            self.setbar()

        def setbar(self):
            """The Occam bar to follow a candidate, and its cap, rising with log2 of the number of candidates (lab/rivals.py, occam)."""
            for R in self.regs:
                R["E"] = [0.0] * len(R["agree"])
            import rivals as RV
            o = RV.occam(sum(len(R["agree"]) - 1 for R in self.regs))
            self.bar, self.Emax = o["theta"], o["Emax"]

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
            got = [b for b in (rec.get(h) for h in range(i - k, i - R["Pr"], -k)) if b is not None][:3]
            own = rec.get(i)
            if not got:
                return own
            v = sum(1 if b else -1 for b in got)
            c = 1 if v > 0 else 0 if v < 0 else got[0]
            if own is None or own == c or R["nb"].get(i, 0) < 2:   # the copies' letter stands until two trusted bads at this step say otherwise
                return c                                          # (the designed brain's trust: one misread doesn't flip it)
            return own

        def predict(self):
            if self.best is None:
                self.food = self.dl
                return
            R, k = self.best
            b = self.vote(R, self.index(R), k)
            if b is not None:
                self.food = b

        def taste(self, value, at):
            if self.vouched():                          # every register and look-back scored on what it would have predicted for this taste,
                letter = self.food if value > 0 else 1 - self.food      # against the default (keep the colour, two contradictions to flip),
                dhit = self.dl == letter                                # as the bank's rivals are; then the letter recorded
                bs, best = 0, None
                for R in self.regs:
                    i = self.index(R)
                    E = R["E"]
                    for k in range(1, len(E)):
                        b = self.vote(R, i, k)
                        hit = (b == letter) if b is not None else dhit
                        E[k] = min(self.Emax, max(0.0, E[k] + (1.0 if hit > dhit else -1.0 if hit < dhit else 0.0)))
                        if b is not None:                # the long-run record, which chooses among those past the bar
                            if hit:
                                R["agree"][k] += 1
                            else:
                                R["dis"][k] += 1
                        sc = R["agree"][k] - 4 * R["dis"][k]
                        if E[k] >= self.bar and (best is None or sc > bs):
                            bs, best = sc, (R, k)
                    rec = R["rec"]
                    rec[i] = letter
                    if value < 0:
                        R["nb"][i] = R["nb"].get(i, 0) + 1
                    for old in [h for h in rec if h <= i - R["Pr"]]:
                        del rec[old]
                        R["nb"].pop(old, None)
                self.best = best
                self.nt += 1
                if value > 0:                           # the default: one letter for every step, with a tally of trust (the designed brain's)
                    self.dt = max(-1, self.dt - 1) if self.dl == letter else self.dt
                if self.dl != letter:
                    self.dt += 1
                    if self.dt >= 1:
                        self.dl, self.dt = letter, 0
            if value > 0:
                self.g += 1
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
            self.regs = [dict(kind=k, Pr=Pr, rec={}, agree=[0] * (Pr // 2 + 1), dis=[0] * (Pr // 2 + 1), nb={}) for k in ("good", "taste")]
            for T in T0:
                T = T * float(np.exp(r.normal(0, 0.1)))
                self.regs.append(dict(kind=("lock", T), Pr=Pr, rec={}, agree=[0] * (Pr // 2 + 1), dis=[0] * (Pr // 2 + 1), nb={},
                                      T=T, a=r.uniform(-T, 0), n=0, tl=0.0))
            self.setbar()

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


def clocks_cls():
    E = events_cls()
    import os
    NC, TLO, THI = int(os.environ.get("NC", 24)), 3.0, 30.0     # a bank of fixed clocks, log-spaced (24: about 10% apart; NC=60: 4%), each with its own tolerance

    class Clocks(E):
        """D39: the lock by a bank instead of by adapting. Clocks of fixed period, never tuned; what the world's changes set is only each
        clock's phase. A change is the revealed letter differing from the last confirmed one, whatever the brain predicted, confirmed by
        the next trusted taste agreeing (so a misread sets nothing, and is never recorded); the boundary lies somewhere between the last
        taste of the old letter and the first of the new, so a clock with a beat in that gap is left alone and any other has its nearest
        beat moved to the gap's nearer end (the first version moved it to the midpoint: p midpoint). A clock register's letters are
        written one taste late, at the beat their own moment falls in, so a change's first taste lands in the new beat. Each clock still
        drifts (.02 a cycle). Registers: good meals, trusted tastes, and one per clock; all scored as Events scores them."""

        def __init__(self, seed, p):
            super().__init__(seed, p)
            r = self.crng
            Pr = max(2, self.P // (2 + NC))
            new = lambda kind: dict(kind=kind, Pr=Pr, rec={}, agree=[0] * (Pr // 2 + 1), dis=[0] * (Pr // 2 + 1), nb={})
            self.regs = [new("good"), new("taste")]
            for j in range(NC):
                T = TLO * (THI / TLO) ** (j / (NC - 1)) * float(np.exp(r.normal(0, 0.03)))
                self.regs.append(dict(new(("clock", T)), T=T, a=r.uniform(-T, 0), n=0, tl=0.0))
            self.cur, self.tcur, self.pend = None, 0.0, None
            self.setbar()

        def advance(self, R):
            c = (self.t - R["tl"]) / R["T"]
            if c > 0:
                R["a"] += self.crng.normal(0.0, 0.02 * R["T"] * math.sqrt(c))
                R["tl"] = self.t
            while self.t >= R["a"] + R["T"]:
                R["a"] += R["T"]
                R["n"] += 1

        def index(self, R):
            if R["kind"] in ("good", "taste"):
                return super().index(R)
            self.advance(R)
            return R["n"]

        def index_at(self, R, t):
            """The beat a past moment fell in, by the clock as it now stands."""
            self.advance(R)
            return R["n"] if t >= R["a"] else R["n"] - int(math.ceil((R["a"] - t) / R["T"]))

        def put(self, R, i, letter, bad):
            rec = R["rec"]
            rec[i] = letter
            if bad:
                R["nb"][i] = R["nb"].get(i, 0) + 1
            for old in [h for h in rec if h <= i - R["Pr"]]:
                del rec[old]
                R["nb"].pop(old, None)

        def settle(self, letter):
            """The taste before this one, now that this one says what it was: written, moved with the boundary, or dropped as a misread."""
            if self.pend is None:
                return
            t0, l0, bad0 = self.pend
            self.pend = None
            if self.cur is not None and l0 != self.cur:
                if letter != l0:
                    return                              # not confirmed: a misread, never recorded
                lo, hi = self.tcur, t0                  # confirmed: the boundary lies between these two tastes, and that is all they say
                for R in self.regs[2:]:
                    self.advance(R)
                    if self.p.get("midpoint"):          # the first version: every clock's nearest beat moved to the midpoint
                        tb = (lo + hi) / 2
                        if tb - R["a"] > R["T"] / 2:
                            R["n"] += 1
                        R["a"] = tb
                        continue
                    a, T = R["a"], R["T"]               # a clock with a beat already between them is left alone; else its nearest
                    b = min((a - T, a, a + T), key=lambda x: 0.0 if lo <= x <= hi else min(abs(x - lo), abs(x - hi)))   # beat goes to the nearer end
                    if lo <= b <= hi:
                        continue
                    s = (lo if b < lo else hi) - b
                    R["a"] = a + s
                    if R["a"] > self.t:                 # the current beat hasn't begun after all
                        R["a"] -= T
                        R["n"] -= 1
                    elif R["a"] + T <= self.t:          # the next one already has
                        R["a"] += T
                        R["n"] += 1
            self.cur, self.tcur = l0, t0
            for R in self.regs[2:]:
                self.put(R, self.index_at(R, t0), l0, bad0)

        def taste(self, value, at):
            if self.vouched():
                letter = self.food if value > 0 else 1 - self.food
                self.settle(letter)
                dhit = self.dl == letter
                bs, best = 0, None
                for R in self.regs:
                    i = self.index(R)
                    E = R["E"]
                    for k in range(1, len(E)):
                        b = self.vote(R, i, k)
                        hit = (b == letter) if b is not None else dhit
                        E[k] = min(self.Emax, max(0.0, E[k] + (1.0 if hit > dhit else -1.0 if hit < dhit else 0.0)))
                        if b is not None:
                            if hit:
                                R["agree"][k] += 1
                            else:
                                R["dis"][k] += 1
                        sc = R["agree"][k] - 4 * R["dis"][k]
                        if E[k] >= self.bar and (best is None or sc > bs):
                            bs, best = sc, (R, k)
                    if R["kind"] in ("good", "taste"):
                        self.put(R, i, letter, value < 0)
                self.pend = (self.t, letter, value < 0)
                self.best = best
                self.nt += 1
                if value > 0:
                    self.dt = max(-1, self.dt - 1) if self.dl == letter else self.dt
                if self.dl != letter:
                    self.dt += 1
                    if self.dt >= 1:
                        self.dl, self.dt = letter, 0
            if value > 0:
                self.g += 1
            self.predict()
    return Clocks


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
    elif arm in ("grow", "record", "tree"):
        if arm not in _C:
            import tree as TR
            _C[arm] = fast.fast_cls({"grow": grow_cls, "record": record_cls, "tree": TR.tree_cls}[arm]())
        q = T.numbers(seed, {"P": P})
        q["P"] = P
        lf = WLife(seed, first, (lambda s: _C[arm](s, q)), w, seconds=True)
    elif arm in ("net", "nonet", "netnf", "netnd", "neteco", "eco1", "net1", "net2", "eco2", "net5", "eco5", "net5c", "eco5c", "net5s", "net5t", "net5c2", "net5t2", "net5v", "net5cv", "net5a", "net5at") or arm.startswith("netE") or arm.startswith("netL") or arm.startswith("net5Lu") or arm.startswith("net5k") or arm.startswith("net10kc") or arm in ("netR", "net5R", "net10R", "net10M", "net10F", "net10S", "net5S", "net10X", "netX", "netRX"):
        from stage2_lang.seconds import seconds_cls
        if arm not in _C:
            import grownet as GN
            if arm in ("neteco", "eco1"):
                _C[arm] = seconds_cls(GN.net_cls(prune=False, economy=True, one=arm == "eco1"))
            elif arm == "net1":
                _C[arm] = seconds_cls(GN.net_cls(one=True))
            elif arm in ("net5a", "net5at"):                  # plan B2: tastes about the eye followed (own action), no vouching (at: symmetry told)
                _C[arm] = seconds_cls(GN.netc_cls(agree=True, action=True, told=arm == "net5at"))
            elif arm in ("net5c", "eco5c", "net5s", "net5t", "net5c2", "net5t2", "net5cv"):   # plan B1 (s: learnt; t: told; 2: every agreeing source scored; cv: and no vouching)
                _C[arm] = seconds_cls(GN.netc_cls(prune=arm != "eco5c", economy=arm == "eco5c", sym=arm == "net5s", told=arm.startswith("net5t"),
                                                  agree=arm.endswith("2") or arm == "net5cv", novouch=arm == "net5cv"))
            elif arm in ("net5", "eco5", "net5v"):           # a stream for every sense line (net5v: no vouching, plan B2)
                _C[arm] = seconds_cls(GN.net_cls(prune=arm != "eco5", economy=arm == "eco5", senses=True, novouch=arm == "net5v"))
            elif arm in ("net2", "eco2"):                    # separate sense lines with clocks
                _C[arm] = seconds_cls(GN.net_cls(prune=arm == "net2", economy=arm == "eco2", one=True, lines=True))
            elif arm.startswith("netE"):
                _C[arm] = seconds_cls(GN.net_cls(prune=False, supply=float(arm[4:])))
            elif arm in ("net10X", "netX", "netRX"):          # strict copies (never a block and its ancestor); 10X: ten streams, on demand; RX: two streams, on demand
                _C[arm] = seconds_cls(GN.net_cls(fade=arm == "netX", ondemand=arm != "netX", senses=arm == "net10X", split=arm == "net10X", strict=True))
            elif arm in ("net10S", "net5S"):                  # recycling on demand, and the simplest partner (one step longer)
                _C[arm] = seconds_cls(GN.net_cls(fade=False, ondemand=True, senses=True, split=arm == "net10S", simplest=True))
            elif arm in ("netR", "net5R", "net10R", "net10M", "net10F"):   # recycling on demand: no fading; copies removed (M: merged); the least used of a few evicted when room is needed (F: none, growth stops when full)
                _C[arm] = seconds_cls(GN.net_cls(fade=False, ondemand=arm != "net10F", senses=arm != "netR", split=arm.startswith("net10"), merge=arm in ("net10M", "net10F")))
            elif arm.startswith("net10kc"):                  # one design for all three ladders: ten sense streams and K clocks re-phased by revealed changes
                _C[arm] = seconds_cls(GN.net_cls(senses=True, split=True, clocks=int(arm[7:]), reset="change", fade=False, ondemand=True, strict=True))
            elif arm.startswith("net5k"):                     # every sense a stream, and K of the brain's own clocks (net5k8: 8; net5kr8: reset by each bad taste)
                r = "change" if arm.startswith("net5kc") else arm.startswith("net5kr")
                _C[arm] = seconds_cls(GN.net_cls(senses=True, clocks=int(arm[6:] if r else arm[5:]), reset=r, fade=False, ondemand=True, strict=True))
            elif arm.startswith("net5Lu"):                   # every sense a stream, and trophic sibling competition: the generic brain so far
                _C[arm] = seconds_cls(GN.net_cls(prune=False, supply=float(arm[6:]), local=True, trophic=True, senses=True))
            elif arm.startswith("netL"):                     # the user's local competition: siblings share their parent's pool (Ls: burn by surprise)
                _C[arm] = seconds_cls(GN.net_cls(prune=False, supply=float(arm[5:] if arm[4] in "su" else arm[4:]), local=True,
                                                 surprise=arm.startswith("netLs"), trophic=arm.startswith("netLu")))
            else:
                _C[arm] = seconds_cls(GN.net_cls(prune=arm != "nonet", fade=arm != "netnf", dup=arm != "netnd"))
        q = T.numbers(seed, {"P": P})
        q["P"] = P
        lf = WLife(seed, first, (lambda s: _C[arm](s, q)), w, seconds=True)
    elif arm in ("events", "lock", "clocks", "treec"):
        from stage2_lang.seconds import seconds_cls          # its clocks change the colour between tastes, so not the compiled step
        if arm not in _C:
            import tree as TR
            _C[arm] = seconds_cls({"events": events_cls, "lock": lock_cls, "clocks": clocks_cls, "treec": TR.treec_cls}[arm]())
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
    if arm in ("tree", "treec"):
        b = lf.brain
        n = ((b.best["kind"] if isinstance(b.best["kind"], str) else f"clock{b.best['T']:.1f}") if b.best else "-", max(len(R["nodes"]) for R in b.regs) if b.best is None else len(b.best["nodes"]))
    elif arm in ("net", "nonet", "netnf", "netnd", "neteco", "eco1", "net1", "net2", "eco2", "net5", "eco5", "net5c", "eco5c", "net5s", "net5t", "net5c2", "net5t2", "net5v", "net5cv", "net5a", "net5at") or arm.startswith("netE") or arm.startswith("netL") or arm.startswith("net5Lu") or arm.startswith("net5k") or arm.startswith("net10kc") or arm in ("netR", "net5R", "net10R", "net10M", "net10F", "net10S", "net5S", "net10X", "netX", "netRX"):
        b = lf.brain
        n = (b.best.kind if b.best else "-", b.alive()[b.nets.index(b.best)] if b.best else max(b.alive()),
             sum(N.births for N in b.nets), sum(N.fades + N.starved for N in b.nets), sum(N.dups for N in b.nets))
    elif arm in ("events", "lock", "clocks"):
        n = (lf.brain.best[0]["kind"], lf.brain.best[1]) if lf.brain.best else None
        if arm == "clocks" and n and isinstance(n[0], tuple):
            n = (f"clock{n[0][1]:.1f}", n[1])
        if arm == "lock" and n and isinstance(n[0], tuple):
            n = (f"lock{n[0][1]:.0f}>{lf.brain.best[0]['T']:.1f}", n[1])
    return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l), sum(a + b for a, b, _ in l), time.perf_counter() - t0, n)


def run(pairs=20, dt=2.5, workers=7, seed0=L.SEEDS0 + 1000, arms=("bank", "grow"), name="seq", Ps=PS, rungs=None):
    I = R.boot(pairs)
    seeds = range(seed0, seed0 + pairs)
    print(f"== teach: {name} ladder, {pairs} pairs, {dt} ms, seeds {seed0}+; x [95%] against base and told; * solved (surely above .5); "
          f"grow's final ring lengths (median, range)", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for size, secs in L.LADDERS[name]["rungs"]:
            if rungs and size not in rungs:
                continue
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
                    if size == (0 if name == "combo" else 1):       # the plain world: the difference itself, there being no gap
                        line += f" P{P} {e[0] - b[0]:+.2f} [{R.ci(e[1] - b[1])[0]:+.2f},{R.ci(e[1] - b[1])[1]:+.2f}]"
                    else:
                        lo, hi = R.ci((e[1] - b[1]) / (t[1] - b[1]))
                        line += f" P{P} {(e[0] - b[0]) / g0:+.2f} [{lo:+.2f},{hi:+.2f}]{'*' if lo > .5 else ' '}"
                    if arm == "grow":
                        ns = [x[6] for x in res]
                        line += f" n{int(np.median(ns))}({min(ns)}-{max(ns)})"
                    if arm in ("net", "nonet", "neteco", "eco1", "net1", "net2", "eco2", "net5", "eco5", "net5c", "eco5c", "net5s", "net5t", "net5c2", "net5t2", "net5v") or arm.startswith("netE"):
                        from collections import Counter
                        line += " " + ",".join(f"{a}" for a, _ in Counter(x[6][0] for x in res).most_common(2))
                        line += f" blocks {int(np.median([x[6][1] for x in res]))} born {int(np.median([x[6][2] for x in res]))} faded {int(np.median([x[6][3] for x in res]))} dup {int(np.median([x[6][4] for x in res]))}"
                    if arm in ("tree", "treec"):
                        from collections import Counter
                        line += " " + ",".join(f"{a}" for a, _ in Counter(x[6][0] for x in res).most_common(2)) + f" nodes {int(np.median([x[6][1] for x in res]))}"
                    if arm in ("events", "lock", "clocks"):
                        from collections import Counter
                        line += " " + ",".join(f"{a}" for a, _ in Counter(f"{x[6][0]}/{x[6][1]}" if x[6] else "-" for x in res).most_common(2))
                        line += f" {np.mean([x[5] for x in res]):.0f}s"
                    line += " |"
                print(line, flush=True)


COL = L.COL

if __name__ == "__main__":
    import ledger
    ledger.start()
    a = sys.argv[1:]
    run(int(a[0]) if a else 20, arms=tuple(a[1].split(",")) if len(a) > 1 else ("bank", "grow"), name=a[2] if len(a) > 2 else "seq",
        Ps=tuple(int(x) for x in a[3].split(",")) if len(a) > 3 else PS, rungs=[int(x) for x in a[4].split(",")] if len(a) > 4 and a[4][0].isdigit() else None,
        seed0=next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), L.SEEDS0 + 1000))   # s96000: fresh seeds
