"""adaptive.py: the bank's jitter gate replaced by rules a block keeps for itself (the user, 2026-11-08: "the right way to think, proceed").
Main session, 2026-11-08. The fault it replaces (discrete/NOTEBOOK.md, D36): the balance learner's wobble switched on below a fixed 15 good
tastes per 32 s, a rate the body happens to supply; in long lives it ratchets on and costs .4.

Two rules, neither knowing what its wire carries:
  1. A block compares its input only with its own past: a fast and a slow leaky average of the signed pulses on its wire (here the taste
     wire, +1 and -1), and it reacts when the fast one is below the slow one by more than counting noise allows (z standard errors). Here
     that re-arms the wobble.
  2. A block that wobbles keeps wobbling only while its wobble pays: after each drive the balance learner already has its own wobble e and
     the drive's outcome against its usual, d; the block keeps leaky averages of d e and (d e)^2 over its drives, and its wobble's size a
     (0..1, times the learner's own sd) moves towards 1 while the mean of d e is z standard errors from 0, towards 0 otherwise.
  3. A block that learns by trial commits the average of its trials since it was armed, not the last one (Polyak averaging): drift by
     chance averages back towards where it began, a real pull moves the average. Here the balance learner's gains centre on its
     iterate x while it explores and on the average as its wobble quiets (avg=1). Tried and failed: a walk without a restoring force
     averages to a walk (lab/v/adaptive_x2.log).
  3'. A block that learns by trial keeps a change only if the evidence for it is significant (the sum of d e since it was armed, z
     standard errors from 0), and otherwise returns to where it began (avg=2).
Born exploring (a = a0). The numbers are mine and generic, none fitted to a body: z = 2 (two standard errors), the averages' windows in
the block's own events (drives) or seconds (tau_f, tau_s), and the wobble's rate of change (n_a drives).

    from adaptive import AV; rivals.make(world, seed, first, kw, cls=AV)   (uncompiled: fast.py compiles only the steps it copies)"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import rivals as RV

DEFAULTS = dict(avg=1, rearm=1, z=2.0, a0=1.0, n_a=100.0, n_z=200.0, tau_f=100.0, tau_s=1000.0)


class AV(RV.RV):
    def __init__(self, seed, p):
        p = {**DEFAULTS, **p, "jit": 0}                 # U's fixed gate off: this block sets the wobble
        super().__init__(seed, p)
        self.a = self.p["a0"]
        self.m1 = self.m2 = 0.0                         # leaky mean of d e and of (d e)^2 over drives
        self.nz = 0.0                                   # drives counted into them (saturating at n_z)
        self.rf = self.rs = self.vf = 0.0               # fast and slow leaky rates of the signed taste; fast rate of all tastes
        self.tl, self.low = 0.0, False
        self.rearms = []
        self.alog = []
        self.x0, self.S1, self.S2 = 0.0, 0.0, 0.0       # rule 3 (avg=2): where the trials began; the sums of d e and (d e)^2 since
        self.xbar, self.nx = 0.0, 0                     # rule 3 (avg=1): the average of the trials since the wobble was (re)armed
        self._wobble()

    def _set(self, v):
        """DriveBal sets its gains at x (+ its wobble e); with rule 3 they centre on a x + (1 - a) xbar: the iterate while it explores,
        the trials' average as it quiets."""
        if self.p.get("avg") == 1 and hasattr(self, "nx"):
            v = v - self.x + self.a * self.x + (1.0 - self.a) * self.xbar
        elif self.p.get("avg") == 2 and hasattr(self, "S1"):
            sig = abs(self.S1) > self.p["z"] * np.sqrt(max(self.S2, 1e-12))
            v = v - self.x + self.a * self.x + (1.0 - self.a) * (self.x if sig else self.x0)
        super()._set(v)

    def _wobble(self):
        self.p["sd"] = self.sd0 * self.a

    # rule 2: per drive
    def step(self):
        n0, b0 = self.drives, self.b
        out = super().step()
        if self.drives > n0:
            self.nx += 1
            self.xbar += (self.x - self.xbar) / self.nx
        if self.drives > n0 and b0 is not None:
            p = self.p
            y = self.pulses if p.get("out", 0) == 0 else self.t - self.start
            d = (y - b0) / max(b0, 1.0) if p.get("rel") else y - b0
            de = d * self.e
            self.S1, self.S2 = self.S1 + de, self.S2 + de * de
            self.nz = min(self.nz + 1.0, p["n_z"])
            k = 1.0 / self.nz
            self.m1 += (de - self.m1) * k
            self.m2 += (de * de - self.m2) * k
            var = max(self.m2 - self.m1 ** 2, 1e-12)
            pays = abs(self.m1) > p["z"] * np.sqrt(var / self.nz)
            self.a += ((1.0 if pays else 0.0) - self.a) / p["n_a"]
            self._wobble()
            self._set(self.x)
            if not self.alog or self.t - self.alog[-1][0] >= 100.0:
                self.alog.append((self.t, self.a))
        return out

    # rule 1: per taste
    def taste(self, value, at):
        if value and self.p["rearm"]:
            p = self.p
            dt = self.t - self.tl
            self.tl = self.t
            ef, es = np.exp(-dt / p["tau_f"]), np.exp(-dt / p["tau_s"])
            self.rf = self.rf * ef + value / p["tau_f"]
            self.rs = self.rs * es + value / p["tau_s"]
            self.vf = self.vf * ef + 1.0 / p["tau_f"]
            low = self.t > p["tau_f"] and self.rf < self.rs - p["z"] * np.sqrt(self.vf / (2.0 * p["tau_f"]))
            if low and not self.low:                    # on the change only: a stretch that stays low re-arms once
                self.rearms.append(self.t)
                self.a, self.nz, self.m1, self.m2 = 1.0, 0.0, 0.0, 0.0
                if self.p.get("avg") == 2 and not abs(self.S1) > self.p["z"] * np.sqrt(max(self.S2, 1e-12)):
                    self.x = self.x0                            # the last trials' change not significant: undone
                self.x0, self.S1, self.S2 = self.x, 0.0, 0.0
                self.x, self.nx = (self.xbar if self.p.get("avg") == 1 else self.x), 0
                self._wobble()
            self.low = low
        super().taste(value, at)


def make(world, seed, first, kw=None, cls=AV):
    """An AV life, uncompiled, in seconds (rivals.make compiles, and fast.py refuses a step it doesn't copy)."""
    import table as T
    from stage2_lang import arms as S, seconds as SEC
    from stage2_lang.sim import WLife
    q = T.numbers(seed, {**S.V7, **(kw or {})})
    C = SEC.seconds_cls(cls)
    return WLife(seed, first, (lambda s: C(s, q)), world, seconds=True)
