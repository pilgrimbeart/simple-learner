"""Watch the split eye's steer live (split.py): python watch_split.py [--seed N] [--told] [--record DIR --seconds S]
The panel: the map learned (which motor turns towards which half) against the truth, each half's food pulses in the
last 0.2 s, and each steer as it happens."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import argparse
import numpy as np
import creature
from discrete import model as M
import split as SP

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=50192)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=100.0)
ap.add_argument("--told", action="store_true", help="the map told, not learned")
ap.add_argument("--nosteer", action="store_true", help="B, for comparison")
a = ap.parse_args()
D = dict(W=0.2, N=1, Q=1, reset=1, lag=1, map="oracle" if a.told else "learn", gap=0.1, steer=0 if a.nosteer else 1)


class Shown(SP.SplitB):
    def stage(self):
        return "waiting"

    def built(self):
        return True

    def drive(self, sensor):
        return 1.0 if sensor == self.food else 0.0

    def draw(self, screen, side, font, sensors, motors, lit):
        screen.fill((20, 24, 28))
        n = [sum(1 for t, hh in self.recent if hh == k and t > self.t - 0.2) for k in (0, 1)]
        name = {self.toward[0]: "eye half 0", self.toward[1]: "eye half 1"}
        if self.k == 0:
            learned = "not yet"
        else:
            m0 = 0 if self.k > 0 else 1                 # the motor learned to turn towards half 0
            ok = "RIGHT" if m0 == self.toward[0] else "wrong"
            learned = f"motor {m0} -> half 0, motor {1 - m0} -> half 1   ({ok})"
        driving = self.t - self.last_drive < self.p["hold"]
        since = self.t - getattr(self, "last_steer", -1e9)
        lines = [f"t {self.t:7.1f} s   steers {self.steers}",
                 "DRIVING" if driving else "scanning (motor 0)", "",
                 f"truth: motor {self.toward[0]} turns towards half 0",
                 f"map ({'told' if a.told else 'learned'}): {learned}   counter {self.k:+.0f}", "",
                 "food pulses in the last 0.2 s:",
                 f"  half 0  {'#' * n[0]:<8} {n[0]}",
                 f"  half 1  {'#' * n[1]:<8} {n[1]}", "",
                 (f">>> STEER towards half {self.last_h} (motor {self.motor_for(self.last_h)})" if since < 0.15 else "")]
        for i, ln in enumerate(lines):
            screen.blit(font.render(ln, True, (240, 228, 66) if ln.startswith(">>>") else (230, 230, 230)), (8, 8 + 20 * i))


p, spread = M.from_bench()
_init = creature.Life.__init__


def _life(self, seed=0, poison="red", *args, brain=None, **k):
    _init(self, seed, poison, *args, brain=lambda s: None, **k)
    r = np.random.default_rng(seed + 5_500_007)
    self.hw = (0, 1)[:: r.choice((1, -1))]
    self.hr = r
    q = M.drawn(p, spread, seed); q["V_H"] = 99.0
    br = Shown(seed, q, D)
    br.food = self.sensor[next(c for c in self.sensor if c != poison)]
    br.toward = {self.hw[0]: self.motor["right"], self.hw[1]: self.motor["left"]}
    self.brain = br


creature.Life.__init__ = _life
creature.Life.step = SP.SplitLife.step
creature.BRAINS["split"] = lambda s: None
creature.watch(a.seed, "split", a.record, a.seconds, False)
