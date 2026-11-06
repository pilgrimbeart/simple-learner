"""seconds.py: the brains in seconds (stage 2c), as subclasses; discrete/model.py, lab/universal_v.py and their bases are untouched.

`seconds_cls(cls)` puts SecondsModel just above discrete.model.Model in any brain class built on it (the base circuit, the bank, the told
arm, the reference), so every layer above keeps its own logic and the block model below it works in seconds:
  - each pulse kept with its moment (stimulate's `at`), not just counted in its tick;
  - the drive, run and scan decided at each moment: a food pulse starts a drive at its moment, a poison pulse ends it at its moment, the
    hold and boredom end at their exact times;
  - each oscillator's beats at the moments its phase crosses a whole number, under the state at that moment; a drive's lone beat at the
    drive's start (`lone`); all returned with their moments in `beats` [(motor, moment within the tick)], which sim.WLife fires there.
  - a taste's moment: the class's whole taste runs with the brain's clock set to the taste's moment (the engine passes it relative to the
    end of the tick the brain has just stepped through).
  - a layer above that rewrote `seen` this tick (the bank's pause zeroes it; its open phase gives every pulse to one eye) is honoured: the
    moments are kept and the eyes reassigned as `seen` says.
What stays counted once a tick, as the limit of halving the step: the brain's decision to step at all (its outputs for a tick are made at
the tick's start, before the tick's tastes arrive; a taste acts from the next tick); the bank's slow nodes, decayed by 1 - TICK/tau a tick
(first order in seconds, error O(TICK/tau), tau >= 30 s). The partner beat "a tick late" (D24) belongs to the split-eye brain, which no arm
here uses: the base circuit's and the bank's two motors beat together (equal rates) or each on its own oscillator.

`RefS`: the reference with its clock re-read every 50 ms of time, not every 5 ticks (at 10 ms the same moments)."""
from __future__ import annotations

import math
import sys

sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
import units
from units import TICK  # noqa: F401  (stage2_checks.set_tick rewrites this module's TICK with every other's)

_CACHE = {}


def _tick():
    return sys.modules[__name__].TICK


class SecondsModel(M.Model):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self._ev = []                                   # (moment, sensor) of this tick's pulses
        self.beats = []

    def stimulate(self, sensor, at):
        self._ev.append((self.t + at, sensor))
        super().stimulate(sensor, at)                   # (counts seen, as Model)

    def _events(self):
        """This tick's pulses as the layers above left `seen`."""
        ev = sorted(self._ev)
        self._ev = []
        want = list(self.seen)
        have = [sum(1 for _, k in ev if k == s) for s in (0, 1)]
        if want == have:
            return ev
        if sum(want) == 0:
            return []
        if sum(want) == len(ev) and 0 in want:          # all to one eye (the open phase)
            k = 0 if want[0] else 1
            return [(t, k) for t, _ in ev]
        out = []
        for s in (0, 1):                                # otherwise keep the last want[s] of each eye's own
            mine = [e for e in ev if e[1] == s]
            out += mine[len(mine) - want[s]:] if want[s] <= len(mine) else mine
        return sorted(out)

    def step(self):
        p = self.p
        dt = _tick()
        t0 = self.t
        t1 = t0 + dt
        ev = self._events()
        self.seen = [0, 0]
        out, beats = [], []
        lone_frac = p["lone"]
        hold, bored = p["hold"], p["bored"]
        self.dq = max(0.0, self.dq - p["drift"] * dt)
        last = {0: None, 1: None}
        i = 0
        cur = t0
        while True:
            while i < len(ev) and ev[i][0] <= cur + 1e-15:     # pulses at this moment (a pulse given before the step: at the tick's start)
                tau, s = ev[i]
                tau = max(tau, t0)
                if s == self.food:
                    self.last_drive = self.last_food = tau
                else:
                    self.last_drive = -1e9
                last[s] = tau
                i += 1
            driving = cur - self.last_drive < hold
            running = not driving and cur - self.last_food > bored
            on = driving or running
            if on and not self.was_on:
                if lone_frac and driving and self.phase < lone_frac:
                    out.append(1)
                    beats.append((1, cur - t0))
                if p.get("sync"):
                    self.phase1 = self.phase
            self.was_on = on
            # the next moment the state can change: a pulse, the hold's end, boredom's start
            nxt = [t1]
            if i < len(ev):
                nxt.append(max(ev[i][0], cur))
            if driving:
                nxt.append(self.last_drive + hold)
            elif not running:
                nxt.append(self.last_food + bored + 1e-12)
            b = max(cur, min(nxt))
            if b <= cur and b < t1:
                b = min(t1, cur + 1e-9)
            r = p["drive"] if driving else p["run"] if running else p["scan"]
            self._beat(r, on, cur, b, t0, out, beats)
            cur = b
            if cur >= t1 - 1e-15 and i >= len(ev):
                break
        if hasattr(self, "last"):                       # Watched's "this eye pulsed just now", at the pulse's moment
            for s in (0, 1):
                if last[s] is not None:
                    self.last[s] = last[s]
        self.t = t1
        self.beats = beats
        return out

    def _beat(self, r, on, a, b, t0, out, beats):
        """The oscillators from a to b at rate r: beats at their crossing moments (Model.step's three cases, in time)."""
        p = self.p
        g0, g1 = p["g0"], p["g1"]
        span = b - a
        if span <= 0:
            return
        if p.get("paired") and g1 != g0 and on:
            hi = max(g0, g1)
            w = r * hi
            for tau in _crossings(self.phase, w, a, span):
                self.phase1 += min(g0, g1) / hi
                if self.phase1 >= 1:
                    self.phase1 -= 1
                    out += [0, 1]
                    beats += [(0, tau - t0), (1, tau - t0)]
                else:
                    m = 0 if g0 > g1 else 1
                    out.append(m)
                    beats.append((m, tau - t0))
            self.phase = (self.phase + w * span) % 1.0
            return
        w = r * g0
        ts = _crossings(self.phase, w, a, span)
        self.phase = (self.phase + w * span) % 1.0
        if not on:
            out += [0] * len(ts)
            beats += [(0, tau - t0) for tau in ts]
            return
        if g1 == g0:
            for tau in ts:
                out += [0, 1]
                beats += [(0, tau - t0), (1, tau - t0)]
            return
        w1 = r * g1
        ts1 = _crossings(self.phase1, w1, a, span)
        self.phase1 = (self.phase1 + w1 * span) % 1.0
        out += [0] * len(ts) + [1] * len(ts1)
        beats += [(0, tau - t0) for tau in ts] + [(1, tau - t0) for tau in ts1]


def _crossings(phase, w, a, span):
    """Moments in (a, a + span] when phase + w (t - a) passes a whole number."""
    if w <= 0:
        return []
    n = int(math.floor(phase + w * span))
    return [a + (k - phase) / w for k in range(1, n + 1)]


def _timed_taste(cls):
    base = cls.taste

    def taste(self, value, at):
        t = self.t
        self.t = t + at                                 # the taste's own moment, for every layer's clock
        try:
            return base(self, value, at)
        finally:
            self.t = t
    return taste


def _matched_step(cls):
    base = cls.step

    def step(self):
        out = base(self)
        bt = list(getattr(self, "beats", []))
        if sorted(out) != sorted(m for m, _ in bt):     # a layer above filtered the beats (a pause): keep the moments of those left
            keep = []
            for m in out:
                j = next((j for j, (mm, _) in enumerate(bt) if mm == m), None)
                keep.append(bt.pop(j) if j is not None else (m, 0.0))
            self.beats = keep
        return out
    return step


def seconds_cls(cls):
    """cls with the block model below it in seconds, its tastes at their moments, its beats with theirs."""
    if cls in _CACHE:
        return _CACHE[cls]
    if not issubclass(cls, M.Model):
        _CACHE[cls] = cls
        return cls
    S = type(cls.__name__ + "S", (cls, SecondsModel), {})
    S.taste = _timed_taste(S)
    S.step = _matched_step(S)
    _CACHE[cls] = S
    return S


def ref_seconds():
    """The reference with its clock re-read every 50 ms of time (lab/stage2b_reference.py re-read it every 5 ticks)."""
    from stage2b_reference import Ref
    import stage1c_arms as A

    class RefS(Ref):
        CLOCK = 0.05

        def step(self):
            self.nticks += 1
            dt = _tick()
            t0 = self.t
            if self.timed and not self.open and math.floor((t0 + dt) / self.CLOCK + 1e-9) > math.floor(t0 / self.CLOCK + 1e-9):
                self.decide(self.food)
            return A.B.Recorder.step(self)
    return RefS
