"""ladder.py: the user's ladder of harder tests (2026-11-02; STORIES.md): each one modification to story 1's baseline, none
accumulating. A test is a rule for which colour is poison at each moment, in a wrapper; world.py is untouched. Scored
as every life: food less 2 a poison; a meal is good or bad by the rule at that moment.

Rules (RULES): plain; swap50, swap20, swap10, swap5: the poison colour swaps every so many s; alternate: the colour just
eaten is poison until the other is eaten; pattern: red, red, blue, in order (a colour out of turn is poison).

Arms: circuit (story 1's), told (follows the rule's food colour at every moment: the target for B's movements), and the
interventions below (bit flips, one memory or counter each).

    python lab/ladder.py table [SEEDS]             # each rule's baseline and target
    python lab/ladder.py judge RULE ARM [k=v ...] [SEEDS]"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from discrete import model as M
from minimal.spec import SPAN, Lived, thirds, summary, efficiency, gain, interval
from story1 import Gated, RunLimit
from units import TICK

COL = ("red", "blue")


class Rule:
    """poison(t): the colour that is poison now, or None; ate(colour): told each meal (the rule's own state)."""

    def __init__(self, first):
        self.first = first                              # the life's label: red or blue poison at the start

    def poison(self, t):
        return self.first

    def ate(self, colour):
        pass


class Swap(Rule):
    T = 50.0

    def poison(self, t):
        return COL[(COL.index(self.first) + int(t / self.T)) % 2]


def swap(T):
    return type(f"Swap{T:g}", (Swap,), {"T": float(T)})


class Alternate(Rule):
    last = None

    def poison(self, t):
        return self.last

    def ate(self, colour):
        self.last = colour


class Pattern(Rule):
    """Food in the order A, A, B (A the life's non-first colour): a colour out of turn is bad and leaves the turn where it is."""

    i = 0

    def seq(self):
        a = COL[1 - COL.index(self.first)]
        return (a, a, self.first)

    def poison(self, t):
        want = self.seq()[self.i]
        return COL[1 - COL.index(want)]

    def ate(self, colour):
        if colour == self.seq()[self.i]:
            self.i = (self.i + 1) % 3


class Digest(Rule):
    """The poison colour as ever, and any meal within W s of the last meal is bad too. Scored apart from the colour by
    marking the colour eaten; poison(t) names the fixed colour, bad(c, t) says all."""

    W = 1.0
    was = -1e9

    def taste(self, value):
        return -1.0 if self.now - self.was < self.W else value

    def bad(self, colour, t):
        return colour == self.first or t - self.was < self.W

    def ate(self, colour, t=None):
        self.was = self.now


RULES = {"digest": Digest, "plain": Rule, "swap50": swap(50), "swap20": swap(20), "swap10": swap(10), "swap5": swap(5),
         "alternate": Alternate, "pattern": Pattern}


class Told(RunLimit, M.Model):
    """B's movements, its bit set by the life to the rule's food colour at every moment. V_H 99: it learns nothing."""


class Circuit(RunLimit, Gated):
    pass


class FlipEach(RunLimit, Gated):
    """Alternate by design: every good taste while driving flips the bit too (win-shift)."""

    def taste(self, value, at):
        v = self.vouched()
        f = self.food
        super().taste(value, at)
        if v and value > 0 and self.food == f:
            self.food = 1 - self.food
            self.L = 0
            self.flips.append(self.t)


class Lengths(RunLimit, Gated):
    """A learned run length per eye: how many vouched goods an eye's turn lasts. A vouched good counts up; at the eye's
    learned length the bit flips by itself. A vouched bad means the eye's turn had already ended: the bit flips, and the
    eye's length moves to what the count had reached (at least 1). A length starts at `top`, no limit in practice, so a
    world that never changes never flips by itself. Holds per eye: a counter, a length."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.n = [0, 0]
        self.R = [int(p.get("top", 15)), int(p.get("top", 15))]

    def taste(self, value, at):
        if not self.vouched():
            return
        k = self.food
        p = self.p
        if value > 0:
            self.n[k] += 1
            self.L = max(-int(p.get("trust", 1)), self.L - 1)
            if self.n[k] >= self.R[k]:
                self.n[k] = 0
                self.food, self.L = 1 - k, 0
                self.flips.append(self.t)
        else:
            self.L += 1
            if self.L >= 1:
                self.R[k] = max(1, self.n[k])
                self.n[k] = 0
                self.food, self.L = 1 - k, 0
                self.flips.append(self.t)


class Transition(RunLimit, Gated):
    """Detect, then cure: a tally M of what follows a vouched good from the same eye: a vouched bad steps it up (the eye's
    turn ended), a vouched good down. Past theta the brain flips after every vouched good; the tally goes on being written
    only while it is off, or by what a flip then brings (a bad after a flip lowers it). One memory, one comparator, one
    gate. In a world that never changes it stays below and nothing happens."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.M = 0.0
        self.after_good = False
        self.on_at = []

    def taste(self, value, at):
        if not self.vouched():
            return
        p = self.p
        th, top = p.get("theta", 2.0), p.get("mtop", 4.0)
        on = self.M >= th
        if self.after_good:
            if on:
                self.M = min(top, max(-top, self.M + (0.25 if value > 0 else -1.0)))   # a flip that was right
            else:
                self.M = min(top, max(-top, self.M + (-0.25 if value > 0 else 1.0)))
        if self.M >= th and not on:
            self.on_at.append(self.t)
        if value > 0:
            self.L = max(-int(p.get("trust", 1)), self.L - 1)
            self.after_good = True
            if self.M >= th:
                self.food, self.L, self.after_good = 1 - self.food, 0, False
                self.after_good = True
                self.flips.append(self.t)
        else:
            self.after_good = False
            self.L += 1
            if self.L >= 1:
                self.food, self.L = 1 - self.food, 0
                self.flips.append(self.t)


class AltEye(RunLimit, Gated):
    """Alternate by design, with a credit: after any meal, good or bad, follow the eye that did not pulse last (the eaten
    colour's eye is nearly always the last to pulse). Holds: which eye pulsed last (a latch), no tally."""

    def taste(self, value, at):
        k = 0 if self.last[0] > self.last[1] else 1
        if self.food == k:
            self.food = 1 - k
            self.flips.append(self.t)

    def step(self):
        return super().step()


class Rhythm(RunLimit, Gated):
    """A learned interval: the time between a flip and the vouched poison that forces the next. The bit also flips by itself
    once that interval has passed since the last flip. A vouched poison before the interval shortens it towards the time
    elapsed; a vouched poison soon after a self-made flip (within `undo` s) means it flipped too early: it flips back and
    lengthens the interval. One slow node (the interval), one timer."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.T = p.get("T0", 1e9)
        self.flip_at = 0.0
        self.self_flip = False

    def taste(self, value, at):
        if not self.vouched():
            return
        p = self.p
        if value > 0:
            self.L = max(-int(p.get("trust", 1)), self.L - 1)
            return
        self.L += 1
        if self.L < 1:
            return
        el = self.t - self.flip_at
        a = p.get("rate", 0.3)
        if self.self_flip and el < p.get("undo", 2.0):
            self.T *= 1 + a                             # too early: back, and wait longer
        elif self.T > 1e8:
            self.T = el
        else:
            self.T += a * (el - self.T)
        self.food, self.L, self.flip_at, self.self_flip = 1 - self.food, 0, self.t, False
        self.flips.append(self.t)

    def step(self):
        if self.t - self.flip_at >= self.T:
            self.food, self.L, self.flip_at, self.self_flip = 1 - self.food, 0, self.t, True
            self.flips.append(self.t)
        return super().step()


class Detect(RunLimit, Gated):
    """Detect, then cure, for the alternate rule: the tally M of what follows a vouched good from the same eye (a vouched bad
    up, a vouched good down) until it passes theta; then one latch turns on for good, and from then on the brain follows the
    eye that did not pulse last, after any meal (AltEye). Before that it is story 1's circuit. Holds: one tally, one latch."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.M, self.after_good, self.on, self.on_at = 0.0, False, False, []

    def taste(self, value, at):
        p = self.p
        if self.on:
            k = 0 if self.last[0] > self.last[1] else 1
            if self.food == k:
                self.food = 1 - k
                self.flips.append(self.t)
            return
        if not self.vouched():
            return
        if self.after_good:
            self.M = max(-p.get("mtop", 4.0), self.M + (-p.get("down", 0.25) if value > 0 else 1.0))
            if self.M >= p.get("theta", 2.0):
                self.on = True
                self.on_at.append(self.t)
        if value > 0:
            self.after_good = True
            self.L = max(-1, self.L - 1)
        else:
            self.after_good = False
            self.L += 1
            if self.L >= 1:
                self.food, self.L = 1 - self.food, 0
                self.flips.append(self.t)


class Volatile(RunLimit, Gated):
    """Trust that depends on how recently the bit last flipped: within `tau` s of a flip, none (the next vouched poison flips
    at once); after that, one step. One timer. Volatility read from its own flips."""

    def taste(self, value, at):
        recent = self.flips and self.t - self.flips[-1] < self.p.get("tau", 15.0)
        self.p["trust"] = 0 if recent else 1
        super().taste(value, at)


class Rhythm2(RunLimit, Gated):
    """A rhythm trusted only once it repeats: the intervals between flips that poison forced; when two running agree within
    `agree`, the bit also flips by itself at the interval since the last swap (the forced flip's time less `lag`, the
    typical wait for the poison). A vouched poison soon after a self-made flip counts against: twice, and it stops."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.T, self.prev, self.flip_at, self.self_flip, self.bad, self.est = None, None, 0.0, False, 0, 0.0

    def taste(self, value, at):
        if not self.vouched():
            return
        p = self.p
        if value > 0:
            self.L = max(-int(p.get("trust", 1)), self.L - 1)
            return
        self.L += 1
        if self.L < 1:
            return
        el = self.t - self.flip_at
        if self.self_flip and el < p.get("undo", 2.0):
            self.bad += 1
            if self.bad >= p.get("strikes", 2):
                self.T, self.bad = None, 0
        else:
            if self.prev and max(el, self.prev) / max(1e-3, min(el, self.prev)) < p.get("agree", 1.35):
                self.T = 0.5 * (el + self.prev)
            self.prev = el
            self.bad = 0
        self.food, self.L, self.flip_at, self.self_flip = 1 - self.food, 0, self.t - p.get("lag", 1.0), False
        self.flips.append(self.t)

    def step(self):
        if self.T and self.t - self.flip_at >= self.T:
            self.food, self.L, self.flip_at, self.self_flip = 1 - self.food, 0, self.t, True
            self.flips.append(self.t)
        return super().step()


class Lengths2(RunLimit, Gated):
    """Run lengths per eye, a step at a time. After a vouched bad: if the eye had given goods, its length is what it reached;
    if none (the flip came too early), the eye flipped from gets one more. A length is believed only once it has come out the
    same twice, so one stray poison in a plain world doesn't start it."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.n, self.R, self.seen_len = [0, 0], [None, None], [None, None]

    def taste(self, value, at):
        if not self.vouched():
            return
        k = self.food
        if value > 0:
            self.n[k] += 1
            self.L = max(-1, self.L - 1)
            if self.R[k] and self.n[k] >= self.R[k]:
                self.n[k], self.food, self.L = 0, 1 - k, 0
                self.flips.append(self.t)
            return
        self.L += 1
        if self.L < 1:
            return
        if self.n[k] > 0:
            if self.seen_len[k] == self.n[k]:
                self.R[k] = self.n[k]
            self.seen_len[k] = self.n[k]
        elif self.R[1 - k]:
            self.R[1 - k] += 1
        self.n[k], self.food, self.L = 0, 1 - k, 0
        self.flips.append(self.t)


class Cycle(RunLimit, Gated):
    """A sequence memory, needing no detector: a counter of length `cycle` that every good taste advances, each position
    holding which eye to follow (a bit) and its own one step of trust. A vouched bad at a position steps its tally up, past
    which that position's bit flips; a vouched good down. Length 1 is story 1's circuit. Holds: a counter, `cycle` bits,
    `cycle` tallies."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        n = int(p.get("cycle", 2))
        self.c, self.bits, self.tally = 0, [self.food] * n, [0] * n
        self.n = n

    def taste(self, value, at):
        c, trust = self.c, int(self.p.get("trust", 1))
        v = self.vouched()
        if value > 0:
            if v:
                self.tally[c] = max(-trust, self.tally[c] - 1)
            self.c = (c + 1) % self.n
        elif v:
            self.tally[c] += 1
            if self.tally[c] >= 1:
                self.bits[c], self.tally[c] = 1 - self.bits[c], 0
                self.flips.append(self.t)
        self.food = self.bits[self.c]


class Rhythm3(RunLimit, Gated):
    """A clock that tracks the swaps: a period believed once two running intervals between forced flips agree. A forced flip
    (a vouched poison with the clock not just flipped) dates the last swap at `lag` before now, and the clock's next flip one
    period after that. A vouched poison just after the clock's own flip means it was early: back, and try again shortly.
    Holds: a period, a timer."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.T, self.prev, self.forced, self.next, self.own, self.fails = None, None, 0.0, 1e18, -1e18, 0

    def taste(self, value, at):
        if not self.vouched():
            return
        p = self.p
        if value > 0:
            self.L = max(-int(p.get("trust", 1)), self.L - 1)
            return
        self.L += 1
        if self.L < 1:
            return
        lag = p.get("lag", 1.0)
        if self.t - self.own < p.get("undo", 2.0):
            self.fails += 1
            self.next = self.t + p.get("retry", 0.5)    # too early: back, and the swap must be near
            if self.fails >= p.get("strikes", 4):
                self.T, self.next, self.fails, self.prev = None, 1e18, 0, None
        else:
            el = self.t - self.forced
            self.forced = self.t
            if self.T is None:
                if self.prev and max(el, self.prev) / max(1e-3, min(el, self.prev)) < p.get("agree", 1.35):
                    self.T = 0.5 * (el + self.prev)
                self.prev = el
            else:
                k = max(1, round(el / self.T))          # (it may have been right for several periods)
                self.T += p.get("rate", 0.2) * (el / k - self.T)
                self.fails = 0
            if self.T:
                self.next = self.t - lag + self.T
        self.food, self.L = 1 - self.food, 0
        self.flips.append(self.t)

    def step(self):
        if self.t >= self.next:
            self.food, self.L = 1 - self.food, 0
            self.own = self.t
            self.next = self.t + self.T if self.T else 1e18
            self.flips.append(self.t)
        return super().step()


class GrowSeq(Cycle):
    """Detect and grow: starts as story 1's circuit (length 1). Frustration F, a leaky tally (tau) of vouched bads: poison
    while driving at what it thought was food. Past theta the sequence grows to its next length (a recruit: a position's bit
    and tally, the counter one step longer), F starts again, and the new positions copy the old. A world where one bit
    suffices leaves F low, and nothing grows. Holds: F, a growth primitive, and what Cycle holds at its final length."""

    SIZES = (1, 2, 3, 6)

    def __init__(self, seed, p):
        p = dict(p, cycle=1)
        super().__init__(seed, p)
        self.F, self.i, self.grew = 0.0, 0, []

    def taste(self, value, at):
        if value < 0 and self.vouched():
            self.F += 1.0
            if self.F >= self.p.get("theta", 3.0) and self.i + 1 < len(self.SIZES):
                self.i += 1
                n = self.SIZES[self.i]
                self.bits = [self.bits[j % self.n] for j in range(n)]
                self.tally = [self.tally[j % self.n] for j in range(n)]
                self.c, self.n, self.F = self.c % n, n, 0.0
                self.grew.append((self.t, n))
        super().taste(value, at)

    def step(self):
        self.F *= 1 - TICK / self.p.get("tau", 20.0)
        return super().step()


class Pause(RunLimit, Gated):
    """For the digest test: after any taste it keeps still for `pause` s, firing nothing and starting no drive. Told its pause;
    told=1 sets the bit too."""

    ate_at = -1e9

    def taste(self, value, at):
        self.ate_at = self.t
        super().taste(value, at)

    def step(self):
        if self.t - self.ate_at < self.p.get("pause", 1.0):
            self.seen = [0, 0]
            super().step()
            return []
        return super().step()


class LearnPause(Pause):
    """The pause learned: a tally P of bads tasted within `win` s of the last taste, stepped down by goods so soon. Past theta
    the pause is on, its length `margin` times the running largest gap at which a bad still came. Holds: a tally, a slow node."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.P, self.on_at, self.est = 0.0, [], 0.0
        self.p["pause"] = 0.0

    def taste(self, value, at):
        gap = self.t - self.ate_at
        p = self.p
        if gap < p.get("win", 2.0):
            if value < 0:
                self.P = min(p.get("mtop", 6.0), self.P + 1)
                self.est = max(self.est * 0.98, gap)
                if self.P >= p.get("theta", 3.0) and not self.on_at:
                    self.on_at.append(self.t)
            else:
                self.P = max(0.0, self.P - p.get("down", 1.0))
        if self.P >= p.get("theta", 3.0) or self.on_at:
            p["pause"] = p.get("margin", 1.2) * self.est
        super().taste(value, at)


class Diagnose(GrowSeq):
    """Which cure? The run of goods since the last vouched bad tells the kind of failure. A vouched bad after a short run
    (at most `short`) charges F, as GrowSeq's: a sequence too short. One after a long run marks a world that changes: trust goes
    to 0 for `tau_v` s, so the next vouched bad flips at once. Adds to GrowSeq one counter, one timer."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.run_g, self.volatile_at = 0, -1e9

    def taste(self, value, at):
        p = self.p
        if self.vouched():
            if value > 0:
                self.run_g += 1
            else:
                long_run = self.run_g > p.get("short", 2)
                self.run_g = 0
                if long_run:
                    if self.t - self.last_long < p.get("tau_v", 40.0):
                        self.volatile_at = self.t
                    self.last_long = self.t
                    p["trust"] = 0 if self.t - self.volatile_at < p.get("tau_v", 40.0) else 1
                    Cycle.taste(self, value, at)
                    return
        p["trust"] = 0 if self.t - self.volatile_at < p.get("tau_v", 40.0) else 1
        super().taste(value, at)

    last_long = -1e9


ARMS = {"circuit": Circuit, "told": Told, "flip": FlipEach, "lengths": Lengths, "transition": Transition, "alteye": AltEye, "rhythm": Rhythm, "detect": Detect, "volatile": Volatile, "rhythm2": Rhythm2, "lengths2": Lengths2, "cycle": Cycle, "rhythm3": Rhythm3, "grow": GrowSeq, "diagnose": Diagnose, "pause": Pause, "learnpause": LearnPause}


def life(job):
    rule, arm, kw, seed, seconds, first = job
    p, spread = M.from_bench()
    q = dict(M.drawn(p, spread, seed), use=0, trust=1, run_max=1.0)
    q.update(kw)
    told = arm == "told" or kw.get("told")
    if told:
        q["V_H"] = 99.0
    R = RULES[rule](first)
    lf = Life(seed, first, brain=lambda s: ARMS[arm](s, q))
    b = lf.brain
    if hasattr(R, "taste"):                             # the taste of a meal too soon after the last: bad, whatever its colour
        tasted, inner = b.taste, b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    ticks = int(round(seconds / TICK))
    labelled = 0
    while lf.t < ticks:
        t = lf.t * TICK
        po = R.poison(t)
        lf.poison = po
        R.now = t
        if told:
            b.food = lf.sensor[COL[1 - COL.index(po)]] if po else b.food
        lf.step()
        while labelled < len(lf.meals):                 # scored by the rule; told the rule of each meal
            tk, c = lf.meals[labelled]
            badm = R.bad(c, t) if hasattr(R, "bad") else c == po
            lf.meals[labelled] = (tk, "red" if badm else "blue")
            R.ate(c)
            labelled += 1
    l = Lived(thirds(lf.meals, lf.moving, ticks, "red"))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.flips = list(getattr(b, "flips", []))
    l.R = list(getattr(b, "R", []))
    l.M = getattr(b, "M", None)
    l.on_at = list(getattr(b, "on_at", []))
    l.T = getattr(b, "T", None)
    l.grew = list(getattr(b, "grew", []))
    l.n = getattr(b, "n", None)
    return l


def run(rule, arm, seeds, kw=None, seconds=100.0, workers=8):
    jobs = [(rule, arm, kw or {}, s, seconds, c) for s in seeds for c in COL]
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(life, jobs, chunksize=4))


def paired(A, B, f=efficiency, boot=2000):
    rng = np.random.default_rng(0)
    n = len(A) // 2
    d = []
    for _ in range(boot):
        k = rng.integers(0, n, n)
        d.append(f([l for i in k for l in (A[2 * i], A[2 * i + 1])]) - f([l for i in k for l in (B[2 * i], B[2 * i + 1])]))
    return f(A) - f(B), interval(d)


def line(name, L):
    s = summary(L)
    c = s["ci"]["efficiency"]
    print(f"{name}: efficiency {s['efficiency']:.2f} [{c[0]:.2f}, {c[1]:.2f}]  gain {s['gain']:.2f}  food {s['food']:.2f}  poison {s['poison']:.2f}  "
          f"last third {s['last']:.2f}  stranded {s['stranded']:.0%}  firings {s['firings']:.0f}", flush=True)
    return s


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args.pop(0)
    kw = {a.split("=")[0]: float(a.split("=")[1]) for a in args if "=" in a}
    rest = [a for a in args if "=" not in a]
    seeds = range(52000, 52064)
    if rest and ":" in rest[-1]:
        lo, hi = rest.pop().split(":")
        seeds = range(int(lo), int(hi))
    if cmd == "table":
        for rule in RULES:
            a, b = run(rule, "circuit", seeds), run(rule, "told", seeds)
            line(f"{rule}: baseline", a)
            line(f"{rule}: target", b)
            d, i = paired(b, a)
            print(f"   gap {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
    else:
        L = run(rest[0], rest[1], seeds, kw)
        line(f"{rest[0]} {rest[1]} {kw}", L)
