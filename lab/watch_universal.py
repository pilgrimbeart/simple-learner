"""Watch the bank of predictors live in any world: python lab/watch_universal.py WORLD [--seed N] [--record DIR --seconds S] [k=v ...]
WORLD: plain, thrusters, swap10, alternate, pattern, digest, noisy, unreliable, ageing, weak, patchy, a combination such as digest+alternate. The panel: each model
with its evidence, the one followed, the pause (lab/universal_v.py; discrete/NOTEBOOK.md, D29)."""
import argparse
import json
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner"]
import blocks                           # the project's, loaded now: lab/blocks.py, a one-off SPICE bench, would otherwise shadow it when creature.watch asks
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
ap = argparse.ArgumentParser()
ap.add_argument("world")
ap.add_argument("--seed", type=int, default=56000)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=100.0)
a, more = ap.parse_known_args()
sys.argv = sys.argv[:1]                 # some lab modules read it on import
import creature
import table as T
import universal_v as UV
import universal_combo
from discrete import model as M
from units import TICK
kw = {**json.load(open("/home/pilgrim/git/simple-learner/lab/v/universal_v7.json")), **{x.split("=")[0]: float(x.split("=")[1]) for x in more if "=" in x}}


class Shown(UV.V):
    def built(self):
        return True

    def stage(self):
        return f"{a.world}, the bank"

    def draw(self, screen, side, font, sensors, motors, lit):
        screen.fill((20, 24, 28))
        lines = [f"t {self.t:6.1f} s", f"world: {a.world}", "", f"following eye {self.food}, flips {len(self.flips)}", "model: table length / trust, evidence"]
        for i, m in enumerate(self.bank):
            lines.append(("> " if i == self.act else "  ") + f"{m['n']} / {m['trust']}   {m['E']:.0f}" + ("   (default)" if i == 0 else ""))
        lines += ["", f"pause: {'ON ' + format(self.est, '.2f') + ' s' if self.pausing else 'off'}, evidence {self.P:.1f}", f"balance x {self.p.get('x', 0.0) or 0.0:+.2f}, eye levels {self.level(0):.1f} {self.level(1):.1f}"]
        for i, ln in enumerate(lines):
            screen.blit(font.render(ln, True, (230, 230, 230)), (8, 8 + 20 * i))


p, spread = M.from_bench()
creature.BRAINS["ladder"] = lambda seed: Shown(seed, {**M.drawn(p, spread, seed), "learn": 1.0, "use": 0, "trust": 1, "run_max": 1.0, **kw})
_init, _step = creature.Life.__init__, creature.Life.step


def init(self, seed=0, *args, **k):
    _init(self, seed, *args, **k)
    self.R = T.WORLDS[a.world](self.poison or "red") if isinstance(self.brain, Shown) else None
    self.done = 0
    if self.R is not None:
        self.R.setup(self, seed)
    if self.R is not None and hasattr(self.R, "taste"):
        inner = self.brain.taste
        self.brain.taste = lambda v, at: inner(self.R.taste(v), at)


def step(self):
    if self.R is None:
        return _step(self)
    self.R.now = self.t * TICK
    self.poison = self.R.poison(self.R.now)
    self.R.tick(self, self.R.now)
    _step(self)
    while self.done < len(self.meals):
        self.R.ate(self.meals[self.done][1])
        self.done += 1
    self.poison = self.R.poison(self.R.now)             # the header shows what is poison after this tick's meals


creature.Life.__init__, creature.Life.step = init, step
creature.watch(a.seed, "ladder", a.record, a.seconds, False)
