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
HIST = 96                                       # steps of history kept on a stream (spans beyond it can't fire)


class Net:
    def __init__(self, kind, P, rng, prune=True, fade=True, dup=True, supply=0.0, economy=False, alphabet=2):
        self.kind, self.P, self.rng, self.prune = kind, P, rng, prune
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

    def says(self, i):
        f, _ = self.firing(i)
        best, key = None, None
        for k in f:
            n = self.units[k]["n"]
            if n[0] != n[1]:
                kk = (self.units[k]["span"], abs(n[1] - n[0]) / (n[0] + n[1]))
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
            self.units[k]["n"][letter] += 1
        # birth beneath a contradiction: the deepest firing unit, if it has seen both letters
        deep = max(firing, key=lambda k: self.units[k]["span"], default=None)
        rich = deep is not None and (not self.economy or self.units[deep]["sym"] is not None or self.units[deep]["cash"] >= GRANT)
        if deep is not None and rich and min(self.units[deep]["n"]) >= 1 and len(self.units) < self.P:
            span = self.units[deep]["span"]
            before, _ = self.firing(i - span)
            if before:
                u = before[int(self.rng.integers(len(before)))]
                if self.units[u]["span"] + span <= HIST // 2:
                    k = self._add(u, deep, self.units[u]["span"] + span, t)
                    if self.supply > 0:                 # the young are protected by their parents' standing: the weaker parent's record
                        pu, pv = self.units[u], self.units[deep]
                        self.units[k]["own"] = min(pu["own"] * math.exp(-(t - pu["to"]) / FADE), pv["own"] * math.exp(-(t - pv["to"]) / FADE))
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

    def tidy(self, i, t):
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
            if j is not None and j in self.units:
                a, b = (j, k) if self._trace(self.units[j], t) >= self._trace(self.units[k], t) else (k, j)
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


def net_cls(prune=True, fade=True, dup=True, supply=0.0, economy=False, one=False, lines=False):
    """one: a single stream, every taste, its symbol the colour eaten and whether it was good (four symbols): no stream chosen by us."""
    D = L.designed_cls()
    import rivals as RV

    class GrowNet(D):
        KINDS = ("taste",) if one or lines else ("good", "eaten")

        def __init__(self, seed, p):
            super().__init__(seed, dict(p, lad="seq", size=1))
            P = max(3, int(p["P"]) // len(self.KINDS))
            rng = np.random.default_rng([int(seed), 77])
            if lines:                                   # separate sense lines with clocks (Net2)
                self.nets = [Net2("taste", P, rng, prune=prune, fade=fade, dup=dup, supply=supply, economy=economy)]
            else:
                self.nets = [Net(k, P, rng, prune, fade, dup, supply, economy, 4 if k == "taste" else 2) for k in self.KINDS]
            self.na = 0
            o = RV.occam(len(self.nets))
            self.bar, self.Emax = o["theta"], o["Emax"]
            self.best = None
            self.dl, self.dt = self.food, 0

        def place(self, N):
            return int(self.g) if N.kind == "good" else self.na

        def predict(self):
            if self.best is None:
                self.food = self.dl
                return
            N = self.best
            k, _ = N.says(self.place(N) - 1)
            self.food = self.dl if k is None else int(N.units[k]["n"][1] > N.units[k]["n"][0])

        def taste(self, value, at):
            v = self.vouched()
            eaten = self.food if v else int(self.last[1] > self.last[0])
            letter = eaten if value > 0 else 1 - eaten
            if v:
                dhit = self.dl == letter
                bs, best = 0, None
                for N in self.nets:
                    i = self.place(N) - 1
                    k, f = N.says(i)
                    b = None if k is None else int(N.units[k]["n"][1] > N.units[k]["n"][0])
                    hit = (b == letter) if b is not None else dhit
                    N.E = min(self.Emax, max(0.0, N.E + (1.0 if hit > dhit else -1.0 if hit < dhit else 0.0)))
                    if b is not None:
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
                if value > 0:
                    self.dt = max(-1, self.dt - 1) if self.dl == letter else self.dt
                if self.dl != letter:
                    self.dt += 1
                    if self.dt >= 1:
                        self.dl, self.dt = letter, 0
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
            return [sum(1 for x in N.units.values() if x["sym"] is None) for N in self.nets]

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
