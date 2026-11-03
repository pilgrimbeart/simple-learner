"""story2_bias.py: errors in the balance towards the scan's far side cost little (D26), so a coarse estimate might aim there.
Sweeps by counters, the learned balance shifted by `bias`, training seeds 0-31 x 2, 2,000 s (lab/story2_stage3.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import story2_stage3 as S
from story2 import line


class Biased(S.Sweeps):
    def step(self):
        out = super().step()
        if self.x != getattr(self, "shown", 0.0):
            self.shown = self.x
            x = self.x + self.p.get("bias", 0.0)
            self.p["g0"], self.p["g1"] = float(np.exp(x / 2)), float(np.exp(-x / 2))
        return out


S.Sweeps = Biased
if __name__ == "__main__":
    T = range(0, 32)
    for K in (32, 64):
        for b in (0.0, -0.03, -0.06, -0.1):
            kw = dict(S.SWEEPS, bank=float(K), local=1.0, binary=1.0, cap=3.0, bias=b)
            L = S.run("sweeps", T, kw, seconds=2000.0)
            line(f"{K} counters, bias {b}", L)
