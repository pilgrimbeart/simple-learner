"""Watch the pilot story's circuit live (lab/story1.py, Gated): python lab/watch_story1.py [--seed N] [--record DIR --seconds S]
Doubt is written only while a drive is on. The panel: the bit, right or wrong (watching only), the tally, each vouched
taste as it comes, and the flips. The first life has blue as poison; seed 50206 is born wrong then, and flips at 0.7 s."""
import argparse
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import creature
from story1 import Gated, M


class Shown(Gated):
    eye = None                                          # watching: the poison eye
    vouched_n = ignored_n = 0

    def built(self):
        return True

    def stage(self):
        return "learning" if self.eye is not None and self.food == self.eye else "bit right"

    def taste(self, value, at):
        if self.vouched():
            self.vouched_n += 1
        else:
            self.ignored_n += 1
        super().taste(value, at)

    def draw(self, screen, side, font, sensors, motors, lit):
        screen.fill((20, 24, 28))
        right = self.eye is not None and self.food != self.eye
        lines = [f"t {self.t:6.1f} s", "", f"following eye {self.food}: " + ("RIGHT (the food eye)" if right else "WRONG (the poison eye)"),
                 f"tally {self.L:+d}  (+1 flips; a food steps down, at most to -{int(self.p['trust'])})",
                 "driving: a taste counts" if self.vouched() else "not driving: a taste is ignored", "",
                 f"tastes counted {self.vouched_n}, ignored {self.ignored_n}",
                 "flips at " + (", ".join(f"{x:.1f} s" for x in self.flips) or "none yet")]
        for i, ln in enumerate(lines):
            screen.blit(font.render(ln, True, (230, 230, 230)), (8, 8 + 20 * i))


p, spread = M.from_bench()
creature.BRAINS["story1"] = lambda seed: Shown(seed, dict(M.drawn(p, spread, seed), use=0, trust=1))
_init = creature.Life.__init__


def _life(self, seed=0, *args, **k):
    _init(self, seed, *args, **k)
    if isinstance(self.brain, Shown) and self.poison in self.sensor:
        self.brain.eye = self.sensor[self.poison]


creature.Life.__init__ = _life
ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=50206)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=100.0)
a = ap.parse_args()
creature.watch(a.seed, "story1", a.record, a.seconds, False)
