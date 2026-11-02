"""cmodel4.py: cmodel3, each motor's rates scaled by g0, g1 (in drive and run; g0 also in the scan); oracle=1:
the drive balanced for the body (it goes straight), oracle=2: every firing restored to world.py's effect.
cmodel3.py SEEDS k=v ...: cmodel2 judged robustly (D13): each life draws its blocks' numbers from their spread
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
               ts=10.0, ratio=0.5, g0=1.0, g1=1.0, adapt=0.0, wob=0.2, base=5.0, xmax=1.4, refind=0.0, t0=0.5, tmax=3.0, alt=0.0, sysid=0, prior_e=2.0, prior_f=10.0, swap=0, back=0.0, flip_to=0.0, init=0.0, drift=0.0, zig=0.0, zw=0.3, zp=0.1, mealw=0.0, lone=0.0)


SPREAD = dict(drift=0.5, hold=0.144, bored=0.209, scan=0.097, drive=0.071, run=0.091, step=0.047, leak=0.171, fstep=0.047,
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
        self.phase1 = rng.random()
        self.x = 0.0                                    # adapt: the drive's balance (log of motor 0's share against 1's)
        self.sign, self.pulses, self.mean = 1.0, 0, 0.0   # this approach's nudge, its pulses, their running mean
        self.was_driving = False
        self.food_tasted = False
        self.lost_at, self.tasted_at = None, -1e9      # refind: when the drive last lost its block
        self.scan_motor, self.scan_since = 0, 0.0      # alt: the scan's motor, swapped every alt s of scanning
        self.ep = [0.0, 0.0]; self.fi = [0.0, 0.0]      # sysid: sightings begun, and firings, scanning with each motor
        self.any_before = False
        self.was_drv = False
        self.was_on = False
        self.zn = [0, 0]; self.zt = 0.0; self.zwas = False; self.zstart = 0   # zig: pulses in each half of the wobble
        self.doubt, self.armed = self.p["init"], True
        self.fast = self.slow = 0.0                     # charnov: food seen lately, and over the long run
        self.running = True
        self.flips = []                                 # watching: when the bit flipped

    def stimulate(self, sensor, at):
        self.seen[sensor] += 1

    def taste(self, value, at):
        p = self.p
        self.tasted_at = self.t
        self.food_tasted = value > 0
        if value < 0:
            self.doubt = min(p["top"], self.doubt + p["step"])
            if self.armed and self.doubt >= p["hi"]:
                self.food, self.armed = 1 - self.food, False
                self.flips.append(self.t)
                if p["flip_reset"]:
                    self.doubt, self.armed = p["flip_to"], True
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
        if p["drift"]:                                  # (drift: the circuit's leak towards trust, to the floor)
            self.doubt = max(-p["conf"], self.doubt - p["drift"] * TICK)
        if self.doubt > 0:
            self.doubt = max(0.0, self.doubt - p["leak"] * TICK)
        else:
            self.doubt = min(0.0, self.doubt + p["cleak"] * TICK)
        if self.doubt < p["lo"]:
            self.armed = True
        if p["swap"] and self.was_drv and not driving and not P and self.t - self.tasted_at > 0.05:
            self.scan_motor = 1 - self.scan_motor       # swap: a block lost from a drive, so sweep back the other way
            self.swapped_at = self.t
        if p["swap"] and p["back"] and self.t - getattr(self, "swapped_at", -1e9) > p["back"]:
            self.scan_motor = 0                         # (back: after so long, the usual way again)
        self.was_drv = driving
        g0, g1 = p["g0"], p["g1"]
        if p["zig"]:                                    # zig: within each approach the balance wobbles (period zp);
            if driving:                                 # the pulses in its two halves, compared at the approach's
                self.zt += TICK                         # end, move it the way that kept the block in view
                half = (int(self.zt / (p["zp"] / 2)) + self.zstart) % 2   # (each approach starts in the other half:
                                                                           # its first moments, rich in pulses, balanced)
                self.zn[half] += F
                y = self.x + p["zw"] * (1 if half == 0 else -1)
            else:
                if self.zwas:
                    a, b = self.zn
                    self.x = float(np.clip(self.x + p["zig"] * (a - b) / (a + b + 1.0), -p["xmax"], p["xmax"]))
                    self.zstart = 1 - self.zstart
                self.zn, self.zt, y = [0, 0], 0.0, self.x
            self.zwas = driving
            g0, g1 = g0 * np.exp(y / 2), g1 * np.exp(-y / 2)
        if p["sysid"]:
            g0, g1 = g0 * np.exp(self.x / 2), g1 * np.exp(-self.x / 2)
        if p["adapt"]:                                  # extremum seeking: each approach nudged one way or the other;
            if driving and not self.was_driving:        # its food pulses against their running mean move the balance
                self.sign, self.pulses = -self.sign, 0  # the way its nudge went
            if driving:
                self.pulses += F
                if p["mealw"] and self.tasted_at >= self.t - TICK and self.food_tasted:
                    self.pulses += p["mealw"]           # (mealw: a meal ending the approach counts that many pulses)
            if self.was_driving and not driving:
                d = self.pulses - self.mean
                self.x = float(np.clip(self.x + p["adapt"] * self.sign * d, -p["xmax"], p["xmax"]))
                self.mean += (self.pulses - self.mean) / p["base"]
            self.was_driving = driving
            y = self.x + p["wob"] * self.sign
            g0, g1 = g0 * np.exp(y / 2), g1 * np.exp(-y / 2)
        if p["refind"]:                                 # the scan turns one way: a block lost from a drive curving
            if self.was_driving and not driving:        # with the scan is found again late, one lost from a drive
                lost = not P and self.t - self.tasted_at > 0.05   # curving against it soon; so motor 0's share
                self.lost_at = self.t if lost else None           # falls after a late find, rises after a soon one
            elif F and self.lost_at is not None:
                dt = self.t - self.lost_at
                if dt < p["tmax"]:
                    self.x = float(np.clip(self.x + p["refind"] * (1.0 if dt < p["t0"] else -1.0), -p["xmax"], p["xmax"]))
                self.lost_at = None
            self.was_driving = driving
            y = self.x
            g0, g1 = g0 * np.exp(y / 2), g1 * np.exp(-y / 2)
        extra = []                                      # lone: motor B's gate opening at a drive's start while the
        if p["lone"] and driving and not self.was_on and self.phase < p["lone"]:   # slow beat is still high (that
            extra = [1]                                 # fraction of its cycle) fires B alone (not from a run: B on)
        self.was_on = driving or running
        r = p["drive"] if driving else p["run"] if running else p["scan"]
        self.phase += r * (g0 if driving or running else p["g0"]) * TICK   # (the scan unbalanced)
        beats = int(self.phase)
        self.phase -= beats
        if not (driving or running):
            m = self.scan_motor
            if p["alt"]:
                self.scan_since += TICK
                if self.scan_since >= p["alt"]:
                    self.scan_motor, self.scan_since = 1 - m, 0.0
            if p["sysid"]:                              # each motor's turn, from the world sweeping past: sightings
                any_now = bool(F or P)                  # begun per firing, scanning with it
                if p["sysid"] == 2:                     # 2: pulses per firing, as long as a block stays in view per
                    self.ep[m] += F + P                 # firing, so as 1 / the motor's turn
                elif any_now and not self.any_before:
                    self.ep[m] += 1
                self.fi[m] += beats
                r0 = (self.ep[0] + p["prior_e"]) / (self.fi[0] + p["prior_f"])
                r1 = (self.ep[1] + p["prior_e"]) / (self.fi[1] + p["prior_f"])
                self.x = float(np.clip(np.log(r0 / r1) if p["sysid"] == 2 else np.log(r1 / r0), -p["xmax"], p["xmax"]))
            self.any_before = bool(F or P)
            return [m] * beats
        if g1 == g0:
            return extra + [0, 1] * beats
        self.phase1 += r * g1 * TICK
        b1 = int(self.phase1)
        self.phase1 -= b1
        return extra + [0] * beats + [1] * b1


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    p, seed, seconds, poison = job
    q = drawn({**NOMINAL, **p}, seed) if p.get("vary", 1) else {**NOMINAL, **p}
    lf = Life(seed, poison, brain=lambda s: Model(s, **{k: v for k, v in q.items() if k not in ("vary", "body", "oracle")}))
    if p.get("body"):
        from discrete.bodies import THRUSTERS, draw, vary
        f = draw(seed, THRUSTERS)
        vary(lf, f)
        if p.get("oracle"):                             # (told the body: the ceiling for adapting to it)
            thr = {m: t for t, m in lf.motor.items()}         # motor -> thruster
            k0, k1 = f[thr[0]], f[thr[1]]
            g = (1 / k0, 1 / k1) if p["oracle"] == 2 else ((k1 / k0) ** 0.5, (k0 / k1) ** 0.5)
            lf.brain.p["g0"], lf.brain.p["g1"] = g
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
    with ProcessPoolExecutor(4) as e:
        return list(e.map(life, jobs))


if __name__ == "__main__":
    from discrete.poison import show
    from minimal.spec import summary
    p = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:])}
    lo, hi = (int(x) for x in sys.argv[1].split(":"))
    print(show(f"model {p}", summary(lives(p, range(lo, hi)))))
