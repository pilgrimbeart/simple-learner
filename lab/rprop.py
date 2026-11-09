"""rprop.py: a balance learner that sizes its own step and wobble from its own evidence (Rprop-like). Main session, 2026-11-08.
Why (discrete/NOTEBOOK.md, D36, the balance speed): the old learner's evidence was enough to balance in about 60-300 drives, but its fixed
step (eta sd^2 f', about .004 a drive) took 1,000+, and its fixed gate made its wobble a random walk in long lives.

The rule, local to the block, knowing nothing of meals or what its wires carry. The block already has, for each drive, its own wobble e
and the drive's outcome against its usual, d (DriveBal). It sums d e and (d e)^2 over drives since its last move:
  - when the sum is z standard errors from 0 (significant), it moves its balance by its step D in the sum's direction; if that direction
    agrees with its last move, D doubles, if not, D halves;
  - when n_max drives pass with nothing significant, D halves and it doesn't move;
  - its wobble's size is its step's, within [sd_min, sd_max]: a block far from right moves and wobbles widely, one at its best quiets,
    and one whose world changes finds agreeing moves again and grows.
DriveBal's own fixed-step update is off (eta 0), and the bank's fixed gate (jit 0).
Numbers chosen generically before any life, none fitted: z 2; D born .3, within [.0125, .8]; wobble within [.05, .4]; n_max 50 drives.
Versions (lab/v/adaptive_predictions.md): v2 n_max infinite (no give-ups); v3 also Dmax .3; v4 v3's Dmax with give-ups that keep the
sums (keep=1): a block with nothing significant to act on quiets, without throwing away what it has seen; v5 (split=1, keep implied)
give-ups halve only the wobble (its share q of the step), the step changing only on moves, and a move restoring the wobble to the step;
v6 (curv=1, with v3's no give-ups and Dmax .3) quiets only when its wobble surely hurts whichever way it goes (the sum of d (e^2 - sd^2)
z standard errors below 0: the mark of standing on a peak), halving its wobble each time; a move restores it; v7 v6 with the wobble's
floor .005; v8 (seq=1) v7 with that test's bar always valid (checked every drive, a false alarm ever only 5% likely).

    from rprop import SZ; adaptive.make(world, seed, first, kw, cls=SZ)"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import rivals as RV

DEFAULTS = dict(z=2.0, D0=0.3, Dmin=0.0125, Dmax=0.8, sd_min=0.05, sd_max=0.4, n_max=50)


class SZ(RV.RV):
    def __init__(self, seed, p):
        p = {**DEFAULTS, **p, "jit": 0, "eta": 0.0}
        super().__init__(seed, p)
        self.D = self.p["D0"]
        self.q = 1.0                                    # v5 (split=1): the wobble's share of the step, halved by give-ups
        self.S1 = self.S2 = 0.0
        self.C1 = self.C2 = 0.0                         # v6 (curv=1): sums of d (e^2 - sd^2) and its square: does the wobble hurt either way?
        self.n, self.dirn = 0, 0
        self.moves = []                                 # watching: (t, x, D) at each move or give-up
        self._wobble()

    def _wobble(self):
        p = self.p
        p["sd"] = float(np.clip(self.D * self.q, p["sd_min"], p["sd_max"]))

    def step(self):
        n0, b0 = self.drives, self.b
        out = super().step()
        if self.drives > n0 and b0 is not None:
            p = self.p
            de = (self.pulses - b0) * self.e
            self.S1, self.S2, self.n = self.S1 + de, self.S2 + de * de, self.n + 1
            if p.get("curv"):                           # v6: a wobble that hurts whichever way it goes means the block is at its best
                dc = (self.pulses - b0) * (self.e ** 2 - p["sd"] ** 2)
                self.C1, self.C2 = self.C1 + dc, self.C2 + dc * dc
                self.nc = getattr(self, "nc", 0) + 1
                if p.get("seq"):                        # v8: an always-valid bar (Robbins' normal mixture, chance alpha .05 of ever
                    rho = 10.0 * self.C2 / self.nc       # crossing by luck however often it is checked; its scale ten drives' worth)
                    bar = np.sqrt((self.C2 + rho) * (np.log((self.C2 + rho) / rho) + 2.0 * np.log(20.0))) if self.C2 > 0 else np.inf
                else:
                    bar = p["z"] * np.sqrt(self.C2)
                if self.C2 > 0 and self.C1 < -bar:
                    self.q *= 0.5
                    self.C1 = self.C2 = 0.0
                    self.nc = 0
                    self.moves.append((self.t, self.x, self.D * self.q))
                    self._wobble()
            s = int(np.sign(self.S1))
            if self.S2 > 0 and abs(self.S1) > p["z"] * np.sqrt(self.S2):
                self.x = float(np.clip(self.x + s * self.D, -1.4, 1.4))
                k = 1.0 if self.dirn == 0 else 2.0 if s == self.dirn else 0.5     # the first move: no direction to agree with
                self.D = float(np.clip(self.D * k, p["Dmin"], p["Dmax"]))
                self.dirn = s
                self.q = 1.0
                self.C1 = self.C2 = 0.0
                self.nc = 0
            elif self.n >= p["n_max"] and p.get("split"):  # v5: a give-up halves the wobble only; the step waits for evidence
                self.q *= 0.5
                self.n = 0
                self.moves.append((self.t, self.x, self.D * self.q))
                self._wobble()
                return out
            elif self.n >= p["n_max"]:
                self.D = max(self.D * 0.5, p["Dmin"])
                if p.get("keep"):                       # keep=1 (v4): a give-up quiets the wobble but keeps the evidence
                    self.n = 0
                    self.moves.append((self.t, self.x, self.D))
                    self._wobble()
                    return out
            else:
                return out
            self.S1 = self.S2 = 0.0
            self.n = 0
            self.moves.append((self.t, self.x, self.D))
            self._wobble()
            self._set(self.x)
        return out
