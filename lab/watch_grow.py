"""Watch case 1's grower live (D17): python watch_grow.py [--seed N] [--record DIR --seconds S]"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import argparse
import creature
from discrete import model as M
from grow import OPS, Grow



class Shown(Grow):
    """The grower with the live view's hooks: its panel lists, per eye, the pathway's operation, the prediction of what
    follows the eye, the frustration, and the recruit's trials."""

    def built(self):
        return True

    def stage(self):
        return "scanning"

    def draw(self, screen, side, font, sensors, motors, lit):
        screen.fill((20, 24, 28))
        lines = [f"t {self.t:6.1f} s"]
        for k in (0, 1):
            r = self.recruit[k]
            tried = "" if r is None else "  tried " + ", ".join(f"{OPS[i]} {v:+.2f}" for i, v in r["score"].items())
            lines += [f"eye {k}: {self.op[k]:8s} predicts {self.pred[k]:+.2f}  frustration {self.fr[k]:.1f}",
                      "        " + ("no recruit" if r is None else f"recruit trying {OPS[r['i']]}") + tried]
        lines += [""] + [f"{t:6.1f} s  {e}" for t, e in self.events[-6:]]
        for i, ln in enumerate(lines):
            screen.blit(font.render(ln, True, (230, 230, 230)), (8, 8 + 20 * i))


p, spread = M.from_bench()
creature.BRAINS["grower"] = lambda seed: Shown(seed, dict(M.drawn(p, spread, seed), all=1))
ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=50000)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=100.0)
a = ap.parse_args()
creature.watch(a.seed, "grower", a.record, a.seconds, False)
