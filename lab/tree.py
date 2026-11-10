"""tree.py: a context tree over registers (D40; QUESTIONS.md, Scaling). Main session, 2026-11-10. Predictions first: lab/v/tree_predictions.md.

The known local form of the ideal learner for the ladders (D39: Rissanen's context tree, PPM, context tree weighting), in its plainest
version. A register per kind of event holds the last DEPTH symbols: `good`, the letter revealed at each good-meal count; `eaten`, the
colour eaten at each taste. Over each register a tree of identical nodes: a node stands for one context (the last d symbols) and counts
which colour was food there. Raw material is nodes, P/2 to each tree, idle until recruited.
  - A trusted taste adds its letter to every node on the current context's path.
  - Recruiting: the deepest node on the path, if it has been contradicted (it has seen both letters) and material remains, recruits one
    child for the context one symbol longer. Novelty beneath a contradiction; a node never contradicted recruits nothing.
  - Predicting: the deepest node on the path whose counts lean one way says the letter.
  - Choosing: each tree's prediction is scored on every trusted taste against a default (keep the colour, two contradictions to flip),
    as the bank scores its rivals, with the Occam bar for the number of trees; the best past the bar is followed, else the default.
Told nothing of the ladder, its size or the life's length.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/teach.py [PAIRS] tree [LADDER] [Ps] [RUNGS]"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L

DEPTH = 16                                      # a register's length, in symbols


def tree_cls():
    D = L.designed_cls()
    import rivals as RV

    class Tree(D):
        KINDS = ("good", "eaten")

        def __init__(self, seed, p):
            super().__init__(seed, dict(p, lad="seq", size=1))
            self.P = int(p["P"])
            cap = max(1, self.P // len(self.KINDS))
            self.regs = [dict(kind=k, hist={}, nodes={(): [0, 0]}, cap=cap, E=0.0, agree=0, dis=0) for k in self.KINDS]
            self.na = 0                                 # tastes so far, the eaten register's place
            o = RV.occam(len(self.regs))
            self.bar, self.Emax = o["theta"], o["Emax"]
            self.best = None
            self.dl, self.dt = self.food, 0

        def place(self, R):
            return int(self.g) if R["kind"] == "good" else self.na

        def context(self, R):
            h, i, c = R["hist"], self.place(R), []
            for j in range(1, DEPTH + 1):
                s = h.get(i - j)
                if s is None:
                    break
                c.append(s)
            return tuple(c)

        def says(self, R, c):
            """The letter of the deepest node on the path whose counts lean one way; None if none does."""
            nodes, out = R["nodes"], None
            for d in range(len(c) + 1):
                n = nodes.get(c[:d])
                if n is None:
                    break
                if n[0] != n[1]:
                    out = int(n[1] > n[0])
            return out

        def learn(self, R, c, letter):
            nodes = R["nodes"]
            for d in range(len(c) + 1):
                n = nodes.get(c[:d])
                if n is None:                           # the node above was the deepest: contradicted, it recruits this one
                    up = nodes[c[:d - 1]]
                    if min(up) >= 1 and len(nodes) < R["cap"]:
                        nodes[c[:d]] = [1 - letter, letter]
                    break
                n[letter] += 1

        def write(self, R, sym, keep=False):
            h, i = R["hist"], self.place(R)
            if keep and i in h:
                return
            h[i] = sym
            h.pop(i - DEPTH - 1, None)

        def predict(self):
            if self.best is None:
                self.food = self.dl
                return
            b = self.says(self.best, self.context(self.best))
            self.food = self.dl if b is None else b

        def taste(self, value, at):
            v = self.vouched()
            eaten = self.food if v else int(self.last[1] > self.last[0])   # by its own eyes, as the designed brain
            letter = eaten if value > 0 else 1 - eaten
            if v:
                dhit = self.dl == letter
                bs, best = 0, None
                for R in self.regs:
                    c = self.context(R)
                    b = self.says(R, c)
                    hit = (b == letter) if b is not None else dhit
                    R["E"] = min(self.Emax, max(0.0, R["E"] + (1.0 if hit > dhit else -1.0 if hit < dhit else 0.0)))
                    if b is not None:
                        if hit:
                            R["agree"] += 1
                        else:
                            R["dis"] += 1
                    sc = R["agree"] - 4 * R["dis"]
                    if R["E"] >= self.bar and (best is None or sc > bs):
                        bs, best = sc, R
                    self.learn(R, c, letter)
                self.best = best
                if value > 0:
                    self.dt = max(-1, self.dt - 1) if self.dl == letter else self.dt
                if self.dl != letter:
                    self.dt += 1
                    if self.dt >= 1:
                        self.dl, self.dt = letter, 0
            self.write(self.regs[0], letter, keep=not v)   # the letter at this good-meal count: a guess never overwrites
            self.write(self.regs[1], eaten)
            self.na += 1
            if value > 0:
                self.g += 1
            self.predict()

    return Tree


def treec_cls():
    """The tree with clocks: the same nodes and rules, with a third kind of register, one per clock of D39's bank (fixed periods, the
    phase set by confirmed changes in the revealed letter and moved no further than the evidence says). A clock's register holds the
    letter of each beat, written one taste late; a beat with no taste is given what its tree would have said, else the letter before."""
    import math
    import os
    import numpy as np
    import rivals as RV
    T0 = tree_cls()
    NC, TLO, THI = int(os.environ.get("NC", 60)), 3.0, 30.0

    class TreeC(T0):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            r = self.crng = np.random.default_rng([int(seed), 13])
            cap = max(1, self.P // (2 + NC))
            for R in self.regs:
                R["cap"] = cap
            for j in range(NC):
                T = TLO * (THI / TLO) ** (j / max(NC - 1, 1)) * float(np.exp(r.normal(0, 0.03)))
                self.regs.append(dict(kind=("clock", T), hist={}, nodes={(): [0, 0]}, cap=cap, E=0.0, agree=0, dis=0, T=T, a=r.uniform(-T, 0), n=0, tl=0.0, lw=None))
            o = RV.occam(len(self.regs))
            self.bar, self.Emax = o["theta"], o["Emax"]
            self.cur, self.tcur, self.pend = None, 0.0, None

        def advance(self, R):
            c = (self.t - R["tl"]) / R["T"]
            if c > 0:
                R["a"] += self.crng.normal(0.0, 0.02 * R["T"] * math.sqrt(c))
                R["tl"] = self.t
            while self.t >= R["a"] + R["T"]:
                R["a"] += R["T"]
                R["n"] += 1

        def place(self, R):
            if isinstance(R["kind"], str):
                return super().place(R)
            self.advance(R)
            return R["n"]

        def place_at(self, R, t):
            self.advance(R)
            return R["n"] if t >= R["a"] else R["n"] - int(math.ceil((R["a"] - t) / R["T"]))

        def context_at(self, R, i):
            h, c = R["hist"], []
            for j in range(1, DEPTH + 1):
                s = h.get(i - j)
                if s is None:
                    break
                c.append(s)
            return tuple(c)

        def context(self, R):
            return self.context_at(R, self.place(R))

        def settle(self, letter):
            """The taste before this one, now that this one says what it was: learned and written, moved with the boundary, or dropped."""
            if self.pend is None:
                return
            t0, l0 = self.pend
            self.pend = None
            if self.cur is not None and l0 != self.cur:
                if letter != l0:
                    return                              # not confirmed: a misread
                lo, hi = self.tcur, t0                  # the boundary lies between these two tastes
                for R in self.regs[2:]:
                    self.advance(R)
                    a, T = R["a"], R["T"]
                    b = min((a - T, a, a + T), key=lambda x: 0.0 if lo <= x <= hi else min(abs(x - lo), abs(x - hi)))
                    if lo <= b <= hi:
                        continue
                    R["a"] = a + (lo if b < lo else hi) - b
                    if R["a"] > self.t:
                        R["a"] -= T
                        R["n"] -= 1
                    elif R["a"] + T <= self.t:
                        R["a"] += T
                        R["n"] += 1
            self.cur, self.tcur = l0, t0
            for R in self.regs[2:]:
                i, h = self.place_at(R, t0), R["hist"]
                if R["lw"] is not None:
                    for b in range(max(R["lw"] + 1, i - DEPTH), i):     # beats that passed with no taste
                        if b not in h:
                            s = self.says(R, self.context_at(R, b))
                            h[b] = h.get(b - 1, l0) if s is None else s
                self.learn(R, self.context_at(R, i), l0)
                h[i] = l0
                R["lw"] = i if R["lw"] is None else max(R["lw"], i)
                for old in [k for k in h if k < i - DEPTH - 1]:
                    del h[old]

        def taste(self, value, at):
            v = self.vouched()
            eaten = self.food if v else int(self.last[1] > self.last[0])
            letter = eaten if value > 0 else 1 - eaten
            if v:
                self.settle(letter)
                dhit = self.dl == letter
                bs, best = 0, None
                for R in self.regs:
                    c = self.context(R)
                    b = self.says(R, c)
                    hit = (b == letter) if b is not None else dhit
                    R["E"] = min(self.Emax, max(0.0, R["E"] + (1.0 if hit > dhit else -1.0 if hit < dhit else 0.0)))
                    if b is not None:
                        if hit:
                            R["agree"] += 1
                        else:
                            R["dis"] += 1
                    sc = R["agree"] - 4 * R["dis"]
                    if R["E"] >= self.bar and (best is None or sc > bs):
                        bs, best = sc, R
                    if isinstance(R["kind"], str):
                        self.learn(R, c, letter)
                self.pend = (self.t, letter)
                self.best = best
                if value > 0:
                    self.dt = max(-1, self.dt - 1) if self.dl == letter else self.dt
                if self.dl != letter:
                    self.dt += 1
                    if self.dt >= 1:
                        self.dl, self.dt = letter, 0
            self.write(self.regs[0], letter, keep=not v)
            self.write(self.regs[1], eaten)
            self.na += 1
            if value > 0:
                self.g += 1
            self.predict()

    return TreeC
