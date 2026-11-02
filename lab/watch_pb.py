"""Watch D20's period learner live on a lopsided body: python watch_pb.py [--seed N] [--standard] [--record DIR --seconds S]
The panel: sweeping or not and with which motor, each motor's period found against the one its thruster gives, the
balance learned against the one it needs, and the intervals counted."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import argparse
import math
import numpy as np
import creature
import world as W
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
from periodbal import PeriodBal

SETTINGS = dict(cal_every=32.0, cal_len=8.0, stall=0.05, stall_need=3000.0, gate=8.0, gate_rate=1.0, cal_first=0.0,
                cal_fast=12.0, sync=1.0)   # D20's, held out


class Shown(PeriodBal):
    right = None                                        # watching: the balance this body needs, and each period
    periods = None

    def built(self):
        return True

    def stage(self):
        return "sweeping" if self.t < self.cal_until else "foraging"

    def draw(self, screen, side, font, sensors, motors, lit):
        screen.fill((20, 24, 28))
        T = ["-" if v is None else f"{v:.2f} s" for v in self.T]
        lines = [f"t {self.t:7.1f} s   sweeps {self.sweeps}" + ("   (stopped: estimate stalled)" if self.stalled else ""),
                 (f"SWEEPING with motor {self.sm}" if self.t < self.cal_until else "foraging (B)"), "",
                 "period found (what comes round again):",
                 f"  motor 0 {T[0]:>8}   ({self.periods[0]:.2f} s its thruster gives)" if self.periods else f"  motor 0 {T[0]}",
                 f"  motor 1 {T[1]:>8}   ({self.periods[1]:.2f} s its thruster gives)" if self.periods else f"  motor 1 {T[1]}",
                 f"intervals counted {self.n[0]}, {self.n[1]}",
                 f"meals in the last 32 s of foraging {len(self.mt)} (a sweep only below {self.p['gate']:g})" if self.p.get("gate") else "", "",
                 f"balance learned  {self.x:+.2f}",
                 f"balance it needs {self.right:+.2f}" if self.right is not None else "",
                 "(log of motor 0's rate over motor 1's)"]
        for i, ln in enumerate(lines):
            screen.blit(font.render(ln, True, (230, 230, 230)), (8, 8 + 20 * i))


p, spread = M.from_bench()
creature.BRAINS["periodbal"] = lambda seed: Shown(seed, dict(M.drawn(p, spread, seed), **SETTINGS))
_init = creature.Life.__init__


def _life(self, seed=0, *args, **k):                       # the lopsided body, as periodbal.life draws it
    _init(self, seed, *args, **k)
    if isinstance(self.brain, Shown) and not a.standard:
        f = draw(seed, THRUSTERS)
        vary(self, f)
        thr = {m: t for t, m in self.motor.items()}
        self.brain.right = float(np.log(f[thr[1]] / f[thr[0]]))
        self.brain.periods = [0.79 * 2 * math.pi * W.DRAG / (self.brain.p["scan"] * f[thr[m]] * W.TURN) for m in (0, 1)]


creature.Life.__init__ = _life
ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=50000)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=900.0)
ap.add_argument("--standard", action="store_true", help="the standard body (no sweeps expected: it drives well)")
a = ap.parse_args()
creature.watch(a.seed, "periodbal", a.record, a.seconds, False)
