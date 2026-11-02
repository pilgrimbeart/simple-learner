"""cmodel.py: the CMOS policy circuit (cmos.pol) as its blocks' measured behaviour (blocks.py), a brain for
creature.Life lived in about a second. Each block is a few lines; its numbers are the bench's."""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from units import TICK

NOMINAL = dict(hold=0.063, bored=2.69, scan=12.3, drive=44.4, run=12.6, step=1.12, leak=0.43, hi=1.5, lo=0.23,
               top=1.8, fb=0, food_reset=0, flip_reset=0)


class Model:
    def __init__(self, seed, **p):
        self.p = {**NOMINAL, **p}
        rng = np.random.default_rng(seed + 91)
        self.food = int(rng.integers(2))                # the bit: which eye it calls food (q), by chance at birth
        self.seen = [0, 0]
        self.t = 0.0
        self.last_drive = -1e9                          # hd: the last food pulse, unless poison was seen since
        self.last_food = -1e9                           # bt: the last food pulse (birth: empty, so it runs)
        self.phase = rng.random()                       # the oscillator
        self.doubt, self.armed = 0.0, True              # dq and its Schmitt (T)

    def stimulate(self, sensor, at):
        self.seen[sensor] += 1

    def taste(self, value, at):
        p = self.p
        if value < 0:                                   # a poison: doubt steps up; through hi, the bit flips
            self.doubt = min(p["top"], self.doubt + p["step"])
            if self.armed and self.doubt >= p["hi"]:
                self.food, self.armed = 1 - self.food, False
                if p["flip_reset"]:                     # (an option: the flip clears doubt)
                    self.doubt, self.armed = 0.0, True
        elif value > 0 and p["food_reset"] == 1:        # (an option: food clears doubt; 2: food seen)
            self.doubt = 0.0

    def drive(self, sensor):
        return 1.0

    def step(self):
        p = self.p
        F, P = self.seen[self.food], self.seen[1 - self.food]
        self.seen = [0, 0]
        self.t += TICK
        if F:
            self.last_drive = self.last_food = self.t
            if p["food_reset"] == 2:
                self.doubt = 0.0
        if P:
            self.last_drive = -1e9                      # poison ahead empties the hold
        driving = self.t - self.last_drive < p["hold"]
        running = not driving and self.t - self.last_food > p["bored"]
        self.doubt = max(0.0, self.doubt - p["leak"] * TICK)
        if self.doubt < p["lo"]:
            self.armed = True
        self.phase += (p["drive"] if driving else p["run"] if running else p["scan"]) * TICK
        beats = int(self.phase)
        self.phase -= beats
        out = [0] * beats + [1] * beats * (driving or running)
        if p["fb"]:
            out += [1] * F
        return out


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    p, seed, seconds, poison = job
    lf = Life(seed, poison, brain=lambda s: Model(s, **p))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings = 9e-9, SPAN * len(lf.firings) / seconds
    return l


def lives(p, seeds, seconds=100.0):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as ex:
        return list(ex.map(life, [(p, s, seconds, c) for s in seeds for c in ("red", "blue")]))


if __name__ == "__main__":
    import pickle
    from discrete.poison import show
    from minimal.spec import summary
    p = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:])}
    lo, hi = (int(x) for x in sys.argv[1].split(":"))
    L = lives(p, range(lo, hi))
    print(show(f"model {p}", summary(L)))
