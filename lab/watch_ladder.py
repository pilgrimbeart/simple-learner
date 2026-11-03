"""Watch a test of the ladder live: python lab/watch_ladder.py RULE ARM [--seed N] [--record DIR --seconds S] [k=v ...]
RULE: plain, swap50, swap20, swap10, swap5, alternate, pattern, digest. ARM: circuit, cycle (cycle=2), grow, diagnose,
learnpause, pause (pause=1)... (lab/ladder.py). The panel: what the brain holds now."""
import argparse
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import creature
import ladder as Lad
from discrete import model as M
from units import TICK

ap = argparse.ArgumentParser()
ap.add_argument("rule")
ap.add_argument("arm")
ap.add_argument("--seed", type=int, default=52000)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=100.0)
a, more = ap.parse_known_args()
kw = {x.split("=")[0]: float(x.split("=")[1]) for x in more if "=" in x}
if a.arm == "grow" or a.arm == "diagnose":
    kw = {"theta": 3.0, "tau": 10.0, "short": 2.0, "tau_v": 40.0, **kw}
Base = Lad.ARMS[a.arm]


class Shown(Base):
    def built(self):
        return True

    def stage(self):
        return f"{a.rule}, {a.arm}"

    def draw(self, screen, side, font, sensors, motors, lit):
        screen.fill((20, 24, 28))
        lines = [f"t {self.t:6.1f} s", f"rule: {a.rule}   brain: {a.arm}", "", f"following eye {self.food}", f"flips {len(self.flips)}"]
        for name in ("n", "c", "bits", "F", "p_", "M", "P", "T"):
            if name == "p_":
                lines.append(f"trust {int(self.p.get('trust', 1))}")
            elif hasattr(self, name) and getattr(self, name) is not None:
                v = getattr(self, name)
                lines.append(f"{dict(n='sequence length', c='position', bits='which eye at each position', F='frustration', M='tally', P='tally', T='period').get(name)}: " + (f"{v:.2f}" if isinstance(v, float) else f"{v}"))
        if hasattr(self, "grew") and self.grew:
            lines.append("grew at " + ", ".join(f"{t:.1f} s to {n}" for t, n in self.grew))
        if getattr(self, "on_at", None):
            lines.append(f"turned on at {self.on_at[0]:.1f} s")
        if "pause" in self.p:
            lines.append(f"pause {self.p['pause']:.2f} s")
        for i, ln in enumerate(lines):
            screen.blit(font.render(ln, True, (230, 230, 230)), (8, 8 + 20 * i))


p, spread = M.from_bench()
creature.BRAINS["ladder"] = lambda seed: Shown(seed, {**M.drawn(p, spread, seed), "use": 0, "trust": 1, "run_max": 1.0, **kw})
_init, _step = creature.Life.__init__, creature.Life.step


def init(self, seed=0, *args, **k):
    _init(self, seed, *args, **k)
    self.R = Lad.RULES[a.rule](self.poison or "red") if isinstance(self.brain, Shown) else None
    self.done = 0
    if self.R is not None and hasattr(self.R, "taste"):
        inner = self.brain.taste
        self.brain.taste = lambda v, at: inner(self.R.taste(v), at)


def step(self):
    if self.R is None:
        return _step(self)
    self.R.now = self.t * TICK
    self.poison = self.R.poison(self.R.now)
    _step(self)
    while self.done < len(self.meals):
        self.R.ate(self.meals[self.done][1])
        self.done += 1
    self.poison = self.R.poison(self.R.now)             # the header shows what is poison after this tick's meals


creature.Life.__init__, creature.Life.step = init, step
creature.watch(a.seed, "ladder", a.record, a.seconds, False)
