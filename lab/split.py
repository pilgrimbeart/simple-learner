"""split.py: the split eye, prepared for the user's decision (QUESTIONS.md, For the user; discrete/NOTEBOOK.md, D21
put its worth to a seer at 3.95 against B's 2.54). world.py is unchanged: each eye's pulses, drawn exactly as
creature.Life draws them (the world's stream untouched), are each assigned to the half of the corridor whose rays
saw it (a Poisson process split by each half's share), so a life has four sensors: 2 * the colour's sensor + the
half's wire, the halves wired at random each life as everything else is.

The brain: B told the colour (V_H = 99, as dance.py), and a steer: while it drives, food pulses from one half (leaky
counts, tau) more than thr ahead of the other's replace a drive beat's pair by one beat on the motor that turns
towards that half. Which motor that is: told (map=oracle), wrong (map=wrong), or learned (map=learn) from its own
scan: B scans on motor 0 alone, so a block passing through the view is seen first in the half motor 0 turns
towards; a saturating counter of food-or-poison half-to-half transitions within `gap` s while scanning.

    python split.py k=v,... k=v,...     # each a variant; held out 50000-50063 x 2; steer=0 is B
"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import world
from creature import Life
from units import TICK
from discrete import model as M


class SplitLife(Life):
    def __init__(self, seed, poison, brain):
        super().__init__(seed, poison, brain=brain)
        r = np.random.default_rng(seed + 5_500_007)     # its own stream: the world's is the unsplit life's
        self.hw = (0, 1)[:: r.choice((1, -1))]          # half -> wire; half 0: rays with ACROSS < 0 (the left)
        self.hr = r

    def step(self):
        b = self.body
        _, far, kind = b.look()
        halves = []
        for h, mask in enumerate((world.ACROSS < 0, world.ACROSS > 0)):
            k = np.where(mask, kind, -1)
            halves.append(world._sees(far, k, len(world.COLOURS)))
        brain = self.brain
        seen = b.sees()
        for ci, c in enumerate(world.COLOURS):
            for _ in range(self.rng.poisson(world.SENSE * seen[c] * TICK)):
                at = self.rng.random() * TICK
                sL, sR = halves[0][ci], halves[1][ci]
                h = 0 if self.hr.random() * (sL + sR) < sL else 1
                brain.stimulate(2 * self.sensor[c] + self.hw[h], at)
        motors = brain.step()                           # (the rest is creature.Life.step's, as it is)
        fired = [f for f in world.THRUSTERS for _ in range(motors.count(self.motor[f]))]
        if fired and self.moving is None:
            self.moving = self.t
        for f in fired:
            b.fire(f)
            self.firings.append((self.t, f))
        taste = 0.0
        for c in b.move():
            self.meals.append((self.t, c))
            taste += -1.0 if c == self.poison else 1.0
            if c == self.poison:
                self.yuck = self.t
        if taste != 0.0:
            at = self.rng.random() * TICK
            brain.taste(min(max(taste, -1.0), 1.0), at)
        self.t += 1


class SplitB(M.Model):
    def __init__(self, seed, p, d):
        super().__init__(seed, p)
        self.d = d
        self.e = [0.0, 0.0]                             # food pulses per half, leaky
        self.k = 0.0                                    # learned: > 0, motor 0 turns towards half 0
        self.lastp = (None, -1e9)                       # (half, time) of the last pulse, while scanning
        self.toward = None                              # half -> motor, if told
        self.steers = 0
        self.runlen = 0
        self.margin = 0
        self.pend = []                                  # [ticks to wait, motor, beats]
        self.recent = []                                # W=: food pulses (time, half) in the last W s

    def stimulate(self, sensor, at):
        c, h = sensor // 2, sensor % 2
        super().stimulate(c, at)
        t = self.t + at
        if c == self.food:
            self.e[h] += 1.0
            self.recent.append((t, h))
        scanning = t - self.last_drive >= self.p["hold"] and t - self.last_food <= self.p["bored"]
        if scanning:
            a, ta = self.lastp
            if t - ta >= self.d.get("gap", 0.3):
                self.runlen = 0
            if a is not None and a != h and t - ta < self.d.get("gap", 0.3) and self.runlen >= self.d.get("run", 1):
                K = self.d.get("K", 8.0)
                self.k = max(-K, min(K, self.k + (1 if a == 0 else -1)))
            self.runlen = self.runlen + 1 if a == h else 1  # run=r: only after r pulses in a row from one half
            self.lastp = (h, t)

    def motor_for(self, h):
        m = self.d.get("map", "oracle")
        if m == "learn":
            if self.k == 0:
                return None
            return 0 if (self.k > 0) == (h == 0) else 1
        return self.toward[h] if m == "oracle" else 1 - self.toward[h]

    def step(self):
        out = super().step()
        due = []
        for x in self.pend:
            x[0] -= 1
            if x[0] <= 0:
                due += [x[1]] * x[2]
        self.pend = [x for x in self.pend if x[0] > 0]
        out = out + due
        f = np.exp(-TICK / self.d.get("tau", 0.1))
        self.e = [x * f for x in self.e]
        driving = self.t - self.last_drive < self.p["hold"]
        if not driving or not self.d.get("steer", 1):
            return out
        thr = self.d.get("thr", 1.0)
        h = 0 if self.e[0] - self.e[1] > thr else 1 if self.e[1] - self.e[0] > thr else None
        if "W" in self.d:                               # W, N, Q: N or more pulses from one half in W s, Q or fewer
            W = self.d["W"]                             # from the other
            self.recent = [x for x in self.recent if x[0] > self.t - W]
            n = [sum(1 for _, hh in self.recent if hh == k) for k in (0, 1)]
            N, Q = self.d.get("N", 2), self.d.get("Q", 0)
            h = 0 if n[0] >= N and n[1] <= Q and n[0] > n[1] else 1 if n[1] >= N and n[0] <= Q and n[1] > n[0] else None
            self.margin = abs(n[0] - n[1])
        qu = self.d.get("quiet")
        if h is not None and qu is not None and self.e[1 - h] > qu * self.e[h]:
            h = None                                    # quiet=q: only while the other half is near silent
        if h is None:
            return out
        self.last_h = h
        m = self.motor_for(h)
        if m is None or self.t - getattr(self, "last_steer", -1e9) < self.d.get("ref", 0.0):
            return out
        n = min(out.count(0), out.count(1))
        if not n:
            return out
        self.steers += n
        self.last_steer = self.t
        self.e = [0.0, 0.0] if self.d.get("reset") else self.e
        self.recent = [] if self.d.get("reset") else self.recent
        lag = int(self.d.get("lag", 0) if self.margin < self.d.get("big", 99) else self.d.get("lag2", 0))                 # lag=k: the other motor's beats k ticks later, cancelling
        if lag:                                         # part of the turn (k=1: 7 degrees, 2: 12; 0: dropped, 18)
            self.pend.append([lag, 1 - m, out.count(1 - m)])
        return [m] * out.count(m)                       # each pair becomes a beat towards it


def life(job):
    from minimal.spec import Lived, SPAN, thirds
    d, seed, poison = job
    lf = SplitLife(seed, poison, brain=lambda s: None)
    if d.get("body"):                                   # body=1: the thrusters drawn (discrete.bodies.THRUSTERS)
        from discrete.bodies import THRUSTERS, draw, vary
        f = draw(seed, THRUSTERS)
        vary(lf, f)
    food = lf.sensor[next(c for c in lf.sensor if c != poison)]
    p, sd = M.from_bench()
    q = M.drawn(p, sd, seed)
    q["V_H"] = 99.0
    br = SplitB(seed, q, d)
    br.food = food
    br.toward = {lf.hw[0]: lf.motor["right"], lf.hw[1]: lf.motor["left"]}   # the right thruster turns it left
    if d.get("body") and d.get("oracle"):               # oracle=1: told its balance, the drive started in step (D20's
        thr = {m: t for t, m in lf.motor.items()}       # ceiling, periodbal.py's oracle arm)
        right = np.log(f[thr[1]] / f[thr[0]])
        br.p["g0"], br.p["g1"], br.p["sync"] = float(np.exp(right / 2)), float(np.exp(-right / 2)), 1.0
    lf.brain = br
    while lf.t < 10000:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, 10000, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / 100.0, "silicon"
    right = br.toward[0] == 0                           # does motor 0 turn towards wire-half 0?
    l.learned = None if br.k == 0 else ((br.k > 0) == right)
    return l


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from minimal.spec import summary
    from discrete.poison import show
    with ProcessPoolExecutor(7) as ex:
        seeds = range(50000, 50064)
        for a in sys.argv[1:]:
            if a.startswith("seeds="):                  # seeds=lo:hi for the variants after it
                lo, hi = (int(x) for x in a[6:].split(":")); seeds = range(lo, hi)
                continue
            d = {k: (v if k == "map" else float(v)) for k, v in (x.split("=") for x in a.split(",") if x)}
            L = list(ex.map(life, [(d, s, c) for s in seeds for c in ("red", "blue")]))
            msg = ""
            if d.get("map") == "learn":
                ok = [l.learned for l in L]
                msg = f"  (map learned right in {sum(x is True for x in ok)}, wrong {sum(x is False for x in ok)} of {len(ok)})"
            print(show(f"split {d}", summary(L)) + msg, flush=True)
