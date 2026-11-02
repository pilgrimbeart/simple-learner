"""cmodel3.py SEEDS k=v ...: cmodel2 judged robustly (D13): each life draws its blocks' numbers from their spread
over seeds' tolerances (SPREAD, benched in ngspice on 32 seeds), and with body=1 its own thrusters (bodies.THRUSTERS).
cmodel2: cmodel's blocks, with the variants of D13: confidence (conf: doubt may fall that far below
rest, food tasted taking it down by fstep, recovering towards rest at cleak), clearing (flip_reset, food_reset 1:
tasted), leaving by poison seen (pk: each poison seen ages the boredom timer by that many s), a Charnov comparator
(charnov: leave when food seen lately, fading over tf, falls below ratio x its long-run rate, fading over ts)."""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from units import TICK

NOMINAL = dict(hold=0.2, bored=2.69, scan=12.3, drive=44.4, run=12.6, step=1.12, leak=0.43, hi=1.5, lo=0.23,
               top=1.8, food_reset=0, flip_reset=0, conf=0.0, fstep=0.0, cleak=0.0, pk=0.0, charnov=0, tf=1.0,
               ts=10.0, ratio=0.5)


SPREAD = dict(hold=0.144, bored=0.209, scan=0.097, drive=0.071, run=0.091, step=0.047, leak=0.171, fstep=0.047,
              cleak=0.171, pk=0.209, tf=0.209, ts=0.209)  # sd of the log, each block's number (a timer, a rate, a step)
SHIFT = dict(hi=0.02, lo=0.01)                          # V, sd: thresholds


def drawn(p, seed):
    """A life's own blocks: each number its design's, varied as the seed's tolerances vary it."""
    rng = np.random.default_rng(seed + 7_300_001)
    q = dict(p)
    for k, sd in SPREAD.items():
        q[k] = p[k] * float(np.exp(rng.normal(0.0, sd)))
    for k, sd in SHIFT.items():
        q[k] = p[k] + float(rng.normal(0.0, sd))
    return q


class Model:
    def __init__(self, seed, **p):
        self.p = {**NOMINAL, **p}
        rng = np.random.default_rng(seed + 91)
        self.food = int(rng.integers(2))
        self.seen = [0, 0]
        self.t = 0.0
        self.last_drive = self.last_food = -1e9
        self.phase = rng.random()
        self.doubt, self.armed = 0.0, True
        self.fast = self.slow = 0.0                     # charnov: food seen lately, and over the long run
        self.running = True
        self.flips = []                                 # watching: when the bit flipped

    def stimulate(self, sensor, at):
        self.seen[sensor] += 1

    def taste(self, value, at):
        p = self.p
        if value < 0:
            self.doubt = min(p["top"], self.doubt + p["step"])
            if self.armed and self.doubt >= p["hi"]:
                self.food, self.armed = 1 - self.food, False
                self.flips.append(self.t)
                if p["flip_reset"]:
                    self.doubt, self.armed = 0.0, True
        elif value > 0:
            if p["conf"]:
                self.doubt = max(-p["conf"], self.doubt - p["fstep"])
            elif p["food_reset"] == 1:
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
        if P:
            self.last_drive = -1e9
            self.last_food -= p["pk"] * P
        driving = self.t - self.last_drive < p["hold"]
        if p["charnov"]:
            self.fast += F / p["tf"] - self.fast * TICK / p["tf"]
            self.slow += F / p["ts"] - self.slow * TICK / p["ts"]
            if F:
                self.running = False
            elif self.fast < p["ratio"] * self.slow:
                self.running = True
            running = self.running and not driving
        else:
            running = not driving and self.t - self.last_food > p["bored"]
        if self.doubt > 0:
            self.doubt = max(0.0, self.doubt - p["leak"] * TICK)
        else:
            self.doubt = min(0.0, self.doubt + p["cleak"] * TICK)
        if self.doubt < p["lo"]:
            self.armed = True
        self.phase += (p["drive"] if driving else p["run"] if running else p["scan"]) * TICK
        beats = int(self.phase)
        self.phase -= beats
        return [0] * beats + [1] * beats * (driving or running)


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    p, seed, seconds, poison = job
    q = drawn({**NOMINAL, **p}, seed) if p.get("vary", 1) else {**NOMINAL, **p}
    lf = Life(seed, poison, brain=lambda s: Model(s, **{k: v for k, v in q.items() if k not in ("vary", "body")}))
    if p.get("body"):
        from discrete.bodies import THRUSTERS, draw, vary
        vary(lf, draw(seed, THRUSTERS))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings = 9e-9, SPAN * len(lf.firings) / seconds
    return l


def lives(p, seeds, seconds=100.0, ex=None):
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(p, s, seconds, c) for s in seeds for c in ("red", "blue")]
    if ex:
        return list(ex.map(life, jobs))
    with ProcessPoolExecutor() as e:
        return list(e.map(life, jobs))


if __name__ == "__main__":
    from discrete.poison import show
    from minimal.spec import summary
    p = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:])}
    lo, hi = (int(x) for x in sys.argv[1].split(":"))
    print(show(f"model {p}", summary(lives(p, range(lo, hi)))))
