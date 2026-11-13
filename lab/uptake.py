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
there); then taste chooses among those few, as learn2. leanlearn3bI: as learn3bI, but playing only while food is scarcer than usual
(recent FAST s of good meals below the long-run SLOW s), foraging as usual otherwise. Arms ending B: play bored from certainty (a
motor sure at PLAY_BORED standard errors, after PLAY_MIN kicks, is played no more; play ends when every motor is sure or has PLAY_N). Arms ending N: play
until each new line has a motor surely moving activity out of its half (all the wiring needs), then the surest wired.
learn3b: play's surest candidate per line wired at once, no taste. Arms
ending I: the arcs with lateral inhibition between the two new lines (an arc fires only if its line saw more food pulses than the other
in the last INHIB_W s: D24's condition, as one line suppressing the other). learn3c: play's candidates (and none) for each line in turn,
CHOOSE_W s windows twice each, the one with most joint coupling kept (Occam against none): steering judged by coupling, not visibility.
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
WORLDS = {"plain": "(world)", "regrow60": "(world (on meal (if (= colour F) (do (hide block) (after 60 (show block))))))"}
WORLD_TEXT = WORLDS[os.environ.get("UPTAKE_WORLD", "plain")]   # UPTAKE_WORLD=regrow60: food regrows only 60 s after it is eaten (D56)
FAST, SLOW = 20.0, 200.0                        # s: playlean's two running averages of good meals (lean: recent below long-run)
SECS = float(os.environ.get("UPTAKE_SECS", 900.0))      # (UPTAKE_SECS: longer lives, for an evidence-starved learner)
BIN = 0.05
TRY = 10.0
CHOOSE_W = 20.0                                 # learn3c: s a window in the choice among play's candidates, by coupling
INHIB_W = 0.2                                   # s: lateral inhibition between the new lines (arms ending I): an arc fires only if
                                                # its line saw more food pulses than the other line in the last INHIB_W s
PLAY_BORED = 3.0                                # bored play (arms ending B): a motor sure at this many standard errors is played no more
PLAY_MIN = 20                                   # ... once it has at least this many kicks (and the control as many)
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
MOTORS = [2, 3, 4, 5]                           # the new motor lines (set from sim.EXTRA in _init: 2 per new strength)
ARCS = [(line, motor) for line in (2, 3) for motor in MOTORS]


def _init():
    global MOTORS, ARCS
    R._init(0.0025, False)
    from stage2_lang import sim
    sim.WLife.extra = True
    sim.WLife.split = True
    sim.GROW = (100.0, 300.0)
    MOTORS = list(range(2, 2 + 2 * len(sim.EXTRA)))
    ARCS = [(line, motor) for line in (2, 3) for motor in MOTORS]


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
            self.shift, self.effect = {m: [] for m in list(MOTORS) + [None]}, None
            self.lean_only = mode.startswith("lean")    # leanI: play only while food is scarcer than usual (the user: play in the lean spells)
            mode = mode[4:] if self.lean_only else mode
            self.fast = self.slow = 0.0
            self.graded = mode.endswith("V")            # arms ending GV: the network's graded readouts (how far, not only which way)
            mode = mode[:-1] if self.graded else mode
            self.grown = mode.endswith("G")             # arms ending G: play's evidence kept by a growing network (D59), its counts deciding
            mode = mode[:-1] if self.grown else mode
            if self.grown:
                import grownet as GN
                self.gnet = GN.Net("kick", 40, np.random.default_rng(int(self.t * 1000) + 11), alphabet=len(MOTORS) + 1, strict=True)
                self.gi = 0
            self.need_play = mode.endswith("N")         # arms ending N: play until each new line has a sure motor, no longer
            mode = mode[:-1] if self.need_play else mode
            self.bored_play = mode.endswith("B")        # arms ending B: boredom from certainty in play (D48)
            self.sure = set()
            mode = mode[:-1] if self.bored_play else mode
            self.inhib = mode.endswith("I")
            self.rl = []
            mode = mode[:-1] if self.inhib else mode
            self.mode = mode
            self.on = set(right or []) if mode == "toldarcs" else set()
            self.mode3b = mode == "learn3b"
            self.mode3c = mode == "learn3c"
            if mode in ("learn3b", "learn3c"):
                self.mode = mode = "learn3"
            self.cands = None if mode == "learn3" else {2: list(MOTORS), 3: list(MOTORS)}
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
                opts = list(MOTORS) + [None]
                if self.bored_play:                     # boredom from certainty: motors already sure are played no more
                    opts = [m for m in MOTORS if m not in self.sure] + [None]
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
            if getattr(self, "grown", False) and self.cands is None:
                return self._close_grown()
            if self.need_play and len(self.shift[None]) >= PLAY_MIN:   # play until each new line has a sure motor (all it needs)
                ctrl = np.array(self.shift[None], float)
                z = {}
                for m in MOTORS:
                    x = np.array(self.shift[m], float)
                    if len(x) >= PLAY_MIN:
                        se = math.sqrt(x.var(ddof=1) / len(x) + ctrl.var(ddof=1) / len(ctrl)) + 1e-9
                        z[m] = (x.mean() - ctrl.mean()) / se
                if any(v >= SURE for v in z.values()) and any(v <= -SURE for v in z.values()):
                    self.effect = {m: z.get(m, 0.0) for m in MOTORS}
                    self.cands = {2: [m for m in MOTORS if self.effect[m] >= SURE], 3: [m for m in MOTORS if self.effect[m] <= -SURE]}
                    self.log.append((round(self.t), "play done", {m: round(v, 1) for m, v in self.effect.items()}, self.cands))
                    if self.mode3b:
                        for line in (2, 3):
                            m = max(self.cands[line], key=lambda mm: abs(self.effect[mm]))
                            self.choice[line] = (line, m)
                            self.on.add((line, m))
                    return
            if self.bored_play and len(self.shift[None]) >= PLAY_MIN:
                ctrl = np.array(self.shift[None], float)
                for m in MOTORS:
                    x = np.array(self.shift[m], float)
                    if m not in self.sure and len(x) >= PLAY_MIN:
                        se = math.sqrt(x.var(ddof=1) / len(x) + ctrl.var(ddof=1) / len(ctrl)) + 1e-9
                        if abs((x.mean() - ctrl.mean()) / se) >= PLAY_BORED:
                            self.sure.add(m)
            done = all(len(self.shift[m]) >= PLAY_N for m in list(MOTORS) + [None])
            if self.bored_play:
                done = all(m in self.sure or len(self.shift[m]) >= PLAY_N for m in MOTORS) and len(self.shift[None]) >= PLAY_MIN
            if done:
                ctrl = np.array(self.shift[None], float)
                self.effect = {}
                for m in MOTORS:
                    x = np.array(self.shift[m], float)
                    se = math.sqrt(x.var(ddof=1) / len(x) + ctrl.var(ddof=1) / len(ctrl)) + 1e-9
                    self.effect[m] = ((x.mean() - ctrl.mean()) / se)
                # a line's candidates: the motors that surely move activity out of its half (towards the other line)
                self.cands = {2: [m for m in MOTORS if self.effect[m] >= SURE],
                              3: [m for m in MOTORS if self.effect[m] <= -SURE]}
                self.log.append((round(self.t), "play done", {m: round(v, 1) for m, v in self.effect.items()}, self.cands))
                if self.mode3c:                         # learn3c: choose among play's candidates by joint coupling, line by line, in turns
                    self.sched = []
                    for line in (2, 3):
                        opts = sorted(self.cands[line]) + [None]
                        self.choice[line] = None
                        if len(opts) > 1:
                            self.sched += [(line, o) for o in opts * 2]
                    self.cscore = {}
                    self.cwin = None
                if self.mode3b:                         # learn3b: play's surest candidate per line wired at once (its certainty is the Occam bar)
                    for line in (2, 3):
                        c = self.cands[line]
                        if c:
                            m = max(c, key=lambda mm: abs(self.effect[mm]))
                            self.choice[line] = (line, m)
                            self.on.add((line, m))
                        else:
                            self.choice[line] = None

        def _close_grown(self):
            """Play's trials as a stream for a growing network: each trial a step, its symbol the kick (or none), its letter whether
            activity moved towards line 3 (1) or line 2 (0); blocks may grow over sequences of kicks. Done when each line has a kick
            whose own unit surely moves activity out of its half against the no-kick unit (two-proportion test, SURE); the surest wired."""
            N = self.gnet
            for m in list(MOTORS) + [None]:
                xs = self.shift[m]
                while len(xs) > getattr(self, "fed", {}).get(m, 0):
                    x = xs[getattr(self, "fed", {}).get(m, 0)]
                    self.fed = getattr(self, "fed", {})
                    self.fed[m] = self.fed.get(m, 0) + 1
                    sym = len(MOTORS) if m is None else MOTORS.index(m)
                    N.write(self.gi, sym)
                    k, f = N.says(self.gi)
                    if getattr(self, "graded", False):
                        N.add_value(f, float(x))
                    if x != 0:
                        N.learn(self.gi, int(x > 0), self.t, k, f)
                        if k is not None:
                            N.credit(k, self.t)
                    N.tidy(self.gi, self.t)
                    self.gi += 1
            sense = {x["sym"]: x["n"] for x in N.units.values() if x["sym"] is not None}
            c = sense[len(MOTORS)]
            nc = c[0] + c[1]
            if nc < PLAY_MIN:
                return
            z = {}
            if getattr(self, "graded", False):          # graded readouts: how far activity moved, against no kick
                vals = {x["sym"]: x.get("val") for x in N.units.values() if x["sym"] is not None}
                for i, m in enumerate(MOTORS):
                    if vals.get(i) and vals[i][0] >= PLAY_MIN:
                        z[m] = N.welch(vals[i], vals.get(len(MOTORS)))
            for i, m in enumerate(MOTORS if not getattr(self, "graded", False) else []):
                a = sense[i]
                na = a[0] + a[1]
                if na < PLAY_MIN:
                    continue
                pa, pc = a[1] / na, c[1] / nc
                pp = (a[1] + c[1]) / (na + nc)
                z[m] = (pa - pc) / (math.sqrt(max(pp * (1 - pp), 1e-6) * (1 / na + 1 / nc)))
            enough = all(sum(sense[i]) >= PLAY_N for i in range(len(MOTORS)))   # as the hand-built play: stop at PLAY_N kicks each
            if (any(v >= SURE for v in z.values()) and any(v <= -SURE for v in z.values())) or enough:
                self.effect = {m: z.get(m, 0.0) for m in MOTORS}
                self.cands = {2: [m for m in MOTORS if self.effect[m] >= SURE], 3: [m for m in MOTORS if self.effect[m] <= -SURE]}
                blocks = sum(1 for x in N.units.values() if x["sym"] is None)
                self.log.append((round(self.t), "play done", {m: round(v, 1) for m, v in self.effect.items()}, self.cands, blocks))
                for line in (2, 3):
                    if self.cands[line]:
                        m = max(self.cands[line], key=lambda mm: abs(self.effect[mm]))
                        self.choice[line] = (line, m)
                        self.on.add((line, m))
                    else:
                        self.choice[line] = None

        def _choose_by_coupling(self):
            """learn3c: windows of CHOOSE_W s, each with one candidate (or none) for one line, the joint coupling of the eyes with the
            original motors counted (D51); when a line's windows are done, its best option kept (a change from none must beat it by
            OCCAM)."""
            if self.t >= self.next_bin:
                if self.prev is not None and self.cwin is not None:
                    self.J[0][self.prev[1], self.s_bin] += 1
                    self.J[1][self.prev[0], self.a_bin] += 1
                self.prev, self.s_bin, self.a_bin = (self.s_bin, self.a_bin), 0, 0
                self.next_bin += BIN
            if self.cwin is not None and self.t < self.cwin[2]:
                return
            if self.cwin is not None:
                line, opt, _ = self.cwin
                self.cscore.setdefault((line, opt), []).append((_mi(self.J[0]) + _mi(self.J[1])) / BIN)
                if not any(x[0] == line for x in self.sched):          # this line's windows done: keep its best
                    sc = {o: np.mean(v) for (l, o), v in self.cscore.items() if l == line}
                    best = max(sc, key=sc.get)
                    if best is not None and sc[best] > OCCAM * sc.get(None, 0.0):
                        self.choice[line] = (line, best)
                        self.on.add((line, best))
                    else:
                        self.choice[line] = None
                    self.log.append((round(self.t), "chose", line, best, {o: round(v, 2) for o, v in sc.items()}))
            self.J[0][:], self.J[1][:] = 0, 0
            if self.sched:
                line, opt = self.sched.pop(0)
                self.choice[line] = (line, opt) if opt is not None else None
                self.cwin = (line, opt, self.t + CHOOSE_W)
            else:
                self.cwin = None
                self.mode3c = False                     # done: work with the choices

        def taste(self, value, at):
            if value > 0:
                self.fast = getattr(self, "fast", 0.0) + 1.0 / FAST
                self.slow = getattr(self, "slow", 0.0) + 1.0 / SLOW
            super().taste(value, at)

        def lean(self):
            wf, ws = 1.0 - math.exp(-self.t / FAST), 1.0 - math.exp(-self.t / SLOW)
            return self.fast / max(wf, 1e-9) < self.slow / max(ws, 1e-9)

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
            if getattr(self, "lean_only", False):
                self.fast *= math.exp(-0.0025 / FAST)
                self.slow *= math.exp(-0.0025 / SLOW)
            beats = list(getattr(self, "beats", None) or [])
            for m, _ in beats:
                if m < 2:
                    self.a_bin |= 1 << m
            if self.pending:
                beats += self.pending
                self.pending = []
            self.beats = beats
            if self.mode3c and self.cands is not None:
                self._choose_by_coupling()
            elif self.mode == "learn2" or (self.mode == "learn3" and self.cands is not None):
                self._close_probes()
            elif self.mode == "learn3" and self.woke is not None:
                self._close_play()
                if self.cands is None and (not self.lean_only or self.lean()):   # still playing (when lean, for playlean)
                    beats = self._play()
                    self.beats = beats
                    self.played = getattr(self, "played", 0.0) + self.p.get("_dt", 0.0025)
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
    lf = WLife(seed, first, (lambda s: cls(s, q)), S.world_of(WORLD_TEXT), seconds=True)
    if arm in ("learn", "toldarcs", "learn2", "learn3", "learn3b", "toldarcsI", "learn3bI", "learn3c", "learn3cI", "leanlearn3bI", "learn3bIB", "learn3bIN", "learn3bING", "learn3bINGV"):
        right = []
        for h in (0, 1):                                # a block in the right half (1): the left side's quarter turns it right
            side = 0 if h == 1 else 1
            right.append((lf.wire_h[h], lf.wire_m[len(lf.wire_m) - 2 + side]))      # the smallest new thruster on that side
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
    sides = {lf.wire_m[th]: th % 2 for th in range(2, len(lf.wire_m))}
    play_done = next((e[0] for e in getattr(b, "log", []) if len(e) > 1 and e[1] == "play done"), None)
    return dict(arm=arm, seed=seed, eff=(0.0, 0.0, g[2], sp * l[2][2] / sum(t for _, _, t in l)), grow=lf.grow_at, sides=sides,
                play_done=play_done, whole=(sum(g), sp),
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
        if a in ("learn", "learn2", "learn3", "learn3b", "learn3bI", "learn3c", "learn3cI", "leanlearn3bI", "learn3bIB", "learn3bIN", "learn3bING", "learn3bINGV"):
            side = lambda arcs, r: {(l, r["sides"].get(m)) for l, m in arcs}
            exact = np.mean([set(map(tuple, r["on"])) == set(map(tuple, r["right"])) for r in rs])
            sideok = np.mean([side(map(tuple, r["on"]), r) == side(map(tuple, r["right"]), r) for r in rs])
            has = np.mean([set(map(tuple, r["right"])) <= set(map(tuple, r["on"])) for r in rs])
            wrong = np.mean([len(set(map(tuple, r["on"])) - set(map(tuple, r["right"]))) for r in rs])
            line += f" | arcs exactly the told two {exact:.0%}; right side for both lines {sideok:.0%}; told two on {has:.0%}; others on, mean {wrong:.1f}"
            pd = [r["play_done"] - r["grow"] for r in rs if r.get("play_done") is not None]
            if pd:
                line += f" | play done {np.median(pd):.0f} s after growth (median), in {len(pd)} of {len(rs)} lives"
        if a != "base":
            wb = np.array([r["whole"][0] for r in rows if r["arm"] == "base"]).sum() / np.array([r["whole"][1] for r in rows if r["arm"] == "base"]).sum()
            wa = np.array([r["whole"][0] for r in rs]).sum() / np.array([r["whole"][1] for r in rs]).sum()
            line += f" | whole life {wa - wb:+.2f}"
        print(line, flush=True)


ARMS = ("base", "told", "toldarcs", "learn", "learn2", "learn3", "learn3b", "toldarcsI", "learn3bI", "learn3c", "learn3cI", "leanlearn3bI", "learn3bIB", "learn3bIN", "learn3bING", "learn3bINGV")

if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 10
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 103000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/uptake_{n}_s{s0}_{int(SECS)}s{os.environ.get('UPTAKE_WORLD', '')}{'_x' + os.environ['EXTRA_N'] if os.environ.get('EXTRA_N') else ''}.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        with ProcessPoolExecutor(7, initializer=_init) as ex:
            arms = [x for x in a if x in ARMS] or list(ARMS)
            rows = list(ex.map(job, [(arm, s, c) for arm in arms for s in range(s0, s0 + n) for c in L.COL], chunksize=2))
        pickle.dump(rows, open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    report(rows, [a for a in ARMS if any(r["arm"] == a for r in rows)])
