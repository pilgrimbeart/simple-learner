"""drift_filter.py: the ideal learner for volatile reversals with false tastes, run online inside a life (2026-11-16, D69): a mixture over
flip rate x false-taste rate of two-state forward filters (which colour is poison), updated at each meal from the meals so far. Used by
the yardstick arm vfilt (stage2_lang/arms.py): the told brain's body steered by this belief instead of the truth."""
import math

import numpy as np

H = np.exp(np.linspace(np.log(10.0), np.log(640.0), 8))
Q = np.linspace(0.0, 0.45, 8)


class Filter:
    def __init__(self):
        hs, qs = np.meshgrid(H, Q, indexing="ij")
        self.hs, self.qs = hs.ravel(), np.clip(qs.ravel(), 0.01, None)
        self.post = np.full((len(self.hs), 2), 0.5)
        self.logw = np.zeros(len(self.hs))
        self.tl = None

    def meal(self, t, c, pois):
        if self.tl is not None:
            p = 0.5 * (1 - np.exp(-2 * (t - self.tl) / self.hs))
            self.post = self.post * (1 - p)[:, None] + self.post[:, ::-1] * p[:, None]
        self.tl = t
        lik = np.empty((len(self.hs), 2))
        for s in (0, 1):
            pp = np.where(c == s, 1 - self.qs, self.qs)
            lik[:, s] = pp if pois else 1 - pp
        pred = (self.post * lik).sum(1)
        self.logw += np.log(pred)
        self.post = self.post * lik / pred[:, None]

    def p_poison(self, t):
        """P(each colour is poison now), the flips since the last meal allowed for."""
        post = self.post
        if self.tl is not None:
            p = 0.5 * (1 - np.exp(-2 * (t - self.tl) / self.hs))
            post = post * (1 - p)[:, None] + post[:, ::-1] * p[:, None]
        w = np.exp(self.logw - self.logw.max())
        v = (w[:, None] * post).sum(0)
        return v / v.sum()

    def poison(self, t):
        """The colour (0 red, 1 blue) more likely poison now, the flips since the last meal allowed for."""
        post = self.post
        if self.tl is not None:
            p = 0.5 * (1 - np.exp(-2 * (t - self.tl) / self.hs))
            post = post * (1 - p)[:, None] + post[:, ::-1] * p[:, None]
        w = np.exp(self.logw - self.logw.max())
        return int((w[:, None] * post).sum(0).argmax())
