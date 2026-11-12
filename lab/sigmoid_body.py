"""sigmoid_body.py: a thruster that works like a muscle (the user, 2026-11-11: each pulse delivers a sigmoid of thrust, and pulses that
follow fast on each other's heels add, so a single pulse moves very weakly but a fast burst accelerates up to substantial movement).
A body variant, opt-in: world.py's body stays the default, so every earlier result stands.

Each thruster has an activation a (like a muscle's calcium): a pulse adds 1, and it decays with time constant TAU_A. Its thrust is a
sigmoid of a, zero at rest and saturating near one:
    f(a) = (s((a - C) / W) - s(-C / W)) / (1 - s(-C / W)),   s the logistic
and it pushes continuously: forward speed gains F_PUSH f a second, and spin F_TURN f a second, away from its side, both fading at
world.DRAG as before. Scaled so that at the drive's rate (RATE_REF pulses a second, steady activation RATE_REF * TAU_A) the body moves as
fast as world.py's (a pulse there adds PUSH and TURN at once): F_PUSH f_ss = RATE_REF PUSH, F_TURN f_ss = RATE_REF TURN.

    single pulse, world.py's body: turns 18 degrees, moves .4 mm; here: see turn_of(n) (printed by `python lab/sigmoid_body.py`)."""
from __future__ import annotations

import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner"]

import numpy as np

import world
from units import TICK

import os
TAU_A = float(os.environ.get("MUSCLE_TAU", 0.03))   # s: activation's decay (the user, 2026-11-11: 30 ms, the compromise between lag and a
                                                    # gentle lone pulse, 7 degrees; 60 ms halved the starting brain's food); MUSCLE_TAU overrides
C, W = 2.0, 0.5         # the sigmoid's centre and width, in units of activation (one pulse adds 1)
RATE_REF = 50.0         # pulses a second: the drive's rate, at which the body moves as world.py's does
SUB = 10                # sub-steps a tick (activation and force are integrated finely)


def _s(x):
    return 1.0 / (1.0 + math.exp(-x))


def f_of(a):
    lo = _s(-C / W)
    return max(0.0, (_s((a - C) / W) - lo) / (1.0 - lo))


F_SS = f_of(RATE_REF * TAU_A)                   # (steady activation at the reference rate, roughly; pulses make it ripple)
F_PUSH = RATE_REF * world.PUSH / F_SS           # m/s^2 at full thrust
F_TURN = RATE_REF * world.TURN / F_SS           # rad/s^2 at full thrust


class SigmoidBody(world.Body):
    """world.Body with muscle-like thrusters (above). fire() adds a pulse to a thruster's activation; move() integrates."""

    def __init__(self, rng):
        super().__init__(rng)
        self.act = {"left": 0.0, "right": 0.0}

    def fire(self, thruster: str) -> None:
        self.act[thruster] += 1.0

    def thrust(self, thruster: str) -> float:
        return f_of(self.act[thruster])

    def move(self) -> list:
        h0 = self.head()
        dt = TICK / SUB
        for _ in range(SUB):
            fl, fr = f_of(self.act["left"]), f_of(self.act["right"])
            self.speed += (fl + fr) * F_PUSH * dt * self.forward()
            self.spin += (fr - fl) * F_TURN * dt                 # the left thruster turns it right (negative), as world.Body.fire
            self.pos = (self.pos + self.speed * dt) % world.WORLD
            self.heading += self.spin * dt
            self.speed *= math.exp(-world.DRAG * dt)
            self.spin *= math.exp(-world.DRAG * dt)
            for k in self.act:
                self.act[k] *= math.exp(-dt / TAU_A)
        if self.speed @ self.forward() <= 0:
            return []
        eaten = world._touching(self.xy, h0, self.head())
        for b in eaten:
            self.xy[b] = self.somewhere()
        return [world.COLOURS[self.kind[b]] for b in eaten]


def turn_of(pulses, interval, body_cls=SigmoidBody, seconds=1.0):
    """Degrees turned and mm moved by `pulses` pulses of the left thruster, `interval` s apart (a still body, no blocks touched)."""
    b = body_cls(np.random.default_rng(0))
    b.xy[:] = 1e3                                        # (no blocks)
    h0, p0 = b.heading, b.pos.copy()
    t, nxt, fired = 0.0, 0.0, 0
    while t < seconds:
        while fired < pulses and nxt <= t + 1e-12:
            b.fire("left")
            fired += 1
            nxt += interval
        b.move()
        t += TICK
    return math.degrees(abs(b.heading - h0)), float(np.linalg.norm(b.wrap(b.pos - p0))) * 1e3


if __name__ == "__main__":
    print(f"sigmoid: centre {C}, width {W}, activation decay {TAU_A * 1000:.0f} ms; steady thrust at {RATE_REF:.0f}/s: {F_SS:.2f}")
    for n, iv in ((1, 0.02), (2, 0.02), (3, 0.02), (5, 0.02), (10, 0.02), (5, 0.1), (10, 0.1)):
        a = turn_of(n, iv)
        o = turn_of(n, iv, world.Body)
        print(f"{n:2d} pulses {iv * 1000:3.0f} ms apart: turns {a[0]:6.1f} deg (world.py's body {o[0]:6.1f})")


_F_CACHE = {}


def mean_thrust(rate, seconds=1.0, dt=1e-4):
    """A thruster's mean thrust (0 to 1) pulsed steadily at `rate` a second, once its activation has settled (the last half)."""
    key = round(rate, 1)
    if key not in _F_CACHE:
        a, t, nxt, acc, n = 0.0, 0.0, 0.0, 0.0, 0
        dec = math.exp(-dt / TAU_A)
        while t < seconds:
            if rate > 0 and t >= nxt:
                a += 1.0
                nxt += 1.0 / rate
            if t >= seconds / 2:
                acc += f_of(a)
                n += 1
            a *= dec
            t += dt
        _F_CACHE[key] = acc / max(n, 1)
    return _F_CACHE[key]


def told_balance(k0, k1, rate):
    """The yardstick's balance knob for the muscle-like body: log(g0 / g1) at which motor 0's thruster (strength k0) and motor 1's (k1),
    pulsed at rate g0 * rate and g1 * rate (g0 g1 = 1), give equal mean thrust. Thrust isn't proportional to rate here, so world.py's
    told balance, log(k1 / k0), is wrong for this body."""
    lo, hi = -4.0, 4.0
    for _ in range(40):
        b = (lo + hi) / 2
        d = k0 * mean_thrust(rate * math.exp(b / 2)) - k1 * mean_thrust(rate * math.exp(-b / 2))
        lo, hi = (lo, b) if d > 0 else (b, hi)
    return (lo + hi) / 2


def told_tempo(d, rate):
    """The yardstick's tempo for the muscle-like body: the factor s on a rate at which mean thrust grows by the drag factor d
    (speed goes as thrust over drag), F(s rate) = d F(rate), solved on a grid; world.py's told tempo was d itself."""
    target = d * mean_thrust(rate)
    lo, hi = 0.1, 10.0
    for _ in range(40):
        s = math.sqrt(lo * hi)
        lo, hi = (s, hi) if mean_thrust(rate * s) < target else (lo, s)
    return math.sqrt(lo * hi)


def right_knob(k0, k1, rate):
    """The right balance knob, log(g0 / g1), for whichever body is on (for reporting a learner's error, and for yardsticks)."""
    import sys
    sim = sys.modules.get("stage2_lang.sim")
    if sim is not None and sim.WLife.muscle:
        return told_balance(k0, k1, rate)
    return math.log(k1 / k0)
