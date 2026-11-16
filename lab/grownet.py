"""grownet.py: the growing network (the user, 2026-11-12, after Bena & Goodman 2025; PROGRAMME.md, the current stage). Main session.
Predictions first: lab/v/grownet_predictions.md.

Blocks appear where something keeps surprising, each comes to stand for one situation, duplicates are removed, blocks build on blocks, all
limited by a fixed supply of material, and a block nobody uses fades, its fading pruning back whatever only it used. No goal but
prediction: a block's readout guesses what comes next when it fires. A generalisation of D40's tree, which fixed the partner of every
recruit (the next older symbol) and never pruned.

Two streams of events, as the tree's two registers: `good`, the letter revealed at each good-meal count; `eaten`, the colour eaten at
each taste. On each stream:
  - The senses: a unit for each symbol, firing at a step when that symbol is there. Never fade.
  - A block (u, v): fires at step i when v fires at i and u fired at i - span(v); its span is span(u) + span(v). So blocks are
    sequences of sequences: a block may join any two units, senses or blocks.
  - A readout on every unit: what came next each time it fired (two tallies).
  - Predicting: of the units firing at the last step, the longest whose tallies lean one way says the letter (ties: the surer).
  - Birth (novelty beneath contradiction): when the unit that spoke is contradicted (it has seen both letters), and material is free, a
    new block (u, speaker) is made, u drawn at random among the units that fired span(speaker) steps before (they were active together).
  - Use: a unit that spoke and was right is used; its use passes down to the units it is made of, and theirs to theirs (support flows
    back from the behaviour). Use is a trace fading with time constant FADE seconds.
  - Fading: a block older than FADE whose trace is below DIE is recycled, and with it every block made from it.
  - Duplicates: two blocks firing on exactly the same steps over the last DUP steps they could both fire on: the less used is recycled.
    FAULT (found 2026-11-13): a block and its own ancestor fire alike while the ancestor's other branches rest, so they were taken for
    copies; strict=True excludes them (D59). The default keeps the fault so that earlier arms reproduce.
Material: P units a stream, the senses included. Choosing between streams and the default (keep the colour, two contradictions to flip)
as the tree does, with its Occam bar. Told nothing of the ladder, its size or the life's length.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/teach.py [PAIRS] net [LADDER] [Ps] [RUNGS]
    (arm net; nonet: births and readouts alone, no fading or removal of duplicates; netnf: no fading; netnd: no duplicate removal;
    neteco: neither, but an economy: a right guess earns 1, kept in part and paid on to the units it is made of; firing costs; a
    parent funds its newborn; a block in debt is recycled (Baum 1999's conserved credit; trophic support, van Ooyen & Willshaw 1999).
    netE<r>: neither, but the blood supply at r a second (blocks firing together share it, by their use; the starved are recycled))"""
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import ladders as L

FADE = 200.0                                    # s: a use trace's time constant; a block unused for this long is recycled
DIE = 0.1                                       # a trace below this is unused
DUP = 30                                        # steps: duplicates fire alike over this many
H0 = 5.0                                        # a newborn's store of energy (supply variant): one firing's need is 1
REST = 0.01                                     # per s: what a block burns at rest (supply variant), so one that never fires starves
FIRE_COST = 0.0                                 # economy variant: what a block pays each time it fires (.05 starved the general blocks, R16)
RENT = 0.005                                    # economy variant: per s, what every block pays to exist (a grant lasts 200 s unearned)
GRANT = 1.0                                     # economy variant: what a parent gives a newborn from its savings
KEEP = 0.5                                      # economy variant: the share of an income a block keeps; the rest is paid to its parts
WM_BETA = float(__import__("os").environ.get("WM_BETA", 0.5))   # weighted majority: a wrong guess multiplies a stream's weight by this
WM_BAR = __import__("os").environ.get("WM_BAR") == "1"   # weighted majority: only streams whose weight beats the default's vote
WM_SHARE = float(__import__("os").environ.get("WM_SHARE", 0.0))   # fixed share among the speakers (2026-11-15)
WM_SPEC = __import__("os").environ.get("WM_SPEC") == "1"   # weighted majority of specialists: only speakers updated, their total kept
PHASES = __import__("os").environ.get("PHASES", "")   # "1" (diagnosis): phase streams on clock 0's told period; "2": phase oscillators locking to changes
PH_MAX = int(__import__("os").environ.get("PH_MAX", 8))   # the longest cycle a told phase offers (PHASES=1)
PHN = int(__import__("os").environ.get("PHN", 6))   # phase oscillators (PHASES=2)
PLL_AVG = __import__("os").environ.get("PLL_AVG") == "1"   # oscillators average their accepted intervals (T12)
PLL_FLOOR, PLL_P2 = float(__import__("os").environ.get("PLL_FLOOR", 0.02)), 0.15
DVOTE = __import__("os").environ.get("DVOTE") == "1"   # (D71) the colour chosen by a vote of experts judged on their choices
DV_BETA = float(__import__("os").environ.get("DV_BETA", 0.8))   # a wrong recommendation's weight factor
BT = float(__import__("os").environ.get("BT", 1.0))   # (D70) the Bayes weights' temper: likelihood ratios raised to this power
GRADED = __import__("os").environ.get("GRADED") == "1"   # (D70) graded readouts on every bank integrator, in the Bayes mixture
GR_ETA = float(__import__("os").environ.get("GR_ETA", 0.05))
LMIX = __import__("os").environ.get("LMIX") == "1"   # (D70) the colour chosen by logistic mixing of the streams' log-odds
LMIX_ETA = float(__import__("os").environ.get("LMIX_ETA", 0.02))   # its learning rate
SURP = __import__("os").environ.get("SURP") == "1"   # (D70) surprise-driven change detection in every block's tallies
SURP_A, SURP_B = 1.0, 100.0                     # its prior on the rate of changes: 1 in 100 tastes, learned from experienced change probabilities
RT_K, RT_ACQ = 6, 40                            # (D68) rhythm trackers: how many, after how many noticed changes
RT_GRID = np.exp(np.linspace(np.log(3.0), np.log(30.0), 120))   # s: the acquiring resonators' trial slot lengths
LB_JOINT = __import__("os").environ.get("LB_JOINT") == "1"   # (D69) the bank also counts each colour with each outcome
LB_LETTER = __import__("os").environ.get("LB_LETTER") == "1"   # (D70) a signed leaky sum of the revealed letter, at every time constant
LB_LINES = ("e0", "e1", "good", "bad", "c0", "c1", "m0", "m1") + (("c0g", "c0b", "c1g", "c1b") if LB_JOINT else ()) + (("ld",) if LB_LETTER else ())   # (D67) every signal
SAYS_N = __import__("os").environ.get("SAYS_N") == "1"   # (D67) a stream speaks through its firing unit with the most evidence
POOL_BITS = float(__import__("os").environ.get("POOL_BITS", 1.0))   # bits saved a stream must show for each unit beyond its share
LB_LIVE = __import__("os").environ.get("LB_LIVE") == "1"   # (D67) bank streams write whenever their reading changes, not only at tastes
LB_FINE = __import__("os").environ.get("LB_FINE") == "1"   # (D67) a finer bank: time constants a factor 2 apart, counts exact to 7
LB_T = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0) if LB_FINE else (1.0, 4.0, 16.0, 64.0)   # s: its time constants, log-spaced
ACOUNT = __import__("os").environ.get("ACOUNT") == "1"   # running averages read as whole counts of recent events
PLL_RES = __import__("os").environ.get("PLL_RES") == "1"   # a resonator after capture: rate corrected by the slide of the changes' mean phase
RES_L, RES_EVERY, RES_G = 0.9, 5, 0.7
PLL_SPAN = __import__("os").environ.get("PLL_SPAN") == "1"   # slot length from the whole span since the first change (T19)
POSC_TOLD = __import__("os").environ.get("POSC_TOLD") == "1"
PMONO = __import__("os").environ.get("PMONO") == "1"
PDRIFT = float(__import__("os").environ.get("PDRIFT", 0.01))   # an oscillator's drift a slot (log)
PLL_S, PLL_P, PLL_WIN = 0.2, 0.3, 0.25          # an oscillator's slot-length and phase steps toward a revealed change, and its window
CPHASE = __import__("os").environ.get("CPHASE") == "1"   # counters read from time since an anchor (a diagnosis, 2026-11-14)
NODRIFT = __import__("os").environ.get("NODRIFT") == "1"   # a diagnosis: the brain's clocks without drift (not allowed in a design)
LOCK = float(__import__("os").environ.get("LOCK", 0.0))   # clocks' period locking rate (0: off), 2026-11-13
LOCK_WIN = float(__import__("os").environ.get("LOCK_WIN", 0.5))   # ... only clocks whose period is within this fraction of the interval
HIST = 96                                       # steps of history kept on a stream (spans beyond it can't fire)


class Net:
    def __init__(self, kind, P, rng, prune=True, fade=True, dup=True, supply=0.0, economy=False, alphabet=2, strict=False):
        self.kind, self.P, self.rng, self.prune = kind, P, rng, prune
        self.strict = strict                            # copies: never a block and its own ancestor (the fix of 2026-11-13)
        self.economy = economy
        self.fade, self.dup = fade and prune, dup and prune
        self.supply, self.pool, self.tp = supply, 0.0, 0.0          # supply: the blood's refill, per s (0: off); the pool holds 10 s of it
        self.starved = 0
        self.units = {}                         # id -> dict(u, v, span, n=[0,0], use, born, kids)
        self.hist = {}                          # step -> symbol
        self.next = 0
        for s in range(alphabet):
            self._add(None, None, 1, 0.0, sym=s)
        self.E, self.agree, self.dis = 0.0, 0, 0
        self.births = self.fades = self.dups = 0

    def _add(self, u, v, span, t, sym=None):
        k = self.next
        self.next += 1
        self.units[k] = dict(u=u, v=v, span=span, n=[0, 0], use=0.0, tu=t, born=t, kids=set(), sym=sym, sig=[], h=H0, th=t, own=0.0, to=t, cash=0.0)
        for p in (u, v):
            if p is not None:
                self.units[p]["kids"].add(k)
        return k

    def add_value(self, firing, x):
        """Graded readouts (2026-11-13): every unit firing keeps the count, sum and sum of squares of the value that followed, so its
        evidence includes how far, not only which way."""
        for k in firing:
            u = self.units.get(k)
            if u is not None:
                v = u.setdefault("val", [0, 0.0, 0.0])
                v[0] += 1
                v[1] += x
                v[2] += x * x

    @staticmethod
    def welch(a, c):
        """Standard errors between two units' mean values (a against the control c); 0 with too few."""
        if a is None or c is None or a[0] < 3 or c[0] < 3:
            return 0.0
        ma, mc = a[1] / a[0], c[1] / c[0]
        va = max(a[2] / a[0] - ma * ma, 0.0) * a[0] / (a[0] - 1)
        vc = max(c[2] / c[0] - mc * mc, 0.0) * c[0] / (c[0] - 1)
        return (ma - mc) / (math.sqrt(va / a[0] + vc / c[0]) + 1e-9)

    def _descends(self, a, b):
        """Whether a is built (at any depth) on b."""
        x = self.units.get(a)
        if x is None or x["sym"] is not None:
            return False
        return x["u"] == b or x["v"] == b or self._descends(x["u"], b) or self._descends(x["v"], b)

    def _remove(self, k):
        if k not in self.units:
            return
        x = self.units.pop(k)
        for c in list(x["kids"]):
            self._remove(c)
        for p in (x["u"], x["v"]):
            if p in self.units:
                self.units[p]["kids"].discard(k)

    def fires(self, k, i, memo):
        key = (k, i)
        if key in memo:
            return memo[key]
        x = self.units[k]
        if x["sym"] is not None:
            r = self.hist.get(i) == x["sym"]
        else:
            r = self.fires(x["v"], i, memo) and self.fires(x["u"], i - self.units[x["v"]]["span"], memo)
        memo[key] = r
        return r

    def firing(self, i):
        memo = {}
        return [k for k in self.units if self.fires(k, i, memo)], memo

    def _room(self):
        """Room to grow: under its own share, or (a shared pool, D67) the pool has material free and this stream is saving bits over the
        default: material goes to the streams that pay in bits. Market (D67): a stream that has saved POOL_BITS a unit beyond its share
        takes a unit of capacity from a stream that has saved nothing (its least used leaf of a few drawn, recycled)."""
        if len(self.units) < self.P:
            return True
        mk = getattr(self, "market", None)
        if mk is not None and getattr(self, "saved", 0.0) > POOL_BITS * (len(self.units) - self.base + 1):
            poor = [N for N in mk.nets if N is not self and getattr(N, "saved", 0.0) <= 0.0 and N.P > 3]
            if poor:
                v = poor[int(self.rng.integers(len(poor)))]
                leaves = [k for k, x in v.units.items() if x["sym"] is None and not x["kids"]]
                if leaves:
                    t = getattr(mk, "t", 0.0)
                    pick = [leaves[int(self.rng.integers(len(leaves)))] for _ in range(4)]
                    v._remove(min(pick, key=lambda k: v._trace(v.units[k], t)))
                v.P -= 1
                self.P += 1
                return True
        mp = getattr(self, "mpool", None)
        return mp is not None and mp.free() > 0 and getattr(self, "saved", 0.0) > POOL_BITS * (len(self.units) - self.P + 1)   # each extra
        # unit paid for by POOL_BITS bits saved (an MDL price: material earned by compression)

    def says(self, i):
        f, _ = self.firing(i)
        best, key = None, None
        for k in f:
            n = self.units[k]["n"]
            if n[0] != n[1]:
                kk = (n[0] + n[1],) if SAYS_N else (self.units[k]["span"], abs(n[1] - n[0]) / (n[0] + n[1]))   # SAYS_N: the most evidence
                if key is None or kk > key:
                    best, key = k, kk
        return best, f

    def _trace(self, x, t):
        return x["use"] * math.exp(-(t - x["tu"]) / FADE)

    def pay(self, k, amount):
        """Conserved credit (Baum 1999): a unit keeps KEEP of an income and pays the rest to the units it is made of, half each. The
        senses keep all (they are paid by the world)."""
        x = self.units.get(k)
        if x is None:
            return
        if x["sym"] is not None:
            x["cash"] += amount
            return
        x["cash"] += KEEP * amount
        for p in (x["u"], x["v"]):
            self.pay(p, (1.0 - KEEP) * amount / 2.0)

    def bill(self, i):
        """Each block firing at this step pays FIRE_COST; one in debt is recycled, with its dependants."""
        f, _ = self.firing(i)
        fs = set(f)
        for k in list(self.units):
            x = self.units.get(k)
            if x is not None and x["sym"] is None:
                x["cash"] -= RENT * (self.tnow - x["th"]) + (FIRE_COST if k in fs else 0.0)
                x["th"] = self.tnow
                if x["cash"] < 0:
                    self._remove(k)
                    self.starved += 1

    def own_credit(self, k, t):
        x = self.units[k]
        x["own"], x["to"] = x["own"] * math.exp(-(t - x["to"]) / FADE) + 1.0, t

    def credit(self, k, t, w=1.0):
        x = self.units.get(k)
        if x is None:
            return
        x["use"], x["tu"] = self._trace(x, t) + w, t
        for p in (x["u"], x["v"]):
            if p is not None:
                self.credit(p, t, w)

    def learn(self, i, letter, t, speaker, firing):
        for k in firing:
            x = self.units[k]
            n = x["n"]
            if SURP and n[0] + n[1] > 0:               # (D70, the user: surprise, not forgetting) the block's change probability from
                q = (n[letter] + 0.5) / (n[0] + n[1] + 1.0)   # its own surprise against its own learned rate of changes (Nassar et al.
                h = (x.get("cs", 0.0) + SURP_A) / (x.get("cn", 0) + SURP_B)   # 2010; Adams & MacKay 2007): old tallies discounted by it
                cpp = h * 0.5 / (h * 0.5 + (1.0 - h) * q)
                x["cs"], x["cn"] = x.get("cs", 0.0) + cpp, x.get("cn", 0) + 1
                n[0] *= 1.0 - cpp
                n[1] *= 1.0 - cpp
            n[letter] += 1
        # birth beneath a contradiction: the deepest firing unit, if it has seen both letters
        deep = max(firing, key=lambda k: self.units[k]["span"], default=None)
        rich = deep is not None and (not self.economy or self.units[deep]["sym"] is not None or self.units[deep]["cash"] >= GRANT)
        room = self._room()
        if getattr(self, "ondemand", False) and deep is not None and rich and min(self.units[deep]["n"]) >= 1 and not room:
            # recycling on demand (Dohare et al. 2024's comparator): a birth is due and material is full, so the least used of a few
            # blocks drawn at random (with no blocks built on them, and not the one about to be built on) is recycled
            leaves = [k for k, x in self.units.items() if x["sym"] is None and not x["kids"] and k != deep]
            if leaves:
                pick = [leaves[int(self.rng.integers(len(leaves)))] for _ in range(4)]
                self._remove(min(pick, key=lambda k: self._trace(self.units[k], t)))
                self.fades += 1
        if deep is not None and rich and min(self.units[deep]["n"]) >= 1 and (room or len(self.units) < self.P):
            span = self.units[deep]["span"]
            before, _ = self.firing(i - span)
            if before and getattr(self, "simplest", False):  # simplest first: the partner is one of the shortest units active then
                m = min(self.units[k]["span"] for k in before)
                before = [k for k in before if self.units[k]["span"] == m]
            if before:
                u = before[int(self.rng.integers(len(before)))]
                if self.units[u]["span"] + span <= HIST // 2:
                    k = self._add(u, deep, self.units[u]["span"] + span, t)
                    if self.supply > 0 or getattr(self, "local", False):   # the young are protected by their parents' standing: the weaker parent's record
                        pu, pv = self.units[u], self.units[deep]
                        self.units[k]["own"] = min(pu["own"] * math.exp(-(t - pu["to"]) / FADE), pv["own"] * math.exp(-(t - pv["to"]) / FADE))
                        if getattr(self, "trophic", False):
                            self.units[k]["use"], self.units[k]["tu"] = min(self._trace(pu, t), self._trace(pv, t)), t
                    self.units[k]["n"][letter] = 1        # it fired now, and saw this letter
                    self.births += 1
                    if self.economy:                    # the parent funds its newborn from its savings (the senses from the world)
                        if self.units[deep]["sym"] is None:
                            self.units[deep]["cash"] -= GRANT
                        self.units[k]["cash"] = GRANT

    def feed(self, i, t):
        """The blood supply: the blocks firing at this step share what the pool holds, each by its use (and a little whatever its use),
        each needing 1; all burn REST a second; a block whose store runs out is recycled, with its dependants."""
        self.pool = min(10.0 * self.supply, self.pool + self.supply * (t - self.tp))
        self.tp = t
        f, _ = self.firing(i)
        # a block with dependants alive is fed by them (support flows back from users), so it neither draws nor pays; the rest compete,
        # each by its own record of being right when it spoke (not the credit passed down from its users)
        fb = [k for k in f if self.units[k]["sym"] is None and not self.units[k]["kids"]]
        w = {k: self.units[k]["own"] * math.exp(-(t - self.units[k]["to"]) / FADE) + 0.1 for k in fb}
        W = sum(w.values())
        give = min(self.pool, float(len(fb)))
        for k, x in list(self.units.items()):
            if x["sym"] is None:
                if not x["kids"]:
                    x["h"] -= REST * (t - x["th"])
                x["th"] = t
        for k in fb:
            g = give * w[k] / W if W > 0 else 0.0
            self.units[k]["h"] += g - 1.0
        self.pool -= give
        for k in list(self.units):
            x = self.units.get(k)
            if x is not None and x["sym"] is None and x["h"] <= 0:
                self._remove(k)
                self.starved += 1

    def err(self, t):
        """The stream's recent rate of wrong guesses (a trace with time constant FADE), .5 before any."""
        w = math.exp(-(t - getattr(self, "te", t)) / FADE)
        a, d = getattr(self, "ra", 0.0) * w, getattr(self, "rd", 0.0) * w
        return (d + 1.0) / (a + d + 2.0)

    def guessed(self, right, t):
        w = math.exp(-(t - getattr(self, "te", t)) / FADE)
        self.ra, self.rd, self.te = getattr(self, "ra", 0.0) * w + right, getattr(self, "rd", 0.0) * w + (not right), t

    def feed_local(self, i, t):
        """The user's local competition (2026-11-12): every unit holds a pool refilled at `supply` a second (10 s of it at most); when
        blocks built on it (its children, it their v) fire together, they share its pool by their own record of being right, each
        needing 1; a block never competes with its parents, nor with blocks under another parent. All blocks burn REST a second; a
        block whose store runs out is recycled with its dependants."""
        f, _ = self.firing(i)
        groups = {}
        for k in f:
            x = self.units[k]
            if x["sym"] is None:
                groups.setdefault(x["v"], []).append(k)
        burn = REST * (2.0 * self.err(t) if getattr(self, "surprise", False) else 1.0)
        for k, x in self.units.items():
            if x["sym"] is None:
                x["h"] -= burn * (t - x["th"])
                x["th"] = t
        for par, kids in groups.items():
            P_ = self.units.get(par)
            if P_ is None:
                continue
            P_["pool"] = min(10.0 * self.supply, P_.get("pool", 0.0) + self.supply * (t - P_.get("tp", t)))
            P_["tp"] = t
            if getattr(self, "trophic", False):          # standing includes credit passed down from the blocks built on it
                w = {k: self._trace(self.units[k], t) + 0.1 for k in kids}
            else:
                w = {k: self.units[k]["own"] * math.exp(-(t - self.units[k]["to"]) / FADE) + 0.1 for k in kids}
            W = sum(w.values())
            give = min(P_["pool"], float(len(kids)))
            for k in kids:
                self.units[k]["h"] += give * w[k] / W - 1.0
            P_["pool"] -= give
        for k in list(self.units):
            x = self.units.get(k)
            if x is not None and x["sym"] is None and x["h"] <= 0:
                self._remove(k)
                self.starved += 1

    def tidy(self, i, t):
        if getattr(self, "local", False):
            self.feed_local(i, t)
            return
        if self.economy:
            self.tnow = t
            self.bill(i)
        if self.supply > 0:
            self.feed(i, t)
        if not self.prune:
            return
        f, memo = self.firing(i)
        fs = set(f)
        for k, x in list(self.units.items()):
            if k not in self.units or x["sym"] is not None:
                continue
            x["sig"].append(k in fs)
            del x["sig"][:-DUP]
            if self.fade and t - x["born"] > FADE and self._trace(x, t) < DIE:
                self._remove(k)
                self.fades += 1
        blocks = [k for k, x in self.units.items() if self.dup and x["sym"] is None and len(x["sig"]) >= DUP]
        seen = {}
        for k in blocks:
            if k not in self.units:
                continue
            s = tuple(self.units[k]["sig"])
            if not any(s):
                continue
            j = seen.get(s)
            if j is not None and j in self.units and getattr(self, "strict", False) and (self._descends(j, k) or self._descends(k, j)):
                continue                                # a block and its own ancestor fire alike while its other branches rest: not copies
            if j is not None and j in self.units:
                a, b = (j, k) if self._trace(self.units[j], t) >= self._trace(self.units[k], t) else (k, j)
                if getattr(self, "merge", False) and not self._descends(a, b):
                    # copies merged: the blocks built on the copy are handed to its twin (they fire alike), not recycled with it
                    for c in list(self.units[b]["kids"]):
                        x = self.units.get(c)
                        if x is None:
                            continue
                        if x["u"] == b:
                            x["u"] = a
                        if x["v"] == b:
                            x["v"] = a
                        self.units[a]["kids"].add(c)
                    self.units[b]["kids"] = set()
                self._remove(b)
                self.dups += 1
                if a in self.units:
                    seen[s] = a
            else:
                seen[s] = k

    def write(self, i, sym, keep=False):
        if keep and i in self.hist:
            return
        self.hist[i] = sym
        self.hist.pop(i - HIST, None)


def net_cls(prune=True, fade=True, dup=True, supply=0.0, economy=False, one=False, lines=False, senses=False, novouch=False, local=False,
            surprise=False, trophic=False, clocks=0, ondemand=False, split=False, merge=False, simplest=False, strict=False, reset=False,
            eyes=0, avgs=0, joint=0, vote=False, wmaj=False, counters=0, allavg=False, since=0, lbank=False, rhythm=False):
    """eyes (2026-11-13): for each eye, `eyes` clocks of its own (periods 0.5 to 10 s, drawn per life); at each beat the stream records
    how many pulses that eye gave since the last beat (0, 1-2, 3-8, 9 or more), so blocks can grow over recent eye activity.
    avgs (the user, 2026-11-13: a running average is a measure to try for any signal): for each eye, `avgs` running averages of its pulse
    rate, each with its own time constant (0.5 to 10 s, drawn per life), sampled at a beat of that period; the stream records whether the
    average is low, middle or high against the thirds of what that average has read so far in the life (nothing told of the world's rates)."""
    """one: a single stream, every taste, its symbol the colour eaten and whether it was good (four symbols): no stream chosen by us.
    senses: a stream for every sense line, each ticking when its line fires (every taste, a good taste, a bad taste, red eaten, blue
    eaten), each recording the same four symbols at its ticks; none chosen by us, the gate choosing among them by their record."""
    ALINES = ((0, 1, "good", "bad", "m0", "m1") + (("c0", "c1") if ACOUNT else ())) if allavg else (0, 1)   # allavg (2026-11-14): a running average of every signal, not only the eyes
    TICKS = {"every": lambda good, eaten: True, "good": lambda good, eaten: good, "bad": lambda good, eaten: not good,
             "red": lambda good, eaten: eaten == 0, "blue": lambda good, eaten: eaten == 1}
    D = L.designed_cls()
    import rivals as RV

    class GrowNet(D):
        KINDS = (tuple(f"{c}:{f}" for c in TICKS for f in ("colour", "outcome")) + tuple(f"clock{c}" for c in range(clocks))
                 + tuple(f"eye{e}c{j}" for e in (0, 1) for j in range(eyes)) + tuple(f"avg{e}c{j}" for e in ALINES for j in range(avgs))
                 + tuple(f"cnt{j}n{m}" for j in range(min(counters, clocks)) for m in range(2, 9))
                 + tuple(f"since{j}" for j in range(min(since, clocks))) + (tuple(f"ph{m}" for m in range(2, PH_MAX + 1)) if PHASES == "1" and clocks else ())
                 + (tuple(f"pq{i}n{m}" for i in range(PHN) for m in range(2, 9)) if PHASES == "2" and clocks else ())
                 + (tuple(f"lb{ln}t{j}" for ln in LB_LINES for j in range(len(LB_T))) if lbank else ())
                 + (tuple(f"rt{i}n{m}" for i in range(RT_K) for m in range(2, 9)) if rhythm else ()) if split else
                 (tuple(TICKS) + tuple(f"clock{c}" for c in range(clocks))) if senses else ("taste",) if one or lines else ("good", "eaten"))

        def __init__(self, seed, p):
            super().__init__(seed, dict(p, lad="seq", size=1))
            self.seed_ = seed
            P = max(3, int(p["P"]) // len(self.KINDS))
            rng = np.random.default_rng([int(seed), 77])
            if lines:                                   # separate sense lines with clocks (Net2)
                self.nets = [Net2("taste", P, rng, prune=prune, fade=fade, dup=dup, supply=supply, economy=economy)]
            else:
                self.nets = [Net(k, P, rng, prune, fade, dup, supply, economy,
                                 5 * int(k.split("n")[-1]) if k.startswith("rt") else (15 if k.startswith("lbld") else 12 if LB_FINE else 8) if k.startswith("lb") else 5 * int(k[2:]) if k.startswith("ph") else 5 * int(k.split("n")[-1]) if k.startswith("pq") else 9 if k.startswith("since") else int(k.split("n")[-1]) if k.startswith("cnt") else (5 if ACOUNT else 3) if k.startswith("avg") else 4 if k.startswith("eye") else 5 if k.startswith("clock") else 2 if split else 4 if k == "taste" or senses else 2,
                                 strict=strict) for k in self.KINDS]
            for N in self.nets:
                N.local, N.surprise, N.trophic, N.ondemand, N.merge, N.simplest = local, surprise, trophic, ondemand, merge, simplest
            if getattr(self, "MARKET", False):          # (D67) capacity moves from streams that save no bits to those that do
                for N in self.nets:
                    N.market, N.base = self, N.P
            if getattr(self, "POOL", False):            # (D67) half of each stream's share pooled; drawn only by streams saving bits
                total = int(p["P"])
                for N in self.nets:
                    N.P = max(3, N.P // 2)
                    N.mpool = self
                self._ptotal = total
                if trophic:
                    pass
            self.na = 0
            self.cnt = {k: 0 for k in self.KINDS}
            if joint:                                   # coincidences across streams, one more stream for the gate (JointNet)
                self.nets.append(JointNet(self, max(3, int(p["P"]) // len(self.KINDS)) if joint is True else joint, np.random.default_rng([int(seed), 83])))
                self.cnt["joint"] = 1
                o = RV.occam(len(self.nets))
            # the brain's own clocks (clocks > 0): periods log-uniform 3 to 30 s, random phase, drifting; never told the world's
            crng = np.random.default_rng([int(seed), 79])
            self.clk = [dict(T=float(np.exp(crng.uniform(np.log(3.0), np.log(30.0))))) for _ in range(clocks)]
            for c in self.clk:
                c["next"] = float(crng.uniform(0.0, c["T"]))
            self.crng, self.lastsym = crng, 4
            self.byk = None
            erng = np.random.default_rng([int(seed), 81])
            self.eclk = [dict(e=e, j=j, T=float(np.exp(erng.uniform(np.log(0.5), np.log(10.0)))), n=0) for e in (0, 1) for j in range(eyes)]
            for c in self.eclk:
                c["next"] = float(erng.uniform(0.0, c["T"]))
            self.aclk = [dict(e=e, j=j, T=float(np.exp(erng.uniform(np.log(0.5), np.log(30.0 if allavg else 10.0)))), r=0.0, tr=0.0, hist=[])
                         for e in ALINES for j in range(avgs)]
            for c in self.aclk:
                c["next"] = float(erng.uniform(0.0, c["T"]))
            o = RV.occam(len(self.nets))
            self.bar, self.Emax = o["theta"], o["Emax"]
            self.best = None
            self.dl, self.dt = self.food, 0

        def place(self, N):
            if senses:
                return self.cnt[N.kind]
            return int(self.g) if N.kind == "good" else self.na

        def _rt_change(self, t):
            """(D68) the rhythm trackers hear a noticed change. Before acquisition: resonators across slot lengths 3 to 30 s (forgetting
            circular means of change times); after RT_ACQ changes, a tracker at each of the RT_K strongest distinct peaks. Each tracker: a
            Kalman filter on phase (in slots) and rate, gated (Gardner; Bar-Shalom); a change should sit at a whole number of slots."""
            if not hasattr(self, "rtz"):
                self.rtz, self.rtn, self.rts = np.zeros(len(RT_GRID), complex), 0, []
            self.rtn += 1
            if not self.rts:
                self.rtz = 0.98 * self.rtz + np.exp(2j * np.pi * t / RT_GRID)
                if self.rtn >= RT_ACQ:
                    R = np.abs(self.rtz)
                    peaks = [i for i in range(1, len(R) - 1) if R[i] >= R[i - 1] and R[i] >= R[i + 1] and R[i] >= 0.5 * R.max()]
                    peaks.sort(key=lambda i: -R[i])
                    chosen = []
                    for i in peaks:
                        if all(abs(RT_GRID[i] / RT_GRID[j] - 1) > 0.1 for j in chosen):
                            chosen.append(i)
                        if len(chosen) == RT_K:
                            break
                    for i in chosen:
                        T_ = float(RT_GRID[i])
                        self.rts.append(dict(f=1.0 / T_, th=float(round(t / T_)), tl=t, P=np.diag([0.05, (0.02 / T_) ** 2]), k=None))
                return
            for x in self.rts:
                dt = t - x["tl"]
                F = np.array([[1.0, dt], [0.0, 1.0]])
                th, f = x["th"] + x["f"] * dt, x["f"]
                Pp = F @ x["P"] @ F.T + np.diag([0.0, 1e-11 * dt])
                e = th - round(th)
                x["tl"] = t
                if abs(e) > 0.3:                        # gated: taken as a false change
                    x["th"], x["f"], x["P"] = th, f, Pp
                    continue
                K = Pp[:, 0] / (Pp[0, 0] + 0.04)
                x["th"], x["f"] = th - K[0] * e, f - K[1] * e
                x["P"] = Pp - np.outer(K, Pp[0, :])

        def _rt_step(self):
            """Each tracker's place: five bins a slot; a bin written (modulo 5m, m 2 to 8) when the phase moves on past it."""
            for i, x in enumerate(getattr(self, "rts", [])):
                kb = int(math.floor(5.0 * (x["th"] + x["f"] * (self.t - x["tl"]))))
                if x["k"] is None or kb > x["k"]:
                    x["k"] = kb
                    for m in range(2, 9):
                        N = self.byk[f"rt{i}n{m}"]
                        k = self.cnt[N.kind]
                        N.write(k, kb % (5 * m))
                        N.tidy(k, self.t)
                        self.cnt[N.kind] = k + 1
                    self.predict()

        def free(self):
            return self._ptotal - sum(len(N.units) for N in self.nets)

        def _lb(self, line, amount=1.0):
            """(D67) the leaky-integrator bank: every event type, time constants LB_T (scale-invariant memory of recent history, Shankar &
            Howard 2012); an event adds 1 to each integrator of its line, each decaying with its own time constant."""
            if not lbank:
                return
            b = self.__dict__.setdefault("lbr", {})
            for j, T in enumerate(LB_T):
                r, tr = b.get((line, j), (0.0, self.t))
                b[(line, j)] = (r * math.exp(-(self.t - tr) / T) + amount, self.t)

        def _lb_write(self, changed_only=False):
            """Each integrator read as a recent count on a log scale (0, 1, 2-3, 4-7, ..., 64+: eight symbols), written to its stream.
            changed_only (LB_LIVE, send-on-delta): only the streams whose reading has changed since they last wrote."""
            b = self.__dict__.setdefault("lbr", {})
            last = self.__dict__.setdefault("lbs", {})
            wrote = False
            for ln in LB_LINES:
                for j, T in enumerate(LB_T):
                    r, tr = b.get((ln, j), (0.0, self.t))
                    c = r * math.exp(-(self.t - tr) / T)
                    if ln == "ld":                      # (D70) the signed evidence line: its leaky sum rounded, -7 to +7 (15 symbols)
                        sym = int(min(max(round(c), -7), 7)) + 7
                    elif LB_FINE:                       # exact counts up to 7, then a log scale (8-15, 16-31, 32-63, 64+): 12 symbols
                        cr = int(round(c))
                        sym = cr if cr < 8 else min(8 + int(math.log2(cr / 8.0)), 11)
                    else:
                        sym = min(int(math.log2(1.0 + c)), 7)
                    if changed_only and last.get((ln, j)) == sym:
                        continue
                    last[(ln, j)] = sym
                    wrote = True
                    N = self.byk[f"lb{ln}t{j}"]
                    k = self.cnt[N.kind]
                    N.write(k, sym)
                    N.tidy(k, self.t)
                    self.cnt[N.kind] = k + 1
            return wrote

        def _gr_vals(self):
            """(D70) every bank integrator's current value (decayed to now): the graded readouts' inputs."""
            out = {}
            for (ln, j), (r, tr) in getattr(self, "lbr", {}).items():
                out[(ln, j)] = r * math.exp(-(self.t - tr) / LB_T[j])
            return out

        def _gr_p1(self, key, v):
            a, c = self.__dict__.setdefault("gr", {}).get(key, (0.0, 0.0))
            z = a * v + c
            return 1.0 / (1.0 + math.exp(-max(min(z, 30.0), -30.0)))

        def _pdef(self, letter):
            """The default's probability for a letter: its own KT record of how often the last revealed letter came again."""
            h, n = getattr(self, "dkt", (0, 0))
            q = (h + 0.5) / (n + 1.0)
            return q if letter == self.dl else 1.0 - q

        @staticmethod
        def _pk(N, k, letter):
            """A speaking unit's probability for a letter: the KT estimate from its tallies (Krichevsky & Trofimov 1981)."""
            n = N.units[k]["n"]
            return (n[letter] + 0.5) / (n[0] + n[1] + 1.0)

        def _lmix_inputs(self):
            """(D70) the logistic mixer's inputs: each stream's log-odds for letter 1 (0 when silent), the default's, and a bias."""
            st = lambda q: math.log(min(max(q, 1e-4), 1 - 1e-4) / (1 - min(max(q, 1e-4), 1 - 1e-4)))
            xs = {"_bias": 1.0, "_def": st(self._pdef(1))}
            for N in self.nets:
                k, _ = N.says(self.place(N) - 1)
                xs[N.kind] = st(self._pk(N, k, 1)) if k is not None else 0.0
            return xs

        def _dv_recs(self):
            """(D71) each expert's recommended letter: the default's, each speaking stream's, each graded readout's (values as now)."""
            recs = {"_def": self.dl}
            for N in self.nets:
                k, _ = N.says(self.place(N) - 1)
                if k is not None:
                    n = N.units[k]["n"]
                    recs[N.kind] = int(n[1] > n[0])
            if GRADED:
                for key, v in getattr(self, "_gv", {}).items():
                    p1 = self._gr_p1(key, v)
                    if p1 != 0.5:
                        recs[key] = int(p1 > 0.5)
            return recs

        def predict(self):
            if DVOTE and getattr(self, "BAYES", False):   # (D71) the colour chosen by a vote judged on choices: Bayes kept for the bits
                self._bayes_predict()
                recs = self._dv_recs()
                w = self.__dict__.setdefault("dvw", {})
                tot = sum(w.get(k, 1.0) * (1 if r == 1 else -1) for k, r in recs.items())
                self._recs = recs
                self.food = int(tot > 0) if tot != 0 else self.dl
                return
            self._bayes_predict()

        def _bayes_predict(self):
            if LMIX and getattr(self, "BAYES", False):  # (D70) logistic mixing (PAQ's context mixing; a product of experts): log-odds summed
                xs = self._lmix_inputs()                 # with learned weights, so independent weak evidence adds up
                w = self.__dict__.setdefault("lw", {})
                z = sum(w.get(k, 1.0 if k == "_def" else 0.0) * v for k, v in xs.items())
                self.p1 = 1.0 / (1.0 + math.exp(-max(min(z, 30.0), -30.0)))
                self._lxs = xs
                self.food = int(self.p1 > 0.5)
                return
            if wmaj and getattr(self, "BAYES", False):  # (2026-11-15) Bayesian mixture of the speakers and the default, each predicting a
                wd = getattr(self, "w_def", 1.0)        # probability (prequential: judged in bits before each outcome); sleepers abstain
                num, den = wd * self._pdef(1), wd
                for N in self.nets:
                    k, _ = N.says(self.place(N) - 1)
                    if k is not None:
                        w = getattr(N, "w", 1.0)
                        num += w * self._pk(N, k, 1)
                        den += w
                if GRADED:                              # (D70) graded readouts: a logistic predictor on each bank integrator's value
                    gw = self.__dict__.setdefault("grw", {})
                    self._gv = self._gr_vals()          # the values this prediction used: the next taste is scored against them, not
                    for key, v in self._gv.items():     # against values that already include that taste
                        w = gw.get(key, 1.0)
                        num += w * self._gr_p1(key, v)
                        den += w
                self.p1 = num / den
                self.food = int(self.p1 > 0.5)
                return
            if wmaj:                                    # weighted majority (Littlestone & Warmuth 1994): each stream's own weight, halved at
                wd = getattr(self, "w_def", 1.0)          # each of its wrong guesses; the default an expert too
                tot = wd * (1 if self.dl == 1 else -1)
                for N in self.nets:
                    if WM_BAR and getattr(N, "w", 1.0) <= wd:
                        continue                        # (WM_BAR) a stream votes only once its record beats the default's
                    k, _ = N.says(self.place(N) - 1)
                    if k is not None:
                        n = N.units[k]["n"]
                        if n[0] != n[1]:
                            tot += getattr(N, "w", 1.0) * (1 if n[1] > n[0] else -1)
                self.food = int(tot > 0)
                return
            if vote:                                    # no gate: every stream adds its own evidence over the default for its guess
                tot = 0.0
                for N in self.nets:
                    if N.E <= 0:
                        continue
                    k, _ = N.says(self.place(N) - 1)
                    if k is not None:
                        n = N.units[k]["n"]
                        if n[0] != n[1]:
                            tot += N.E * (1 if n[1] > n[0] else -1)
                self.food = self.dl if abs(tot) < self.bar else int(tot > 0)
                return
            if self.best is None:
                self.food = self.dl
                return
            N = self.best
            k, _ = N.says(self.place(N) - 1)
            self.food = self.dl if k is None else int(N.units[k]["n"][1] > N.units[k]["n"][0])

        def taste(self, value, at):
            if avgs and allavg:
                self._bump("good" if value > 0 else "bad")
            v = True if novouch else self.vouched()         # novouch (plan B2): learn from every taste, what was eaten the eye that pulsed last
            eaten = int(self.last[1] > self.last[0]) if novouch else self.food if v else int(self.last[1] > self.last[0])
            if lbank:                                   # the bank: this taste's events (good or bad, a meal of this colour), written after learning
                self._lb("good" if value > 0 else "bad")
                self._lb(f"c{eaten}")
                if LB_JOINT:
                    self._lb(f"c{eaten}{'g' if value > 0 else 'b'}")
                if LB_LETTER:                           # (D70) the brain's own teaching signal as an event: +1 when a taste reveals letter 1
                    self._lb("ld", 1.0 if (eaten if value > 0 else 1 - eaten) == 1 else -1.0)   # as food, -1 for letter 0
                self._lbpend = True
            if avgs and allavg and ACOUNT:              # (2026-11-15) a leaky count of meals of each colour; every average's count written
                self._pend = eaten                      # just after this taste is learned from (next step), fresh for the next guess
            letter = eaten if value > 0 else 1 - eaten
            if v:
                dhit = self.dl == letter
                bs, best = 0, None
                spoke = []
                for N in self.nets:
                    i = self.place(N) - 1
                    k, f = N.says(i)
                    b = None if k is None else int(N.units[k]["n"][1] > N.units[k]["n"][0])
                    hit = (b == letter) if b is not None else dhit
                    N.E = min(self.Emax, max(0.0, N.E + (1.0 if hit > dhit else -1.0 if hit < dhit else 0.0)))
                    if wmaj and b is not None:
                        spoke.append((N, hit) if not getattr(self, "BAYES", False) else (N, hit, self._pk(N, k, letter)))
                    if wmaj and b is not None and not hit and not (WM_SPEC or wmaj == "spec"):
                        N.w = getattr(N, "w", 1.0) * WM_BETA
                    if b is not None:
                        N.guessed(hit, self.t)
                        if hit:
                            N.agree += 1
                            N.credit(k, self.t)
                            N.own_credit(k, self.t)
                            if N.economy:
                                N.pay(k, 1.0)
                        else:
                            N.dis += 1
                    sc = N.agree - 4 * N.dis
                    if N.E >= self.bar and (best is None or sc > bs):
                        bs, best = sc, N
                    N.learn(i, letter, self.t, k, f)
                self.best = best
                if LMIX and getattr(self, "BAYES", False) and getattr(self, "_lxs", None) is not None:
                    y = float(letter)                   # each weight nudged by its own input's share of the error (gradient of the log loss)
                    err = y - self.p1
                    w = self.__dict__.setdefault("lw", {})
                    for kk, v in self._lxs.items():
                        w[kk] = w.get(kk, 1.0 if kk == "_def" else 0.0) + LMIX_ETA * err * v
                    self.lbits = getattr(self, "lbits", 0.0) - math.log2(max(self.p1 if letter == 1 else 1 - self.p1, 1e-12))
                if DVOTE and getattr(self, "BAYES", False) and getattr(self, "_recs", None):
                    w = self.__dict__.setdefault("dvw", {})   # specialists judged on choices: the speakers' weights times DV_BETA when
                    recs = self._recs                         # wrong, their total kept, then a fixed share among them
                    W0 = sum(w.get(k_, 1.0) for k_ in recs)
                    for k_, r_ in recs.items():
                        w[k_] = w.get(k_, 1.0) * (1.0 if r_ == letter else DV_BETA)
                    W1 = sum(w[k_] for k_ in recs)
                    even = 0.01 * W0 / len(recs)
                    for k_ in recs:
                        w[k_] = 0.99 * w[k_] * W0 / W1 + even
                    top = max(w.values())
                    if top < 1e-6 or top > 1e6:
                        for k_ in w:
                            w[k_] /= top
                if wmaj and getattr(self, "BAYES", False):   # Bayes over the speakers: each weight times its probability for what happened, over
                    pd = self._pdef(letter)                     # the speakers' mixture (their total kept: sleeping experts); bits counted
                    gq = {}
                    if GRADED:
                        gw = self.__dict__.setdefault("grw", {})
                        for key, v in getattr(self, "_gv", {}).items():
                            p1 = self._gr_p1(key, v)
                            gq[key] = (p1 if letter == 1 else 1.0 - p1, v, p1)
                    W0 = getattr(self, "w_def", 1.0) + sum(getattr(N, "w", 1.0) for N, _, _ in spoke) + sum(gw.get(k_, 1.0) for k_ in gq) if GRADED else \
                        getattr(self, "w_def", 1.0) + sum(getattr(N, "w", 1.0) for N, _, _ in spoke)
                    pm = (getattr(self, "w_def", 1.0) * pd + sum(getattr(N, "w", 1.0) * q for N, _, q in spoke)
                          + (sum(gw.get(k_, 1.0) * g[0] for k_, g in gq.items()) if GRADED else 0.0)) / W0
                    self.pbits = getattr(self, "pbits", 0.0) - math.log2(max(pm, 1e-12))   # the brain's prequential code length
                    self.ntaste = getattr(self, "ntaste", 0) + 1
                    self.w_def = getattr(self, "w_def", 1.0) * (pd / pm) ** BT
                    for N, _, q in spoke:
                        N.w = getattr(N, "w", 1.0) * (q / pm) ** BT
                        N.saved = getattr(N, "saved", 0.0) + math.log2(q / pd)   # bits this stream saved over the default when it spoke
                    if GRADED:
                        gp = self.__dict__.setdefault("gr", {})
                        for k_, (q, v, p1) in gq.items():
                            gw[k_] = gw.get(k_, 1.0) * (q / pm) ** BT
                            a, c = gp.get(k_, (0.0, 0.0))   # the readout's two numbers moved down the gradient of its own log loss
                            e = float(letter) - p1
                            gp[k_] = (a + GR_ETA * e * v / (1.0 + abs(v)), c + GR_ETA * e)
                    sh = getattr(self, "SHARE", WM_SHARE)
                    if sh and spoke:
                        k = len(spoke) + 1
                        even = sh * W0 / k
                        self.w_def = (1.0 - sh) * self.w_def + even
                        for N, _, _ in spoke:
                            N.w = (1.0 - sh) * N.w + even
                        if GRADED and gq:               # (the graded readouts share too; the even share recomputed over all)
                            for k_ in gq:
                                gw[k_] = (1.0 - sh) * gw.get(k_, 1.0) + even
                    h, n = getattr(self, "dkt", (0, 0))
                    self.dkt = (h + int(letter == self.dl), n + 1)
                elif wmaj and (WM_SPEC or wmaj == "spec"):   # specialists (Freund, Schapire, Singer & Warmuth 1997): only those that spoke are updated,
                    W0 = getattr(self, "w_def", 1.0) + sum(getattr(N, "w", 1.0) for N, _ in spoke)   # their total weight kept the same
                    self.w_def = getattr(self, "w_def", 1.0) * (1.0 if self.dl == letter else WM_BETA)
                    for N, hit in spoke:
                        N.w = getattr(N, "w", 1.0) * (1.0 if hit else WM_BETA)
                    W1 = self.w_def + sum(N.w for N, _ in spoke)
                    if W1 > 0:
                        self.w_def *= W0 / W1
                        for N, _ in spoke:
                            N.w *= W0 / W1
                    sh = getattr(self, "SHARE", WM_SHARE)
                    if sh and spoke:              # fixed share among those that spoke (Herbster & Warmuth 1998): a share of their weight
                        k = len(spoke) + 1              # returned evenly, so a stream that becomes right can recover (tracking a changing best)
                        even = sh * W0 / k
                        self.w_def = (1.0 - sh) * self.w_def + even
                        for N, _ in spoke:
                            N.w = (1.0 - sh) * N.w + even
                elif wmaj and self.dl != letter:
                    self.w_def = getattr(self, "w_def", 1.0) * WM_BETA
                if wmaj:                                # keep the weights in range (a common rescaling, no information lost)
                    top = max([getattr(N, "w", 1.0) for N in self.nets] + [getattr(self, "w_def", 1.0)])
                    if top < 1e-6:
                        for N in self.nets:
                            N.w = getattr(N, "w", 1.0) / top
                        self.w_def = getattr(self, "w_def", 1.0) / top
                if value > 0:
                    self.dt = max(-1, self.dt - 1) if self.dl == letter else self.dt
                if self.dl != letter:
                    self.dt += 1
                    if self.dt >= 1:
                        self.dl, self.dt = letter, 0
            if senses:
                self.lastsym = 2 * eaten + (value > 0)
                for c in self.clk:
                    c["sym"] = self.lastsym
                    if reset == "change":                   # D39's trigger: the food colour this taste reveals differs from the last revealed
                        pass
                    elif reset and value < 0:               # a surprise restarts every clock: its next beat one period from now
                        c["next"] = self.t + c["T"]
                if reset == "change":
                    letter = eaten if value > 0 else 1 - eaten
                    if getattr(self, "lastletter", letter) != letter:
                        tl = getattr(self, "lastchange", None)
                        for c in self.clk:
                            if LOCK and tl is not None:     # period locking: nudge T toward the interval since the last change over its
                                d = self.t - tl             # nearest whole number of beats (the noticing delay cancels between changes)
                                m = max(1, round(d / c["T"]))
                                if abs(d / (m * c["T"]) - 1.0) < LOCK_WIN:
                                    c["T"] += LOCK * (d / m - c["T"])
                            c["next"] = self.t + c["T"] / 2.0       # the change lies between tastes: a slot boundary half a period back
                        if PHASES == "2" and hasattr(self, "posc"):   # each oscillator locks to the revealed changes: its slot length
                            for o in self.posc:         # nudged toward the interval since the last change over its nearest whole number of
                                if PLL_RES and o.get("n", 0) >= 10:   # a resonator (T20): the phase never moved; a forgetting circular mean of
                                    o["th"] += (self.t - o["tl"]) / o["S"]   # where in its slot each change falls; its slide per slot is the rate's
                                    o["tl"] = self.t                         # error, and only the rate is corrected
                                    a = 2.0 * math.pi * (o["th"] % 1.0)
                                    o["rc"] = RES_L * o.get("rc", 0.0) + math.cos(a)
                                    o["rs"] = RES_L * o.get("rs", 0.0) + math.sin(a)
                                    o["rn"] = RES_L * o.get("rn", 0.0) + 1.0
                                    o["nc"] = o.get("nc", 0) + 1
                                    if o["nc"] % RES_EVERY == 0:
                                        mu = math.atan2(o["rs"], o["rc"]) / (2.0 * math.pi)
                                        R_ = math.hypot(o["rc"], o["rs"]) / o["rn"]
                                        if "mu" in o and R_ > 0.3:
                                            dmu = (mu - o["mu"] + 0.5) % 1.0 - 0.5
                                            dk = o["th"] - o["thm"]
                                            if dk > 0:
                                                o["S"] *= 1.0 + RES_G * dmu / dk
                                        o["mu"], o["thm"] = mu, o["th"]
                                    continue
                                if PLL_SPAN and o.get("n", 0) >= 10:   # the span since an anchor over its whole number of slots (the delays
                                    o.setdefault("ta", self.t)          # telescope: error falls as 1 / span); first the intervals' average
                                    D = self.t - o["ta"]                # sets the slot, then the anchor is the change that reached ten
                                    m = round(D / o["S"])
                                    if m >= 1 and abs(D / o["S"] - m) < 0.4:
                                        o["S"] = D / m
                                elif tl is not None:    # slots (the noticing delays cancel), its phase nudged toward a slot's start
                                    d = self.t - tl
                                    m = max(1, round(d / o["S"]))
                                    if abs(d / (m * o["S"]) - 1.0) < PLL_WIN:
                                        if PLL_AVG:     # an average of the accepted intervals (step 1/(n+2), floor PLL_FLOOR): keeps the evidence
                                            o["n"] = o.get("n", 0) + 1
                                            o["S"] += max(1.0 / (o["n"] + 2), PLL_FLOOR) * (d / m - o["S"])
                                        else:
                                            o["S"] += PLL_S * (d / m - o["S"])
                                o["th"] += (self.t - o["tl"]) / o["S"]
                                o["tl"] = self.t
                                e = o["th"] - round(o["th"])
                                o["th"] -= (PLL_P2 if PLL_AVG else PLL_P) * e
                        if rhythm:
                            self._rt_change(self.t)
                        self.lastchange = self.t
                        for c in self.clk:
                            c["since"] = 0
                    self.lastletter = letter
                for N in self.nets:
                    clk, _, rec = N.kind.partition(":")
                    if clk in TICKS and TICKS[clk](value > 0, eaten):
                        c = self.cnt[N.kind]
                        N.write(c, (eaten if rec == "colour" else int(value > 0)) if rec else 2 * eaten + (value > 0))
                        N.tidy(c, self.t)
                        self.cnt[N.kind] = c + 1
                for N in self.nets:
                    if N.kind == "joint":
                        N.tidy(0, self.t)
                self.na += 1
                if value > 0:
                    self.g += 1
                self.predict()
                return
            if one:
                if lines:
                    self.nets[0].write(self.na, (0 if value > 0 else 1, 2 + eaten))
                else:
                    self.nets[0].write(self.na, 2 * eaten + (value > 0))
                self.nets[0].tidy(self.na, self.t)
                self.na += 1
                if value > 0:
                    self.g += 1
                self.predict()
                return
            gi, ei = int(self.g), self.na
            self.nets[0].write(gi, letter, keep=not v)
            self.nets[1].write(ei, eaten)
            self.nets[1].tidy(ei, self.t)
            self.na += 1
            if value > 0:
                self.g += 1
                self.nets[0].tidy(gi, self.t)
            self.predict()

        def alive(self):
            return [sum(1 for x in N.units.values() if x.get("sym") is None) for N in self.nets]

        def _bump(self, line):
            for c in self.aclk:
                if c["e"] == line:                      # a leaky average of the line's rate (events a second), decayed lazily
                    c["r"] = c["r"] * math.exp(-(self.t - c["tr"]) / c["T"]) + 1.0 / c["T"]
                    c["tr"] = self.t

        def stimulate(self, sensor, at):
            if lbank and sensor in (0, 1):
                self._lb(f"e{sensor}")
            if avgs and sensor in (0, 1):
                self._bump(sensor)
            if eyes and sensor in (0, 1):
                for c in self.eclk:
                    if c["e"] == sensor:
                        c["n"] += 1
            return super().stimulate(sensor, at)

        def step(self):
            if (clocks or eyes or avgs or lbank or rhythm) and self.byk is None:
                self.byk = {N.kind: N for N in self.nets}
            if lbank and getattr(self, "_lbpend", False) and self.byk is not None:
                self._lbpend = False
                self._lb_write()
                self.predict()
            elif lbank and LB_LIVE and self.byk is not None and self.t - getattr(self, "_lbt", -1.0) >= 0.1:
                self._lbt = self.t                      # send-on-delta: every .1 s, a stream whose decaying count has moved writes it
                if self._lb_write(changed_only=True):
                    self.predict()
            if avgs and ACOUNT and getattr(self, "_pend", None) is not None and self.byk is not None:
                self._bump(f"c{self._pend}")
                self._pend = None
                for c in self.aclk:
                    r = c["r"] * math.exp(-(self.t - c["tr"]) / c["T"])
                    N = self.byk[f"avg{c['e']}c{c['j']}"]
                    k = self.cnt[N.kind]
                    N.write(k, min(int(round(r * c["T"])), 4))
                    N.tidy(k, self.t)
                    self.cnt[N.kind] = k + 1
                self.predict()
            if avgs and not ACOUNT:
                for c in self.aclk:
                    if self.t >= c["next"]:             # a beat: the average against the thirds of its own history
                        r = c["r"] * math.exp(-(self.t - c["tr"]) / c["T"])
                        h = c["hist"]
                        if ACOUNT:                      # (2026-11-15) the average read as a whole count of recent events (rate x time
                            sym = min(int(round(r * c["T"])), 4)   # constant: 0 to 4 or more), not against the thirds of its own history
                        elif len(h) >= 3:
                            lo, hi = np.percentile(h, [33.3, 66.7])
                            sym = 0 if r < lo else 2 if r > hi else 1
                        else:
                            sym = 1
                        h.append(r)
                        del h[:-300]
                        N = self.byk[f"avg{c['e']}c{c['j']}"]
                        k = self.cnt[N.kind]
                        N.write(k, sym)
                        N.tidy(k, self.t)
                        self.cnt[N.kind] = k + 1
                        c["next"] += c["T"]
                        self.predict()
            if eyes:
                for c in self.eclk:
                    if self.t >= c["next"]:             # a beat: how many pulses this eye gave since the last
                        N = self.byk[f"eye{c['e']}c{c['j']}"]
                        k = self.cnt[N.kind]
                        sym = 0 if c["n"] == 0 else 1 if c["n"] <= 2 else 2 if c["n"] <= 8 else 3
                        N.write(k, sym)
                        N.tidy(k, self.t)
                        self.cnt[N.kind] = k + 1
                        c["n"] = 0
                        c["next"] += c["T"]
                        self.predict()
            if PHASES == "1" and clocks:                # (diagnosis) a phase: a clock of a fifth of clock 0's period, never re-phased or
                if not hasattr(self, "pnext"):          # drifting, its beats counted modulo 5m: the place in a cycle of m slots, 5 bins each
                    self.pnext, self.pk = self.t, 0
                if self.t >= self.pnext:
                    self.pk += 1
                    self.pnext += self.clk[0]["T"] / 5.0
                    for m in range(2, PH_MAX + 1):
                        N = self.byk[f"ph{m}"]
                        k = self.cnt[N.kind]
                        N.write(k, self.pk % (5 * m))
                        N.tidy(k, self.t)
                        self.cnt[N.kind] = k + 1
                    self.predict()
            if PHASES == "2" and clocks:                # phase oscillators (2026-11-15): never jumped; each a slot length S (drawn, drifting) and a
                if not hasattr(self, "posc"):           # phase th in slots; five bins a slot, each bin's beat counted modulo 5m (m = 2 to 8)
                    orng = np.random.default_rng([int(self.seed_), 85])
                    self.posc = [dict(S=float(np.exp(orng.uniform(np.log(3.0), np.log(30.0)))), th=float(orng.uniform(0, 1)), k=0,
                                      tl=self.t) for _ in range(PHN)]
                    self.orng = orng
                if POSC_TOLD:                           # (diagnosis) oscillator 0 told the slot length (via TOLDT's clock 0), phase still locked
                    self.posc[0]["S"] = self.clk[0]["T"]
                for i, o in enumerate(self.posc):
                    o["th"] += (self.t - o["tl"]) / o["S"]
                    o["tl"] = self.t
                    kb = int(math.floor(o["th"] * 5.0))
                    if (kb > o["k"]) if PMONO else (kb != o["k"]):   # PMONO: a bin written only when the phase moves on past it
                        if kb // 5 != o["k"] // 5:      # a slot passed: the oscillator drifts (a brain's clocks drift)
                            o["S"] *= float(np.exp(self.orng.normal(0.0, PDRIFT)))
                        o["k"] = kb
                        for m in range(2, 9):
                            N = self.byk[f"pq{i}n{m}"]
                            k = self.cnt[N.kind]
                            N.write(k, kb % (5 * m))
                            N.tidy(k, self.t)
                            self.cnt[N.kind] = k + 1
                        self.predict()
            if clocks:
                for j, c in enumerate(self.clk):
                    if self.t >= c["next"]:                 # a beat: write what was last tasted since the last beat (4: nothing)
                        kind = f"clock{j}"
                        N = self.byk[kind]
                        k = self.cnt[kind]
                        N.write(k, getattr(self, "lastletter", 0) if reset == "change" else c.get("sym", 4))   # change mode: the food colour last revealed, held
                        N.tidy(k, self.t)
                        self.cnt[kind] = k + 1
                        if not NODRIFT:                     # (NODRIFT: a diagnosis only, never a design: AGENTS, a brain's clocks drift)
                            c["T"] *= float(np.exp(self.crng.normal(0.0, 0.01)))   # drift
                        c["next"] += c["T"]
                        c["sym"] = 4                            # nothing tasted since this clock's beat, until a taste
                        if j < since:                       # beats since the food colour was last seen to change (2026-11-14): a count the
                            c["since"] = c.get("since", 0) + 1   # world's changes reset, recorded up to 8 (9 symbols)
                            Ns = self.byk[f"since{j}"]
                            ks = self.cnt[Ns.kind]
                            Ns.write(ks, min(c["since"], 8))
                            Ns.tidy(ks, self.t)
                            self.cnt[Ns.kind] = ks + 1
                        if j < counters:                    # counters (2026-11-14): this clock's beats counted modulo 2 to 8, each a stream
                            if CPHASE:                      # (diagnosis) the count read from time since an anchor, so re-phasing can't slip it
                                c.setdefault("anchor", self.t)
                                c["beats"] = int(round((self.t - c["anchor"]) / c["T"]))
                            else:
                                c["beats"] = c.get("beats", 0) + 1
                            for m in range(2, 9):
                                Nc = self.byk[f"cnt{j}n{m}"]
                                kc = self.cnt[Nc.kind]
                                Nc.write(kc, c["beats"] % m)
                                Nc.tidy(kc, self.t)
                                self.cnt[Nc.kind] = kc + 1
                        self.predict()
            if rhythm and self.byk is not None:
                self._rt_step()
            out = super().step()
            if lbank and out:
                for m in out:
                    if m in (0, 1):
                        self._lb(f"m{m}")
            if avgs and allavg and out:
                for m in out:
                    if m in (0, 1):
                        self._bump(f"m{m}")
            return out

    return GrowNet


class Net2(Net):
    """Separate sense lines and clocks (stage 5): the senses are four lines, good taste, bad taste, ate red, ate blue (two fire at each
    taste). A block keeps time by a clock: every taste, or the firings of one sense line; its span counts that clock's ticks, and its
    output holds from one tick to the next. A block made on a sense draws its clock at random (every taste or one of the senses); a
    block made on a block keeps that block's clock. So a block can count good meals, say, by itself, with nothing told."""
    LINES = 4
    CLOCKS = "earned"

    def __init__(self, kind, P, rng, **kw):
        super().__init__(kind, P, rng, alphabet=self.LINES, **kw)
        for x in self.units.values():
            x["clock"] = None
        self.ticks = {c: [] for c in [None] + list(range(self.LINES))}
        self.clock_n = {}

    def _add(self, u, v, span, t, sym=None, clock=None):
        k = super()._add(u, v, span, t, sym)
        self.units[k]["clock"] = clock
        return k

    def write(self, i, syms, keep=False):
        self.hist[i] = set(syms)
        self.hist.pop(i - HIST, None)
        self.ticks[None].append(i)
        for s in syms:
            self.ticks[s].append(i)
        for c in self.ticks:
            del self.ticks[c][:-HIST]

    def draw_clock(self, i):
        """A new root's clock. CLOCKS="random": any, evenly. CLOCKS="earned": clocks compete by how well the colour eaten at their
        last tick has foretold the next food colour (each clock's own small readout, kept in clock_n), drawn in proportion to the
        excess of that record over chance (a clock whose ticks always see one colour foretells nothing)."""
        cs = [None] + list(range(self.LINES))
        if self.CLOCKS == "random":
            return cs[int(self.rng.integers(len(cs)))]
        w = []
        for c in cs:
            n = self.clock_n.get(c, {})
            right = sum(max(v) for v in n.values())
            tot = sum(sum(v) for v in n.values())
            w.append(max(0.0, (right + 1) / (tot + 2) - 0.5) + 1e-3)
        w = np.array(w) / sum(w)
        return cs[int(self.rng.choice(len(cs), p=w))]

    def clock_learn(self, i, letter):
        for c in [None] + list(range(self.LINES)):
            tick, _ = self._last(c, i)
            if tick is None:
                continue
            col = 2 if 2 in self.hist.get(tick, ()) else 3
            v = self.clock_n.setdefault(c, {}).setdefault(col, [0, 0])
            v[letter] += 1

    def _last(self, c, i):
        """The last tick of clock c at or before step i, and its place in the clock's list."""
        import bisect
        L = self.ticks[c]
        j = bisect.bisect_right(L, i) - 1
        return (L[j], j) if j >= 0 else (None, None)

    def fires(self, k, i, memo):
        key = (k, i)
        if key in memo:
            return memo[key]
        x = self.units[k]
        if x["sym"] is not None:
            r = x["sym"] in self.hist.get(i, ())
        else:
            L = self.ticks[x["clock"]]
            tick, j = self._last(x["clock"], i)
            r = False
            if tick == i:
                back = j - x.get("gap", self.units[x["v"]]["span"])
                r = back >= 0 and self.fires(x["v"], i, memo) and self.active(x["u"], L[back], memo)
        memo[key] = r
        return r

    def active(self, k, i, memo):
        x = self.units[k]
        if x["sym"] is not None or x["clock"] is None:
            return self.fires(k, i, memo)
        tick, _ = self._last(x["clock"], i)
        return tick is not None and self.fires(k, tick, memo)

    def firing(self, i):
        memo = {}
        return [k for k in self.units if self.active(k, i, memo)], memo

    def says(self, i):
        """Spans on different clocks can't be compared, so the unit that speaks is the surest: the highest chance of being right by
        its own record ((agreeing + 1) / (all + 2)), the longer span among equals."""
        f, _ = self.firing(i)
        best, key = None, None
        for k in f:
            n = self.units[k]["n"]
            if n[0] != n[1]:
                kk = ((max(n) + 1) / (n[0] + n[1] + 2), self.units[k]["span"])
                if key is None or kk > key:
                    best, key = k, kk
        return best, f

    def learn(self, i, letter, t, speaker, firing):
        for k in firing:
            self.units[k]["n"][letter] += 1
        self.clock_learn(i, letter)
        if not firing:
            return
        # novelty beneath the most specific contradicted unit active (the longest span; among equals one at random): the surest
        # speaks, but growth is where the detail is
        con = [k for k in firing if min(self.units[k]["n"]) >= 1]
        if not con:
            return
        top = max(self.units[k]["span"] for k in con)
        deep = [k for k in con if self.units[k]["span"] == top]
        deep = deep[int(self.rng.integers(len(deep)))]
        d = self.units[deep]
        rich = not self.economy or d["sym"] is not None or d["cash"] >= GRANT
        if not (rich and min(d["n"]) >= 1 and len(self.units) < self.P):
            return
        clock = d["clock"] if d["sym"] is None else self.draw_clock(i)
        tick, j = self._last(clock, i)
        if tick is None:
            return
        if d["sym"] is not None and tick != i:
            return                                      # a sense joins a clock only at one of its ticks
        span = d["span"]
        memo = {}
        # a partner active span ticks before (a sequence: u, then deep) or at the same tick (a coincidence: u and deep together)
        cands = [(k, 0) for k in self.units if k != deep and self.active(k, self.ticks[clock][j], memo)]
        if j - span >= 0:
            cands += [(k, span) for k in self.units if self.active(k, self.ticks[clock][j - span], memo)]
        if not cands:
            return
        u, gap = cands[int(self.rng.integers(len(cands)))]
        nspan = self.units[u]["span"] + span if gap else max(self.units[u]["span"], span)
        if nspan > HIST // 4:
            return
        k = self._add(u, deep, nspan, t, clock=clock)
        self.units[k]["gap"] = gap
        self.units[k]["n"][letter] = 1
        self.births += 1
        if self.economy:
            if d["sym"] is None:
                d["cash"] -= GRANT
            self.units[k]["cash"] = GRANT


class NetC(Net):
    """No symmetry told (plan B1): a unit's readout is a table of what each choice led to, m[eye] = [bad, good], not a tally of the food
    colour; it prefers the eye with the better record ((good + 1) / (all + 2)) and leans when the two differ. A taste teaches only about
    the eye eaten. Contradicted: some eye has led both to good and to bad."""

    def _add(self, u, v, span, t, sym=None):
        k = super()._add(u, v, span, t, sym)
        self.units[k]["m"] = [[0, 0], [0, 0]]
        return k

    SYM = False                                     # NetCS: each unit may learn that the two eyes are opposites

    @classmethod
    def choice(cls, m):
        if cls.SYM == "always" or (cls.SYM and cls.opposite(m)):
            s, f = m[0][1] + m[1][0], m[0][0] + m[1][1]   # pooled: eye 0 good and eye 1 bad are the same news
            p0 = (s + 1) / (s + f + 2)
            p = [p0, 1.0 - p0]
        else:
            p = [(m[e][1] + 1) / (m[e][0] + m[e][1] + 2) for e in (0, 1)]
        return None if p[0] == p[1] else int(p[1] > p[0]), abs(p[1] - p[0])

    @staticmethod
    def opposite(m):
        """MacKay's Occam factor on the unit's own record: the evidence that the two eyes are opposites (one chance, eye 0 good
        meaning eye 1 bad) against independent (a chance each), uniform priors, even odds."""
        from math import lgamma

        def lb(a, b):
            return lgamma(a + 1) + lgamma(b + 1) - lgamma(a + b + 2)
        ind = lb(m[0][1], m[0][0]) + lb(m[1][1], m[1][0])
        opp = lb(m[0][1] + m[1][0], m[0][0] + m[1][1])
        return opp > ind

    def says(self, i):
        f, _ = self.firing(i)
        best, key = None, None
        for k in f:
            c, gap = self.choice(self.units[k]["m"])
            if c is not None:
                kk = (self.units[k]["span"], gap)
                if key is None or kk > key:
                    best, key = k, kk
        return best, f

    def learn(self, i, obs, t, speaker, firing):
        eye, good = obs
        for k in firing:
            self.units[k]["m"][eye][int(good)] += 1
        deep = max(firing, key=lambda k: self.units[k]["span"], default=None)
        if deep is None:
            return
        d = self.units[deep]
        rich = not self.economy or d["sym"] is not None or d["cash"] >= GRANT
        if getattr(self, "ondemand", False) and rich and min(d["m"][eye]) >= 1 and len(self.units) >= self.P:
            leaves = [k for k, x in self.units.items() if x["sym"] is None and not x["kids"] and k != deep]
            if leaves:
                pick = [leaves[int(self.rng.integers(len(leaves)))] for _ in range(4)]
                self._remove(min(pick, key=lambda k: self._trace(self.units[k], t)))
                self.fades += 1
        if not (rich and min(d["m"][eye]) >= 1 and len(self.units) < self.P):
            return
        span = d["span"]
        before, _ = self.firing(i - span)
        if not before:
            return
        u = before[int(self.rng.integers(len(before)))]
        if self.units[u]["span"] + span > HIST // 2:
            return
        k = self._add(u, deep, self.units[u]["span"] + span, t)
        self.units[k]["m"][eye][int(good)] = 1
        self.births += 1
        if self.economy:
            if d["sym"] is None:
                d["cash"] -= GRANT
            self.units[k]["cash"] = GRANT


class NetCS(NetC):
    SYM = True


class NetCT(NetC):
    SYM = "always"                                  # told: B1's machinery with the symmetry given (an ablation)


def netc_cls(prune=True, economy=False, sym=False, told=False, agree=False, novouch=False, action=False):
    """action (plan B2): what a taste is about is the eye the brain was following (its own action), never which eye pulsed last; every
    taste counts (no vouching); recycling on demand and strict copies, the overnight best."""
    """Plan B1: a stream for every sense line (as net_cls(senses=True)), with NetC's readouts: no symmetry told. The default (keep the
    eye; two bad tastes on it to change) and the gate are judged only on tastes of the eye they would have chosen."""
    G = net_cls(prune=prune, economy=economy, senses=True)
    import rivals as RV

    class GrowNetC(G):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            P = max(3, int(p["P"]) // len(self.KINDS))
            rng = np.random.default_rng([int(seed), 77])
            self.NC = NetCT if told else NetCS if sym else NetC
            self.nets = [self.NC(k, P, rng, prune, prune, prune, 0.0, economy, 4) for k in self.KINDS]
            if action:
                for N in self.nets:
                    N.fade, N.ondemand, N.strict = False, True, True
            self.trng = np.random.default_rng([int(seed), 78])     # the brain's own noise, for choosing who steers

        def predict(self):
            """Who steers: the default and each stream whose speaker leans, chosen by sampling each one's record of good and bad meals
            when it was followed (Thompson sampling): an untried source is sometimes tried, which is how it can prove itself without
            being told that one colour's poison means the other's food."""
            rec = getattr(self, "rec", None)
            if rec is None:
                rec = self.rec = {"default": [0, 0]}
            opts = [("default", self.dl)]
            for N in self.nets:
                k, _ = N.says(self.place(N) - 1)
                if k is not None:
                    opts.append((N.kind, self.NC.choice(N.units[k]["m"])[0]))
            draws = [self.trng.beta(rec.get(src, [0, 0])[1] + 1, rec.get(src, [0, 0])[0] + 1) for src, _ in opts]
            src, eye = opts[int(np.argmax(draws))]
            self.src, self.food, self.opts = src, eye, opts
            self.best = next((N for N in self.nets if N.kind == src), None)

        def taste(self, value, at):
            v = True if (novouch or action) else self.vouched()
            eaten = self.food if action else int(self.last[1] > self.last[0]) if novouch else self.food if v else int(self.last[1] > self.last[0])
            good = value > 0
            if v and getattr(self, "src", None) is not None:
                if agree:                               # every source whose choice was the eye eaten learns from this taste
                    for src in {s_ for s_, e in self.opts if e == eaten}:
                        self.rec.setdefault(src, [0, 0])[int(good)] += 1
                else:
                    self.rec.setdefault(self.src, [0, 0])[int(good)] += 1
            if v:
                dhit = good if eaten == self.dl else None
                bs, best = 0, None
                for N in self.nets:
                    i = self.place(N) - 1
                    k, f = N.says(i)
                    b = None if k is None else self.NC.choice(N.units[k]["m"])[0]
                    hit = (good if eaten == b else None) if b is not None else dhit
                    if hit is not None and dhit is not None:
                        N.E = min(self.Emax, max(0.0, N.E + (1.0 if hit > dhit else -1.0 if hit < dhit else 0.0)))
                    if b is not None and eaten == b:
                        if good:
                            N.agree += 1
                            N.credit(k, self.t)
                            N.own_credit(k, self.t)
                            if N.economy:
                                N.pay(k, 1.0)
                        else:
                            N.dis += 1
                    sc = N.agree - 4 * N.dis
                    if N.E >= self.bar and (best is None or sc > bs):
                        bs, best = sc, N
                    N.learn(i, (eaten, good), self.t, k, f)
                self.best = best
                if eaten == self.dl:
                    if good:
                        self.dt = max(-1, self.dt - 1)
                    else:
                        self.dt += 1
                        if self.dt >= 1:
                            self.dl, self.dt = 1 - self.dl, 0
            for N in self.nets:
                if N.kind in ("every",) or (N.kind == "good" and good) or (N.kind == "bad" and not good) or \
                        (N.kind == "red" and eaten == 0) or (N.kind == "blue" and eaten == 1):
                    c = self.cnt[N.kind]
                    N.write(c, 2 * eaten + int(good))
                    N.tidy(c, self.t)
                    self.cnt[N.kind] = c + 1
            self.na += 1
            if good:
                self.g += 1
            self.predict()

    return GrowNetC


class JointNet:
    """Coincidences across streams (2026-11-13; the user: crack on): units that join one unit of one stream with one of another, firing
    when both are active at the same moment (each stream's units as they stand at its latest step). One more stream for the gate: the
    same interface as Net (says, learn, credit), so it competes as any stream does. Births beneath its own contradictions, or when nothing
    of its own spoke: the deepest unit active in one stream (drawn at random) joined to the deepest active in another (drawn at random),
    co-active now. Material P; recycling on demand (the least used of four drawn at random)."""

    def __init__(self, brain, P, rng):
        self.brain, self.P, self.rng = brain, P, rng
        self.kind, self.units, self.next = "joint", {}, 0
        self.E, self.agree, self.dis, self.economy = 0.0, 0, 0, False
        self.births = self.fades = self.dups = self.starved = 0

    def _active(self):
        b, act = self.brain, {}
        for N in b.nets:
            if N is self:
                continue
            f, _ = N.firing(b.place(N) - 1)
            act[N.kind] = (N, set(f))
        return act

    def says(self, i):
        act = self._active()
        self._act = act
        f = [k for k, x in self.units.items() if x["a"] in act[x["A"]][1] and x["b"] in act[x["B"]][1]]
        best, key = None, None
        for k in f:
            n = self.units[k]["n"]
            if n[0] != n[1]:
                kk = ((max(n) + 1) / (n[0] + n[1] + 2), n[0] + n[1])
                if key is None or kk > key:
                    best, key = k, kk
        return best, f

    def credit(self, k, t, w=1.0):
        x = self.units.get(k)
        if x is not None:
            x["use"] = x["use"] * math.exp(-(t - x["tu"]) / FADE) + w
            x["tu"] = t

    def own_credit(self, k, t):
        pass

    def guessed(self, right, t):
        pass

    def learn(self, i, letter, t, speaker, firing):
        for k in firing:
            self.units[k]["n"][letter] += 1
        wrong = speaker is None or int(self.units[speaker]["n"][1] > self.units[speaker]["n"][0]) != letter
        if not wrong:
            return
        act = getattr(self, "_act", None) or self._active()
        cands = []
        for kind, (N, f) in act.items():
            deep = [k for k in f if N.units[k]["sym"] is None] or list(f)
            if deep:
                top = max(N.units[k]["span"] for k in deep)
                deep = [k for k in deep if N.units[k]["span"] == top]
                cands.append((kind, deep[int(self.rng.integers(len(deep)))]))
        if len(cands) < 2:
            return
        i1, i2 = self.rng.choice(len(cands), 2, replace=False)
        (A, a), (B, bb) = cands[int(i1)], cands[int(i2)]
        if any((x["A"], x["a"], x["B"], x["b"]) in ((A, a, B, bb), (B, bb, A, a)) for x in self.units.values()):
            return
        if len(self.units) >= self.P:
            ks = list(self.units)
            pick = [ks[int(self.rng.integers(len(ks)))] for _ in range(4)]
            gone = min(pick, key=lambda k: self.units[k]["use"] * math.exp(-(t - self.units[k]["tu"]) / FADE))
            del self.units[gone]
            self.fades += 1
        n = [0, 0]
        n[letter] = 1
        self.units[self.next] = dict(A=A, a=a, B=B, b=bb, n=n, use=0.0, tu=t, born=t)
        self.next += 1
        self.births += 1

    def tidy(self, i, t):
        """Units whose parts were recycled in their own streams go too."""
        b = self.brain
        alive = {N.kind: N.units for N in b.nets if N is not self}
        for k in [k for k, x in self.units.items() if x["a"] not in alive.get(x["A"], {}) or x["b"] not in alive.get(x["B"], {})]:
            del self.units[k]
