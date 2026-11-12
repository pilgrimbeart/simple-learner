"""uptake.py: G2, taking up new parts in life (PROGRAMME.md, Next; the user, 2026-11-12). The body: the original thrusters; at one
moment drawn each life (100 to 300 s) a split eye (lines 2 and 3, each a half of the corridor, wired at random) and two more thrusters a
side (a half and a quarter strength, lines 2 to 5, wired at random) come alive together. Food from birth (the plain world), 900 s lives,
efficiency in the last third.

The learner, from generic pieces only. Raw material: a candidate reflex arc from every new sensor line to every new motor line (2 x 4),
each born off; an arc that is on fires one kick on its motor line at each food pulse (the colour the brain eats) on its sensor line while
the brain is driving, at most once each REFRACT s: a new input attached to an existing behaviour, with nothing saying which line or
thruster is which. The clue: the new lines start carrying pulses. Then the arcs take turns (D54): each tried on for TRY s and off for TRY
s, judged by the joint coupling of the eyes with the original motors (D51's measure): each visit on, off, on, off for TRY s each (drift
cancels in the paired differences); visits accumulate per arc, the least visited next; an arc is decided when its mean difference
reaches SURE standard errors (boredom from certainty, D48), and one still unsure after MAXV visits stays off (MacKay's Occam factor). learn2: each arc judged by its own consequence, fast: at each food pulse on a new line while driving, one of that line's candidate
arcs fires, or none (the control), in turn; the food pulses in the next AFTER s are its outcome; an arc surely (SURE standard errors)
above the control is kept, the best per line (the forward half of coupling, per arc: does my action make my input continue?).
learn3: play first (the user: an instinct to play with its senses and body first): the base behaviour paused, still; when something is
in view on the new lines, one new motor's kick or none, in turn, then a pause for its motion to fade; a look-around beat of the scanning
motor when nothing has been in view for a while; each motor's effect is how it moves activity between the two new lines (the new sense teaching the new
actuator, no food involved); a line's candidates are the motors that surely move activity out of its half (turning towards what is
there); then taste chooses among those few, as learn2. learn3b: play's surest candidate per line wired at once, no taste. Arms
ending I: the arcs with lateral inhibition between the two new lines (an arc fires only if its line saw more food pulses than the other
in the last INHIB_W s: D24's condition, as one line suppressing the other).
Arms: base (the original parts only), told (D24's reflex with a quarter
kick, told the map, from the growth), toldarcs (the learner's arc form with the right arcs on, told: does the form suffice?), learn.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/uptake.py [PAIRS] [s103000]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import ladders as L
import newparts as NP
import stage3_random as R

import os
SECS = float(os.environ.get("UPTAKE_SECS", 900.0))      # (UPTAKE_SECS: longer lives, for an evidence-starved learner)
BIN = 0.05
TRY = 10.0
INHIB_W = 0.2                                   # s: lateral inhibition between the new lines (arms ending I): an arc fires only if
                                                # its line saw more food pulses than the other line in the last INHIB_W s
PLAY_N = 120                                     # learn3: probes per new motor (and of the control) in play
SETTLE = 0.15                                   # learn3: s for a kick's motion to fade before the next
LOOK = 0.5                                      # learn3: s with nothing in view before a look-around beat
PRE = 0.15                                       # s: the window before and after a play probe
MAXP = 400                                      # learn2: an arc still unsure after this many probes counts as no better (Occam)
AFTER = 0.3                                     # s: an arc's consequence: food pulses this long after its kick (learn2)
SURE, MAXV = 2.0, 6                             # an arc is decided when its mean on-less-off difference reaches SURE standard errors
                                                # (at least 3 visits); still unsure after MAXV visits, it stays off (Occam)
REFRACT = 0.2
OCCAM = 1.05
ARCS = [(line, motor) for line in (2, 3) for motor in (2, 3, 4, 5)]


def _init():
    R._init(0.0025, False)
    from stage2_lang import sim
    sim.WLife.extra = True
    sim.WLife.split = True
    sim.GROW = (100.0, 300.0)


def _mi(J):
    n = J.sum()
    if n == 0:
        return 0.0
    P = J / n
    px, py = P.sum(1), P.sum(0)
    nz = P > 0
    I = float((P[nz] * np.log2(P[nz] / np.outer(px, py)[nz])).sum())
    return I - ((nz.sum() - 1) - (np.count_nonzero(px) - 1) - (np.count_nonzero(py) - 1)) / (2 * n * math.log(2))


def arcs_cls(cls):
    class Arcs(cls):
        split_lines = True
        mode, on, last_c, last_fire = "learn", None, None, None

        def setup(self, mode, right=None):
            self.mode = mode
            self.last_fire = {a: -1e9 for a in ARCS}
            self.woke, self.order, self.trial = None, None, None
            self.J = [np.zeros((4, 4)), np.zeros((4, 4))]
            self.s_bin, self.a_bin, self.prev, self.next_bin = 0, 0, None, BIN
            self.pending, self.log = [], []
            self.diffs, self.decided = {a: [] for a in ARCS}, {}
            self.open, self.out, self.turn, self.choice = [], {a: [] for a in ARCS + [(2, None), (3, None)]}, {2: 0, 3: 0}, {}
            self.lines, self.play_open, self.play_turn, self.play_last, self.last_line = [], [], 0, -1e9, -1e9
            self.shift, self.effect = {m: [] for m in (2, 3, 4, 5, None)}, None
            self.inhib = mode.endswith("I")
            self.rl = []
            mode = mode[:-1] if self.inhib else mode
            self.mode = mode
            self.on = set(right or []) if mode == "toldarcs" else set()
            self.mode3b = mode == "learn3b"
            if mode == "learn3b":
                self.mode = mode = "learn3"
            self.cands = None if mode == "learn3" else {2: [2, 3, 4, 5], 3: [2, 3, 4, 5]}
            self.rng_arcs = np.random.default_rng(int(self.t * 1000) + 7)

        def stimulate(self, sensor, at):
            if sensor >= 2:
                if self.last_c == self.food:            # recent food pulses on each new line (for lateral inhibition)
                    self.rl.append((self.t + at, sensor))
                    self.rl = [x for x in self.rl if x[0] > self.t + at - INHIB_W]
                if self.woke is None:                   # the clue: a new line has started to carry pulses
                    self.woke = self.t
                    self.order = list(self.rng_arcs.permutation(len(ARCS)))
                if self.mode == "learn3":
                    self.lines.append((self.t + at, sensor))
                    self.last_line = self.t + at
                    if self.cands is None:
                        return                          # play runs in step(): still, one kick at a time
                    if self.last_c == self.food and self.t - self.last_drive < self.p["hold"]:
                        self._probe(sensor, at)
                    return
                if self.mode == "learn2" and self.last_c == self.food and self.t - self.last_drive < self.p["hold"]:
                    self._probe(sensor, at)
                    return
                if self.last_c == self.food and self.t - self.last_drive < self.p["hold"]:
                    active = set(self.on)
                    if self.trial is not None and self.trial["phase"] == "on":
                        active.add(self.trial["arc"])
                    for arc in active:
                        if arc[0] == sensor and self.t - self.last_fire[arc] >= REFRACT and self._free(sensor):
                            self.pending.append((arc[1], at))
                            self.last_fire[arc] = self.t
                return
            self.last_c = sensor
            self.s_bin |= 1 << sensor
            if self.mode in ("learn2", "learn3") and sensor == self.food:  # count food pulses for the probes still open
                for pr in self.open:
                    if self.t + at <= pr[2]:
                        pr[3] += 1
            super().stimulate(sensor, at)

        def _play(self):
            """learn3's play, still (the base behaviour paused): when something is in view on the new lines, one new motor's kick or
            none, in turn; wait for its window and for the motion to fade (SETTLE); if nothing has been in view for LOOK s, one beat
            of the scanning motor to find something. Returns the beats to fire this tick."""
            if self.play_open or self.t < self.play_last + PRE + SETTLE:
                return []
            if self.t - self.last_line < 0.1:
                opts = [2, 3, 4, 5, None]
                m = opts[self.play_turn % len(opts)]
                self.play_turn += 1
                self.play_last = self.t
                self.play_open.append([m, self.t])
                return [(m, 0.0)] if m is not None else []
            if self.t - max(self.last_line, self.play_last) > LOOK:
                self.play_last = self.t - PRE              # (a look-around beat, then settle before the next probe)
                return [(0, 0.0)]
            return []

        def _close_play(self):
            keep = []
            for m, t0 in self.play_open:
                if self.t > t0 + PRE:
                    def bal(a, b):
                        return sum(1 for t, l in self.lines if a <= t < b and l == 3) - sum(1 for t, l in self.lines if a <= t < b and l == 2)
                    self.shift[m].append(bal(t0, t0 + PRE) - bal(t0 - PRE, t0))
                else:
                    keep.append([m, t0])
            self.play_open = keep
            self.lines = [x for x in self.lines if x[0] > self.t - 2 * PRE - 0.1]
            if all(len(self.shift[m]) >= PLAY_N for m in (2, 3, 4, 5, None)):
                ctrl = np.array(self.shift[None], float)
                self.effect = {}
                for m in (2, 3, 4, 5):
                    x = np.array(self.shift[m], float)
                    se = math.sqrt(x.var(ddof=1) / len(x) + ctrl.var(ddof=1) / len(ctrl)) + 1e-9
                    self.effect[m] = ((x.mean() - ctrl.mean()) / se)
                # a line's candidates: the motors that surely move activity out of its half (towards the other line)
                self.cands = {2: [m for m in (2, 3, 4, 5) if self.effect[m] >= SURE],
                              3: [m for m in (2, 3, 4, 5) if self.effect[m] <= -SURE]}
                self.log.append((round(self.t), "play done", {m: round(v, 1) for m, v in self.effect.items()}, self.cands))
                if self.mode3b:                         # learn3b: play's surest candidate per line wired at once (its certainty is the Occam bar)
                    for line in (2, 3):
                        c = self.cands[line]
                        if c:
                            m = max(c, key=lambda mm: abs(self.effect[mm]))
                            self.choice[line] = (line, m)
                            self.on.add((line, m))
                        else:
                            self.choice[line] = None

        def _free(self, line):
            """Lateral inhibition (arms ending I): the line fires only if it saw more recent food pulses than the other new line."""
            if not self.inhib:
                return True
            n = sum(1 for _, l in self.rl if l == line)
            return n > sum(1 for _, l in self.rl if l != line)

        def _probe(self, line, at):
            """learn2: at a food pulse on a new line while driving: if its arcs are decided, fire the chosen one; else fire one of its
            candidate arcs, or none (the control), in turn, and watch the food pulses in the next AFTER s."""
            if line in self.choice:
                arc = self.choice[line]
                if arc is not None and self.t - self.last_fire[arc] >= REFRACT and self._free(line):
                    self.pending.append((arc[1], at))
                    self.last_fire[arc] = self.t
                return
            if any(pr[0] == line for pr in self.open):
                return                                   # one probe at a time on a line: each consequence belongs to one choice
            opts = [a for a in ARCS if a[0] == line and (self.cands is None or a[1] in self.cands[line])] + [(line, None)]
            if len(opts) == 1:                           # no candidate: nothing to choose
                self.choice[line] = None
                return
            arc = opts[self.turn[line] % len(opts)]
            self.turn[line] += 1
            if arc[1] is not None:
                self.pending.append((arc[1], at))
            self.open.append([line, arc, self.t + at + AFTER, 0])

        def _close_probes(self):
            keep = []
            for pr in self.open:
                if self.t > pr[2]:
                    self.out[pr[1]].append(pr[3])
                else:
                    keep.append(pr)
            self.open = keep
            for line in (2, 3):
                if line in self.choice:
                    continue
                ctrl = np.array(self.out[(line, None)], float)
                if len(ctrl) < 10:
                    continue
                best, decided = None, True
                for a in [a for a in ARCS if a[0] == line and (self.cands is None or a[1] in self.cands[line])]:
                    x = np.array(self.out[a], float)
                    if len(x) < 10:
                        decided = False
                        continue
                    se = math.sqrt(x.var(ddof=1) / len(x) + ctrl.var(ddof=1) / len(ctrl)) + 1e-9
                    z = (x.mean() - ctrl.mean()) / se
                    if abs(z) < SURE and len(x) < MAXP:
                        decided = False                  # not yet sure of this arc, and trials still to spend
                    if z >= SURE and (best is None or x.mean() > best[1]):
                        best = (a, x.mean())
                if decided:
                    self.choice[line] = best[0] if best else None      # the best sure arc, or none (Occam)
                    if best:
                        self.on.add(best[0])
                    self.log.append((round(self.t), line, best[0] if best else None))

        def _next_trial(self):
            undecided = [a for a in ARCS if a not in self.decided]
            if not undecided:
                self.trial = None
                return
            arc = min(undecided, key=lambda a: (len(self.diffs[a]), self.order.index(ARCS.index(a))))   # the least visited next
            self.trial = dict(arc=arc, phase="on", end=self.t + TRY, f=[])

        def step(self):
            out = super().step()
            beats = list(getattr(self, "beats", None) or [])
            for m, _ in beats:
                if m < 2:
                    self.a_bin |= 1 << m
            if self.pending:
                beats += self.pending
                self.pending = []
            self.beats = beats
            if self.mode == "learn2" or (self.mode == "learn3" and self.cands is not None):
                self._close_probes()
            elif self.mode == "learn3" and self.woke is not None:
                self._close_play()
                if self.cands is None:                  # still playing: the base behaviour's beats are withheld
                    beats = self._play()
                    self.beats = beats
            if self.mode == "learn" and self.woke is not None:
                if self.t >= self.next_bin:
                    if self.prev is not None:
                        self.J[0][self.prev[1], self.s_bin] += 1
                        self.J[1][self.prev[0], self.a_bin] += 1
                    self.prev, self.s_bin, self.a_bin = (self.s_bin, self.a_bin), 0, 0
                    self.next_bin += BIN
                if self.trial is None and len(self.decided) < len(ARCS):
                    self._next_trial()
                    self.J[0][:], self.J[1][:] = 0, 0
                elif self.trial is not None and self.t >= self.trial["end"]:
                    tr = self.trial
                    tr["f"].append((_mi(self.J[0]) + _mi(self.J[1])) / BIN)
                    self.J[0][:], self.J[1][:] = 0, 0
                    if len(tr["f"]) < 4:                # on, off, on, off: drift cancels in the paired differences
                        tr["phase"] = "on" if tr["phase"] == "off" else "off"
                        tr["end"] = self.t + TRY
                    else:
                        a, f = tr["arc"], tr["f"]
                        self.diffs[a].append(((f[0] - f[1]) + (f[2] - f[3])) / 2)
                        d = np.array(self.diffs[a])
                        z = d.mean() / (d.std(ddof=1) / math.sqrt(len(d)) + 1e-9) if len(d) >= 3 else 0.0
                        if len(d) >= 3 and abs(z) >= SURE:
                            self.decided[a] = z > 0
                        elif len(d) >= MAXV:
                            self.decided[a] = False      # still unsure: off (Occam)
                        if self.decided.get(a):
                            self.on.add(a)
                        self.log.append((self.t, a, round(float(d.mean()), 2), round(float(z), 2), self.decided.get(a)))
                        self.trial = None
            return [m for m, _ in beats]
    return Arcs


def make(arm, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    if arm == "told":
        return NP.make("plain", "splitQ", seed, first)
    q = T.numbers(seed, {"sync": 1})
    cls = seconds_cls(T.Circuit) if arm == "base" else arcs_cls(seconds_cls(T.Circuit))
    lf = WLife(seed, first, (lambda s: cls(s, q)), S.world_of("(world)"), seconds=True)
    if arm in ("learn", "toldarcs", "learn2", "learn3", "learn3b", "toldarcsI", "learn3bI"):
        right = []
        for h in (0, 1):                                # a block in the right half (1): the left side's quarter turns it right
            side = 0 if h == 1 else 1
            right.append((lf.wire_h[h], lf.wire_m[4 + side]))
        lf.brain.setup(arm, right)
        lf.right_arcs = right
    return lf


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    arm, seed, first = j
    lf = make(arm, seed, first)
    l = S.live(lf, SECS)
    g = [a - COST * c for a, c, _ in l]
    sp = spent(l)
    b = lf.brain
    sides = {lf.wire_m[th]: th % 2 for th in range(2, 6)}
    return dict(arm=arm, seed=seed, eff=(0.0, 0.0, g[2], sp * l[2][2] / sum(t for _, _, t in l)), grow=lf.grow_at, sides=sides,
                on=sorted(getattr(b, "on", set()) or []), right=sorted(getattr(lf, "right_arcs", [])), log=getattr(b, "log", []))


def report(rows, arms):
    n = len([r for r in rows if r["arm"] == arms[0]]) // 2
    I = R.boot(n)
    base = L.scored([r["eff"] for r in rows if r["arm"] == "base"], SECS, I)
    print(f"== uptake of new parts: {n} pairs, {SECS:.0f} s lives (parts grow at 100 to 300 s), efficiency in the last third [95%]")
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        e = L.scored([r["eff"] for r in rs], SECS, I)
        d = e[1] - base[1]
        line = f"  {a:9s} {e[0]:+.2f} [{np.percentile(e[1], 2.5):+.2f},{np.percentile(e[1], 97.5):+.2f}]"
        if a != "base":
            line += f"  vs base {e[0] - base[0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        if a in ("learn", "learn2", "learn3", "learn3b", "learn3bI"):
            side = lambda arcs, r: {(l, r["sides"].get(m)) for l, m in arcs}
            exact = np.mean([set(map(tuple, r["on"])) == set(map(tuple, r["right"])) for r in rs])
            sideok = np.mean([side(map(tuple, r["on"]), r) == side(map(tuple, r["right"]), r) for r in rs])
            has = np.mean([set(map(tuple, r["right"])) <= set(map(tuple, r["on"])) for r in rs])
            wrong = np.mean([len(set(map(tuple, r["on"])) - set(map(tuple, r["right"]))) for r in rs])
            line += f" | arcs exactly the told two {exact:.0%}; right side for both lines {sideok:.0%}; told two on {has:.0%}; others on, mean {wrong:.1f}"
        print(line, flush=True)


ARMS = ("base", "told", "toldarcs", "learn", "learn2", "learn3", "learn3b", "toldarcsI", "learn3bI")

if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 10
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 103000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/uptake_{n}_s{s0}_{int(SECS)}s.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        with ProcessPoolExecutor(7, initializer=_init) as ex:
            arms = [x for x in a if x in ARMS] or list(ARMS)
            rows = list(ex.map(job, [(arm, s, c) for arm in arms for s in range(s0, s0 + n) for c in L.COL], chunksize=2))
        pickle.dump(rows, open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    report(rows, [a for a in ARMS if any(r["arm"] == a for r in rows)])
