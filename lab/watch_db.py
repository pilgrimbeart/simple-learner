"""Watch D19's per-drive balance learner live on a lopsided body: python watch_db.py [--seed N] [--record DIR --seconds S]
The panel: the balance it has learned against the one it should have (told its body), each drive's jitter and outcome."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import argparse
import numpy as np
import creature
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
from drivebal import DriveBal


class Shown(DriveBal):
    right = None                                        # the oracle's balance, set once the body is known (watching)

    def built(self):
        return True

    def stage(self):
        return "driving" if self.was_driving else "scanning"

    def step(self):
        d0 = self.drives
        out = super().step()
        if self.drives > d0:
            self.log = (getattr(self, "log", []) + [(self.t, self.e, self.pulses, self.b)])[-8:]
        return out

    def draw(self, screen, side, font, sensors, motors, lit):
        screen.fill((20, 24, 28))
        lines = [f"t {self.t:7.1f} s   drives {self.drives}",
                 f"balance learned  {self.x:+.2f}",
                 f"balance it needs {self.right:+.2f}" if self.right is not None else "",
                 f"(log of motor 0's rate over motor 1's)",
                 f"jitter now {self.e:+.2f}" + ("   driving" if self.was_driving else ""), "",
                 "last drives: jitter, food pulses seen, usual"]
        lines += [f"  {t:7.1f} s  {e:+.2f}  {n:3d}  {b:5.1f}" for t, e, n, b in getattr(self, "log", [])]
        for i, ln in enumerate(lines):
            screen.blit(font.render(ln, True, (230, 230, 230)), (8, 8 + 20 * i))


p, spread = M.from_bench()
creature.BRAINS["drivebal"] = lambda seed: Shown(seed, dict(M.drawn(p, spread, seed), eta=0.03, N=1000.0))
_init = creature.Life.__init__


def _life(self, seed=0, *a, **k):                       # the lopsided body, as drivebal.life draws it
    _init(self, seed, *a, **k)
    if isinstance(self.brain, Shown):
        f = draw(seed, THRUSTERS)
        vary(self, f)
        thr = {m: t for t, m in self.motor.items()}
        self.brain.right = float(np.log(f[thr[1]] / f[thr[0]]))


creature.Life.__init__ = _life
ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=50000)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=300.0)
a = ap.parse_args()
creature.watch(a.seed, "drivebal", a.record, a.seconds, False)
