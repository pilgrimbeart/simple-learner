"""table.py: the interventions table (the user, 2026-11-03; STORIES.md): one mismatch at a time against story 1's finished
circuit, every class of PARTS.md's section 5 tried, tuned on training seeds, judged on seeds that chose nothing. A world is
a wrapper: world.py is untouched and the standard body keeps its identical thrusters and eyes.

    python lab/table.py gaps [WORLD ...]                # each world's baseline and target
    python lab/table.py judge WORLD ARM [k=v ...] [--seconds S] [--seeds LO:HI]
    python lab/table.py tune WORLD ARM [--n N] [--seconds S]    # random settings on training seeds, the best held out

Training seeds 53000-53015 x 2; held out 53100-53163 x 2 (`HELD`); a k_x=v scales the life's drawn number k by v."""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
from minimal.spec import SPAN, Lived, thirds, summary, efficiency, interval
import world
import ladder as Lad
from ladder import Rule, COL, paired
from story1 import Gated, RunLimit, Path, Still
import grow as G
from units import TICK, MILLI
import periodbal as PB
import drivebal as DB

TRAIN, HELD = range(53000, 53016), range(53100, 53164)


class Flaw(Rule):
    """A mismatch: Rule's poison and meals, and hooks on the life. told: the mismatch is removed or stated to the brain, the
    row's target."""

    told = False

    def setup(self, lf, seed):
        pass

    def tick(self, lf, t):
        pass

    def target(self):
        return "told"                                   # the target's arm

    def told_poison(self, t):
        return self.poison(t)


class Thrusters(Flaw):
    """Each thruster drawn 0.5 to 2 (the bodies the project has used). Told: each motor's rate set for a straight drive."""

    def setup(self, lf, seed):
        f = draw(seed, THRUSTERS)
        vary(lf, f)
        thr = {m: t for t, m in lf.motor.items()}
        self.right = float(np.log(f[thr[1]] / f[thr[0]]))
        lf.brain.p["sync"] = 1
        if lf.brain.p.get("scan_told"):
            lf.brain.p["scan_m"] = int(self.right > 0) ^ int(lf.brain.p.get("scan_flip", 0))
        if self.told:
            lf.brain.p["g0"], lf.brain.p["g1"] = float(np.exp(self.right / 2)), float(np.exp(-self.right / 2))


class Ageing(Flaw):
    """Born identical; one thruster (by a coin) weakens steadily, the log balance moving RATE per s, so a calibration made once
    goes stale. Told: the balance at every moment."""

    RATE = 0.001

    def setup(self, lf, seed):
        self.sign = 1 if np.random.default_rng(seed + 5_500_009).random() < 0.5 else -1
        vary(lf, {"left": 1.0, "right": 1.0})
        self.thr = {m: t for t, m in lf.motor.items()}
        lf.brain.p["sync"] = 1

    def tick(self, lf, t):
        a = self.sign * self.RATE * t
        f = lf.body.factors
        f["left"], f["right"] = float(np.exp(a / 2)), float(np.exp(-a / 2))
        if self.told:
            x = float(np.log(f[self.thr[1]] / f[self.thr[0]]))
            lf.brain.p["g0"], lf.brain.p["g1"] = float(np.exp(x / 2)), float(np.exp(-x / 2))


class NoisyEye(Flaw):
    """One eye (by a coin) also fires at random, RATE per s, whatever it sees. Told: no spurious pulses."""

    RATE = 10.0

    def setup(self, lf, seed):
        r = np.random.default_rng(seed + 5_500_011)
        self.eye, self.r = int(r.integers(2)), r
        lf.brain.p["bad_eye"] = self.eye

    def tick(self, lf, t):
        if not self.told:
            for _ in range(self.r.poisson(self.RATE * TICK)):
                lf.brain.stimulate(self.eye, self.r.random() * TICK)


class WeakEye(Flaw):
    """One eye (by a coin) passes only a fraction K of its pulses. Told: the standard body."""

    K = 0.25

    def setup(self, lf, seed):
        r = np.random.default_rng(seed + 5_500_013)
        eye = int(r.integers(2))
        lf.brain.p["bad_eye"] = eye
        if not self.told:
            inner = lf.brain.stimulate

            def stimulate(sensor, at):
                if sensor != eye or r.random() < self.K:
                    inner(sensor, at)
            lf.brain.stimulate = stimulate


class Scarce(Flaw):
    """A sixth of the blocks: 3 of each colour. No told version exists: a target must come from search."""

    KEEP = 3

    def setup(self, lf, seed):
        b = lf.body
        i = [j for k in range(2) for j in np.flatnonzero(b.kind == k)[:self.KEEP]]
        b.xy, b.kind = b.xy[i], b.kind[i]

    def target(self):
        return None


class Patchy(Flaw):
    """The same blocks, in PATCHES fixed clumps of mixed colours (a normal of SD about the clump's), a block eaten reappearing
    in a clump chosen at random. So a meal predicts more nearby. No told version: a target must come from search."""

    PATCHES, SD = 4, 3 * MILLI

    def setup(self, lf, seed):
        r = np.random.default_rng(seed + 5_500_017)
        centres = r.uniform(0, world.WORLD, (self.PATCHES, 2))
        b = lf.body

        def somewhere():
            for _ in range(100):
                q = (centres[r.integers(self.PATCHES)] + r.normal(0, self.SD, 2)) % world.WORLD
                if np.linalg.norm(b.wrap(q - b.pos)) > 3 * world.EAT + world.BODY:
                    return q
            return q
        b.somewhere = somewhere
        b.xy = np.array([somewhere() for _ in b.kind])

    def target(self):
        return None


class Unreliable(Flaw):
    """A colour is only usually what it is: each meal is the life's poison colour's opposite with chance E. Told: the colour."""

    E = 0.2

    def setup(self, lf, seed):
        self.r = np.random.default_rng(seed + 5_500_019)

    def poison(self, t):
        return COL[1 - COL.index(self.first)] if self.r.random() < self.E else self.first

    def told_poison(self, t):
        return self.first


class Moving(Flaw):
    """Every block drifts in its own direction at SPEED. No told version: a target must come from search."""

    SPEED = 5 * MILLI

    def setup(self, lf, seed):
        r = np.random.default_rng(seed + 5_500_023)
        a = r.uniform(0, 2 * np.pi, len(lf.body.kind))
        self.v = self.SPEED * np.column_stack((np.cos(a), np.sin(a)))

    def tick(self, lf, t):
        lf.body.xy = (lf.body.xy + self.v * TICK) % world.WORLD

    def target(self):
        return None


class Swap(Flaw, Lad.Swap):
    pass


class Swap10(Swap):
    T = 10.0


class Alternate(Flaw, Lad.Alternate):
    pass


class Pattern(Flaw, Lad.Pattern):
    pass


class Digest(Flaw, Lad.Digest):
    def target(self):
        return "toldpause"


class Plain(Flaw):
    pass


class AllFood(Flaw):
    """The control for anything that should happen only with something to learn: both colours food."""

    def poison(self, t):
        return None


WORLDS = {"plain": Plain, "allfood": AllFood, "thrusters": Thrusters, "swap10": Swap10, "alternate": Alternate, "pattern": Pattern, "digest": Digest,
          "patchy": Patchy, "scarce": Scarce, "noisy": NoisyEye, "weak": WeakEye, "ageing": Ageing, "unreliable": Unreliable, "moving": Moving}
LONG = {"ageing": 1000.0, "thrusters": 1000.0}                               # a life long enough for the mismatch to bite


class Told(RunLimit, M.Model):
    """B's movements, its bit set to the rule's food colour at every moment. It learns nothing."""


class Circuit(RunLimit, Gated):
    """The base brain: story 1's."""


class ToldPause(Lad.Pause):
    """Digest's target: the colour told, and still for the 1 s."""


class Probe(Circuit):
    """Sense: every probe_T s, for probe_len s, it follows the other eye. A vouched good there keeps the flip; a vouched bad
    ends the probe and costs the bit nothing. Moving in order to learn. Holds: a timer."""

    probing, until, next_probe = False, 0.0, None

    def taste(self, value, at):
        if not self.probing:
            return super().taste(value, at)
        if self.vouched():
            self.probing, self.L = False, 0
            self.next_probe = self.t + self.p["probe_T"]
            if value > 0:
                self.flips.append(self.t)
            else:
                self.food = 1 - self.food

    def step(self):
        p = self.p
        if self.next_probe is None:
            self.next_probe = p["probe_T"]
        if self.probing and self.t >= self.until:
            self.probing, self.food = False, 1 - self.food
            self.next_probe = self.t + p["probe_T"]
        elif not self.probing and self.t >= self.next_probe:
            self.probing, self.food, self.until = True, 1 - self.food, self.t + p["probe_len"]
        return super().step()


class PathC(RunLimit, Path):
    """Use: no bit, each eye judged by its own drives, ignored once bad (story 1's)."""


class ScanSide(Circuit):
    """Use: the scan on motor scan_m (told, for the thrusters' sign: Thrusters.setup)."""

    def step(self):
        out = super().step()
        if self.p.get("scan_m") and out and all(m == 0 for m in out):
            return [1] * len(out)
        return out


class ScanLearn(ScanSide):
    """The scan's motor chosen by trying: trial s on each, then the one with more good tastes; tried again every again s. One
    bit, two counters. Good tastes count, so it needs no signal beyond the taste."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.c, self.side, self.next, self.settled = [0, 0], 0, p.get("trial", 20.0), False
        self.p["scan_m"] = 0

    def taste(self, value, at):
        super().taste(value, at)
        if value > 0:
            self.c[int(self.p["scan_m"])] += 1

    def step(self):
        if self.t >= self.next:
            p = self.p
            if self.side == 0:
                self.side, p["scan_m"], self.next = 1, 1, self.t + p.get("trial", 20.0)
            else:
                p["scan_m"], self.c, self.side, self.next = int(self.c[1] > self.c[0]), [0, 0], 2, self.t + p.get("again", 1e9)
                self.side = 0 if p.get("again") else 2
        return super().step()


class SweepsC(RunLimit, Gated, PB.PeriodBal):
    """Sense: D20's sweeps on the base brain. forget: each sweep scales what the counters hold, so an old body fades."""

    def taste(self, value, at):
        Gated.taste(self, value, at)
        if value > 0:
            self.meals += 1
            self.mt.append(self.fc)

    def _close(self, scan=False):
        super()._close(scan)
        f = self.p.get("forget")
        if f:
            for m in (0, 1):
                self.h[m] *= f
                self.null[m] *= f
                self.var[m] *= f
                self.hb[m] *= f


class JitterC(RunLimit, Gated, DB.DriveBal):
    """Judge: D19's balance jittered per drive, on the base brain."""


class Filter(Circuit):
    """A pulse counts only if the same eye pulsed within `win` s before (a coincidence: a brief memory of one bit). eye_told=1:
    only on the eye the body makes noisy; win=0 with it: that eye ignored."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.pt = [-1e9, -1e9]

    def stimulate(self, sensor, at):
        now = self.t + at
        old, self.pt[sensor] = self.pt[sensor], now
        if self.p.get("eye_told") and sensor != self.p.get("bad_eye"):
            return super().stimulate(sensor, at)
        if now - old < self.p.get("win", 0.05):
            super().stimulate(sensor, at)


class Integrate(Circuit):
    """Each eye a leaky count (tau); a pulse passes only with the count at theta. A memory per eye."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.cnt, self.tu = [0.0, 0.0], [0.0, 0.0]

    def level(self, k):
        if self.p.get("eye_told") and k != self.p.get("bad_eye"):
            return 1.0
        return self.p.get("theta", 2.0)

    def stimulate(self, sensor, at):
        now = self.t + at
        self.cnt[sensor] = self.cnt[sensor] * np.exp(-(now - self.tu[sensor]) / self.p.get("tau_e", 0.1)) + 1.0
        self.tu[sensor] = now
        if self.cnt[sensor] >= self.level(sensor):
            super().stimulate(sensor, at)


class AdaptEye(Integrate):
    """Automatic: each eye's slow running rate (tau_s); the level a margin over what that rate alone would hold in the leaky
    count, and never below 1, so an eye with no background passes every pulse."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.slow, self.su = [0.0, 0.0], [0.0, 0.0]

    def level(self, k):
        return max(1.0, self.p.get("margin", 2.0) * self.slow[k] * self.p.get("tau_e", 0.1))

    def stimulate(self, sensor, at):
        now = self.t + at
        ts = self.p.get("tau_s", 10.0)
        self.slow[sensor] = self.slow[sensor] * np.exp(-(now - self.su[sensor]) / ts) + 1.0 / ts
        self.su[sensor] = now
        super().stimulate(sensor, at)


class EyeHold(Circuit):
    """A drive's hold scaled while following the weak eye (told: bad_eye), so sparse pulses still hold it."""

    def step(self):
        if not hasattr(self, "hold0"):
            self.hold0 = self.p["hold"]
        self.p["hold"] = self.hold0 * (self.p.get("eye_k", 1.0) if self.food == self.p.get("bad_eye") else 1.0)
        return super().step()


class AutoHold(Circuit):
    """Automatic EyeHold: each eye's slow running rate; the hold scaled by the other eye's rate over the followed eye's, within
    limits, so two equal eyes give about 1. Two slow nodes."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.r, self.hold0 = [1.0, 1.0], None

    def stimulate(self, sensor, at):
        self.r[sensor] += 1.0
        super().stimulate(sensor, at)

    def step(self):
        p = self.p
        if self.hold0 is None:
            self.hold0 = p["hold"]
        d = np.exp(-TICK / p.get("tau_s", 30.0))
        self.r[0] *= d
        self.r[1] *= d
        ratio = self.r[1 - self.food] / self.r[self.food]
        p["hold"] = self.hold0 * min(p.get("top", 4.0), max(1.0, ratio ** p.get("pow", 1.0)))
        return super().step()


class EyeSlow(Circuit):
    """Sense, for the weak eye: everything slower while following the weak eye (told: bad_eye), so it gets longer to see; slow_b
    the same while the weak eye is the one ignored."""

    def step(self):
        p = self.p
        if not hasattr(self, "r0"):
            self.r0 = (p["scan"], p["drive"], p["hold"])
        k = p.get("slow_k", 0.5) if self.food == p.get("bad_eye") else p.get("slow_b", 1.0)
        p["scan"], p["drive"], p["hold"] = self.r0[0] * k, self.r0[1] * k, self.r0[2] / k
        return super().step()


class LearnTrust(Circuit):
    """Automatic, for unreliable taste: a flip that bounces (a vouched bad before `short` vouched goods) was likely false. A leaky
    tally B of bounces sets the trust, from 1 up to top. Holds: a run counter, a slow node."""

    B, goods, watching = 0.0, 0, False

    def taste(self, value, at):
        p = self.p
        if self.vouched():
            if self.watching:
                if value > 0:
                    self.goods += 1
                    self.watching = self.goods < p.get("short", 3)
                else:
                    self.B += 1.0
                    self.watching = False
            p["trust"] = 1 + int(min(p.get("top", 3.0) - 1, self.B))
        n = len(self.flips)
        super().taste(value, at)
        if len(self.flips) > n:
            self.watching, self.goods = True, 0

    def step(self):
        self.B *= 1 - TICK / self.p.get("tau_b", 60.0)
        return super().step()


class SweepsG(SweepsC):
    """Sweeps that only a shortage of meals allows, the balance moving only then too, so a body that eats well is left alone."""

    def taste(self, value, at):
        if self.t < self.cal_until:                     # a sweep ignores what it sees, so what it eats says nothing of the bit
            if value > 0:
                self.meals += 1
                self.mt.append(self.fc)
            return
        super().taste(value, at)

    def _learn(self):
        if self.t >= self.next and self.fc > 0 and self.content():
            self.next += self.p.get("every", 20.0)
            return []
        return super()._learn()


class JitterG(JitterC):
    """D19's jitter only while meals are short: good tastes on the last 32 s of life under `gate`. Holds: a leaky count of meals."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.sd0, self.rate = self.p.get("sd", 0.3), self.p.get("gate", 12.0) * self.p.get("win", 32.0) / 32.0     # (born content)

    def taste(self, value, at):
        Gated.taste(self, value, at)
        if value > 0:
            self.rate += 1.0

    def step(self):
        w = self.p.get("win", 32.0)
        self.rate *= 1 - TICK / w
        self.p["sd"] = self.sd0 if self.rate * 32.0 / w < self.p.get("gate", 12.0) else 0.0
        return super().step()


class Volatile2(Circuit):
    """Trust falls for tau s only after a flip that ended a run of at least `k` vouched goods, `need` of them within tau: the mark
    of a world that was right and changed. A flip at birth has no such run. Holds: a run counter, a timer."""

    run_g, until, last_long = 0, -1e9, -1e9

    def taste(self, value, at):
        p = self.p
        if value > 0 and self.vouched():
            self.run_g += 1
        p["trust"] = 0 if self.t < self.until else 1
        n = len(self.flips)
        super().taste(value, at)
        if len(self.flips) > n:
            tau = p.get("tau", 40.0)
            if self.run_g >= p.get("k", 3.0):
                if p.get("need", 1.0) <= 1 or self.t - self.last_long < tau:
                    self.until = self.t + tau
                self.last_long = self.t
            self.run_g = 0


class LearnPause2(Lad.Pause):
    """The pause, learned and able to lapse: a tally P of bads within `win` s of the last taste, less for goods so soon, leaking
    (tau_p). The pause is on while P is at theta, its length a staircase: up to a bad's gap times `margin`, down a little at a good.
    With the pause on nothing comes soon, P leaks away and it lapses, so a false alarm ends itself. Holds: a tally, a slow node."""

    P, est = 0.0, 0.0

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.p["pause"] = 0.0
        self.on_at = []

    def taste(self, value, at):
        gap = self.t - self.ate_at
        p = self.p
        if value < 0 and gap < p.get("win", 1.5) and (not p.get("vouch") or self.vouched()):
            self.P = min(p.get("mtop", 6.0), self.P + 1)
            self.est = max(self.est, gap * p.get("margin", 1.1))
        elif value > 0:
            if gap < p.get("win", 1.5):
                self.P = max(0.0, self.P - p.get("down", 1.0))
            self.est *= p.get("shrink", 0.98)
        super().taste(value, at)

    def step(self):
        p = self.p
        self.P *= 1 - TICK / p.get("tau_p", 200.0)
        on = self.P >= p.get("theta", 3.0)
        if on and not p["pause"]:
            self.on_at.append(self.t)
        p["pause"] = self.est if on else 0.0
        return super().step()


class SweepsG2(SweepsG):
    """The gate must read short `debounce` slots running before a sweep; the first sweep of a contented body is then rare, and the
    balance moves only on `need` pairs. Holds: a small counter."""

    shorts, checked = 0, -1e9

    def content(self):
        c = super().content()
        if self.t - self.checked >= self.p["cal_every"]:
            self.checked, self.shorts = self.t, 0 if c else self.shorts + 1
        return c or self.shorts < self.p.get("debounce", 2.0)


class JitterG2(JitterG):
    """Born well above the gate (`born` times it), so a life's start isn't taken for a shortage."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rate *= self.p.get("born", 1.5)


class LearnPause3(Lad.Pause):
    """The pause, judged against later meals: a tally P up for a bad within `win` s of the last taste, down `late` for a bad after
    longer (bads that don't care about the gap say nothing of it), down for a good so soon: `down` while the pause is off, `down_on`
    while on (a good just after the pause speaks well of the pause). Pause on while P is at theta. Its length a staircase: a bad's gap
    x `margin` up, shrink at each good inside win, so the many goods long after say nothing. Holds: a tally, a slow node."""

    P, est = 0.0, 0.0

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.p["pause"] = 0.0
        self.on_at = []

    def taste(self, value, at):
        gap = self.t - self.ate_at
        p = self.p
        soon = gap < p.get("win", 1.5)
        if p.get("vouch") and not self.vouched():       # vouch=1: only meals of the colour it was driving at as food
            super().taste(value, at)
            return
        if value < 0:
            if soon:
                self.P = min(p.get("mtop", 6.0), self.P + 1)
                self.est = max(self.est, gap * p.get("margin", 1.2))
            else:
                self.P = max(0.0, self.P - p.get("late", 1.0))
        elif value > 0 and soon:
            self.P = max(0.0, self.P - (p.get("down_on", 0.0) if p["pause"] else p.get("down", 1.0)))
            self.est *= p.get("shrink", 0.98)
        super().taste(value, at)

    def step(self):
        p = self.p
        self.P *= 1 - TICK / p.get("tau_p", 400.0)
        on = self.P >= p.get("theta", 3.0) or (p["pause"] and self.P > p.get("off", p.get("theta", 3.0)))     # off: it lapses only below this
        if on and not p["pause"]:
            self.on_at.append(self.t)
        p["pause"] = self.est if on else 0.0
        return super().step()


class Bt(LearnTrust):
    """LearnTrust whose bounce counts step_b."""

    def taste(self, value, at):
        was = self.B
        super().taste(value, at)
        if self.B > was:
            self.B = was + self.p.get("step_b", 1.0)


class Unwired(RunLimit, G.Unwired):
    """Row 1's base: taste wired to nothing, either eye starts a drive."""


class B(RunLimit, M.Model):
    """Row 1's Store: the bounded tally, written by every taste."""


class JudgeSoon(Circuit):
    """Judge, for digest: a taste within W s of the last says nothing of the colour, so the bit ignores it. Moves nothing else."""

    was = -1e9

    def taste(self, value, at):
        soon = self.t - self.was < self.p.get("W", 1.0)
        self.was = self.t
        if not soon:
            super().taste(value, at)


class Local(Circuit):
    """Store, for patchy: a meal within local_t s lengthens how long it scans here (bored) and shortens nothing else; no meal for
    long makes the run between clumps longer. A timer."""

    was = -1e9

    def taste(self, value, at):
        self.was = self.t
        super().taste(value, at)

    def step(self):
        p = self.p
        if not hasattr(self, "b0"):
            self.b0, self.r0 = p["bored"], p["run_max"]
        near = self.t - self.was < p.get("local_t", 2.0)
        p["bored"] = self.b0 * (p.get("local_k", 3.0) if near else 1.0)
        p["run_max"] = self.r0 * (1.0 if near else p.get("far_k", 1.0))
        return super().step()


class Rest(Circuit):
    """Spend, for scarce: nothing seen for rest_after s, it rests rest_len s, firing nothing; an eye's pulse ends the rest."""

    seen_at, until = 0.0, -1.0

    def stimulate(self, sensor, at):
        self.seen_at, self.until = self.t, -1.0
        super().stimulate(sensor, at)

    def step(self):
        p = self.p
        if self.t < self.until:
            super().step()
            return []
        if self.t - self.seen_at > p.get("rest_after", 3.0):
            self.until, self.seen_at = self.t + p.get("rest_len", 3.0), self.t + p.get("rest_len", 3.0)
        return super().step()


ARMS = {"told": Told, "circuit": Circuit, "toldpause": ToldPause, "probe": Probe, "path": PathC, "scanside": ScanSide, "scanlearn": ScanLearn,
        "sweeps": SweepsC, "jitter": JitterC, "filter": Filter, "integrate": Integrate, "adapteye": AdaptEye, "eyehold": EyeHold,
        "autohold": AutoHold, "judgesoon": JudgeSoon, "sweepsg": SweepsG, "jitterg": JitterG, "volatile2": Volatile2, "learnpause2": LearnPause2, "bt": Bt, "sweepsg2": SweepsG2, "jitterg2": JitterG2, "learnpause3": LearnPause3, "unwired": Unwired, "B": B, "toldc": Told, "still": Still, "eyeslow": EyeSlow, "learntrust": LearnTrust, "local": Local, "rest": Rest}


def arms():
    """Every arm, those of the ladder too, by name."""
    return {**Lad.ARMS, **ARMS}


def numbers(seed, kw):
    p, spread = M.from_bench()
    q = dict(M.drawn(p, spread, seed), use=0, trust=1, run_max=1.0)
    for k, v in kw.items():
        if k.endswith("_x"):
            q[k[:-2]] *= v
        else:
            q[k] = v
    return q


def life(job):
    w, arm, kw, seed, seconds, first = job
    told = arm.startswith("told")
    q = numbers(seed, kw)
    if told:
        q["V_H"] = 99.0
    R = WORLDS[w](first)
    R.told = told and arm != "toldc"                    # toldc: told the colour, the mismatch still there
    lf = Life(seed, first, brain=lambda s: arms()[arm](s, q))
    b = lf.brain
    R.setup(lf, seed)
    if hasattr(R, "taste"):                             # (digest) the taste of a meal too soon: bad, whatever its colour
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    ticks = int(round(seconds / TICK))
    labelled = 0
    while lf.t < ticks:
        t = lf.t * TICK
        po = R.poison(t)
        lf.poison, R.now = po, t
        if told:
            tp = R.told_poison(t)
            b.food = lf.sensor[COL[1 - COL.index(tp)]] if tp else b.food
        R.tick(lf, t)
        lf.step()
        while labelled < len(lf.meals):                 # scored by the rule; told the rule of each meal
            tk, c = lf.meals[labelled]
            badm = R.bad(c, t) if hasattr(R, "bad") else c == po
            lf.meals[labelled] = (tk, "red" if badm else "blue")
            R.ate(c)
            labelled += 1
    l = Lived(thirds(lf.meals, lf.moving, ticks, "red"))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.flips = len(getattr(b, "flips", []))
    l.n = getattr(b, "n", None)
    l.grew = list(getattr(b, "grew", []))
    l.on = list(getattr(b, "on_at", []))
    l.x = getattr(b, "x", None)
    l.sweeps = getattr(b, "sweeps", 0)
    l.mode = getattr(b, "mode", None)
    l.weak_food = lf.brain.p.get("bad_eye") == 1 - lf.sensor[first]    # (weak, noisy) the flawed eye is the food's
    return l


def run(w, arm, seeds=HELD, kw=None, seconds=None):
    seconds = seconds or LONG.get(w, 100.0)
    jobs = [(w, arm, kw or {}, s, seconds, c) for s in seeds for c in COL]
    with ProcessPoolExecutor(8) as ex:
        return list(ex.map(life, jobs, chunksize=2))


def line(name, L):
    s = summary(L)
    c = s["ci"]["efficiency"]
    print(f"{name}: efficiency {s['efficiency']:.2f} [{c[0]:.2f}, {c[1]:.2f}]  gain {s['gain']:.2f}  food {s['food']:.2f}  poison {s['poison']:.2f}  "
          f"stranded {s['stranded']:.0%}  firings {s['firings']:.0f}", flush=True)
    return s


def against(L, B, name="against the base brain"):
    d, i = paired(L, B)
    print(f"   {name} {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
    return d, i


# the classes' generic arms: what can be asked of any world
SPACES = {
    "immunise": lambda r: {k + "_x": float(3 ** r.uniform(-1, 1)) for k in ("hold", "bored", "scan", "drive", "run")} | {"run_max": float(r.choice([0.5, 1, 2, 5]))},
    "spend": lambda r: {k + "_x": float(3 ** r.uniform(-1, 0)) for k in ("scan", "drive", "run")},
}


def tune(w, arm, space, n=24, seconds=None, base_kw=None, keep=3):
    """Random settings on training seeds, the best `keep` judged held out against the base brain."""
    r = np.random.default_rng(1)
    base = run(w, "circuit", seconds=seconds)
    line(f"{w} circuit", base)
    res = []
    for _ in range(n):
        kw = dict(base_kw or {}, **SPACES[space](r))
        res.append((efficiency(run(w, arm, TRAIN, kw, seconds)), kw))
    res.sort(key=lambda x: -x[0])
    for e, kw in res[:keep]:
        L = run(w, arm, HELD, kw, seconds)
        line(f"{w} {arm} {space} training {e:.2f} {json.dumps({k: round(v, 3) for k, v in kw.items()})}", L)
        against(L, base)


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args.pop(0)
    seconds, seeds, n = None, HELD, 24
    for flag in ("--seconds", "--seeds", "--n"):
        if flag in args:
            i = args.index(flag)
            v = args[i + 1]
            del args[i:i + 2]
            if flag == "--seconds":
                seconds = float(v)
            elif flag == "--n":
                n = int(v)
            else:
                seeds = range(*(int(x) for x in v.split(":")))
    kw = {a.split("=")[0]: float(a.split("=")[1]) for a in args if "=" in a}
    rest = [a for a in args if "=" not in a]
    if cmd == "gaps":
        for w in rest or WORLDS:
            a = run(w, "circuit", seeds, seconds=seconds)
            line(f"{w}: base brain", a)
            if WORLDS[w]("red").target():
                b = run(w, WORLDS[w]("red").target(), seeds, seconds=seconds)
                line(f"{w}: target", b)
                against(b, a, "gap")
            else:
                print(f"   {w}: no stated target; search gives it", flush=True)
    elif cmd == "judge":
        base = run(rest[0], "circuit", seeds, seconds=seconds)
        L = run(rest[0], rest[1], seeds, kw, seconds)
        line(f"{rest[0]} {rest[1]} {kw}", L)
        against(L, base)
    elif cmd == "tune":
        tune(rest[0], rest[1], rest[2], n, seconds, kw)
