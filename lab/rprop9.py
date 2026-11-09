"""rprop9.py: the sized balance learner v9, kept apart from lab/rprop.py because a queued job imports that one. Main session, night of
2026-11-08.
Why: v7 in plain at 10,000 s (lab/v/rprop_fresh7.log, its traces): 2 of 20 lives sit at x = +-.3 for 100 s or more in the last third.
Its step D is born .3 and in plain nothing ever halves it (no agreeing or reversing moves), and its move test (two standard errors,
checked after every drive) fires by chance eventually however long it waits: one chance move costs a full .3 on plain's sharp peak.
Two fixes, each a local rule, tried as two arms:
  seqm=1   (v9a) the move test's bar always valid (Robbins' normal mixture, as v8's peak test): a chance move ever only 5% likely.
  peakD=1  (v9b, with seqm) the peak's mark halves the step as well as the wobble: a block that finds itself on a peak shrinks both.
The peak test keeps v7's two-standard-error bar (v8's always-valid one there quieted plain too slowly).

    from rprop9 import SZ9; adaptive.make(world, seed, first, kw, cls=SZ9)"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import rprop as RP


def avbar(s2, n, alpha=0.05):
    """Robbins' normal-mixture bar on a running sum with variance s2 after n drives; its scale ten drives' worth."""
    if s2 <= 0:
        return np.inf
    rho = 10.0 * s2 / n
    return np.sqrt((s2 + rho) * (np.log((s2 + rho) / rho) + 2.0 * np.log(1.0 / alpha)))


class SZ9(RP.SZ):
    def step(self):
        n0, b0 = self.drives, self.b
        out = RP.RV.RV.step(self)
        if not (self.drives > n0 and b0 is not None):
            return out
        p = self.p
        de = (self.pulses - b0) * self.e
        self.S1, self.S2, self.n = self.S1 + de, self.S2 + de * de, self.n + 1
        dc = (self.pulses - b0) * (self.e ** 2 - p["sd"] ** 2)
        self.C1, self.C2 = self.C1 + dc, self.C2 + dc * dc
        if self.C2 > 0 and self.C1 < -p["z"] * np.sqrt(self.C2):           # the peak's mark
            self.q *= 0.5
            if p.get("peakD"):
                self.D = max(self.D * 0.5, p["Dmin"])
            self.C1 = self.C2 = 0.0
            self.moves.append((self.t, self.x, self.D * self.q))
            self._wobble()
        bar = avbar(self.S2, self.n) if p.get("seqm") else p["z"] * np.sqrt(self.S2)
        if self.S2 > 0 and abs(self.S1) > bar:
            s = int(np.sign(self.S1))
            self.x = float(np.clip(self.x + s * self.D, -1.4, 1.4))
            k = 1.0 if self.dirn == 0 else 2.0 if s == self.dirn else 0.5
            self.D = float(np.clip(self.D * k, p["Dmin"], p["Dmax"]))
            self.dirn = s
            self.q = 1.0
            self.C1 = self.C2 = 0.0
            self.S1 = self.S2 = 0.0
            self.n = 0
            self.moves.append((self.t, self.x, self.D))
            self._wobble()
            self._set(self.x)
        return out
