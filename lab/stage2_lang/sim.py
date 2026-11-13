"""sim.py: the engine: a copy of world.Body and creature.Life.step in a pipeline of named stages, each with hooks that do nothing when a
world has no rule there. world.py and creature.py are untouched; every world.py constant is a register of the life. Nothing here knows
about any brain beyond the interface: stimulate, step, taste.

Two modes (stage 2c), by WLife.seconds (the class default) or the `seconds` argument:
  seconds=False   creature.Life's loop, tick by tick: with no rules a life is the unmodified life exactly (lab/stage2c_identity.py).
                  Motor beats at the tick's start, the body moved by one Euler step, one taste a tick (the meals' signs summed and
                  clipped, food and poison cancelling), deferrals rounded to whole ticks, injected pulses first in their tick.
  seconds=True    everything at its own moment: each motor beat fires at its moment within the tick (the brain's `beats`, or a moment
                  drawn uniformly if it gives none), the body's motion integrated exactly between events (drag as an exponential); the
                  mouth's path checked segment by segment, each meal at its own moment; each meal its own taste at that moment; deferrals
                  at their exact time, run inside the tick they fall in; pulses, injected or not, delivered in order of their moments; a
                  block touched and left uneaten (drop) is one touch while the contact lasts, not one a tick. Event stages see `t` as
                  the event's moment.
In both: the interface by construction. A world writes only a meal's worth (0, or a size in lang.WORTH_RANGE, either sign); the taste is
the worth's sign, computed here; the score is the worths, and COST and THRUST are fixed at birth. A rule's Python error refuses the life.
Instruments watch every life (lab/stage2_lang/instruments.py reads what is recorded here) and never feed back; WLife.instruments =
False switches them off, for worlds already vetted.
Speed (2026-11-06, about 7x at 1 ms): with no instruments, no trace and no rule at see, pulse, fire or move, seconds mode runs
_step_fast (the same tick, its light and motion compiled), and with a compiled brain (fast.py) _step_fused (light and draws, then
brain, beats and motion, compiled, numpy's own draw function called from compiled code). _step_seconds stays the reference: every
fast life is checked identical to it (lab/speed_fingerprint.py, lab/speed_crosscheck.py), and a change to _step_seconds must be made
in _step_fast and _step_fused too, then those two checks re-run."""
from __future__ import annotations

import heapq
import math
import re

import numpy as np
from numba import njit

import units
import world as W0
from stage2_lang.lang import LifeRefused as Refused, WORTH_RANGE
from stage2_lang.fast import step as _brain_step

COLOURS = W0.COLOURS
THRUSTERS = W0.THRUSTERS
EXTRA = (0.5, 0.25)                                     # the new thrusters' strengths, against the original's 1 (WLife.extra)
GROW = (100.0, 300.0)                                   # s: the new parts come alive at a moment drawn uniformly in this range
MUSCLE_STEP = 0.0005                                    # s: the muscle-like body's sub-step while a thruster's activation lasts


@njit(cache=True)
def _wrap(d, world):
    x = d + world / 2
    if 0.0 <= x < world:                                # x % world is x itself here (Python's float %): the same value, no division
        return x - world / 2
    return x % world - world / 2


@njit(cache=True)
def _mod(x, world):
    """x % world, Python's float %, skipping the division when x is already in (0, world); 0 gives +0.0, as Python's % does."""
    if 0.0 < x < world:
        return x
    if x == 0.0:
        return 0.0
    return x % world


@njit(cache=True)
def _look(xy, alive, h, f, world, block, reach_range, eat, across):
    """The first block each ray meets (or -1), and how far (or RANGE). As world._look, returning the block rather than its kind."""
    rays = across.shape[0]
    far, hit_b = np.full(rays, reach_range), np.full(rays, -1)
    for b in range(xy.shape[0]):
        if not alive[b]:
            continue
        dx, dy = _wrap(xy[b, 0] - h[0], world), _wrap(xy[b, 1] - h[1], world)
        ahead, off = dx * f[0] + dy * f[1], dx * f[1] + dy * -f[0]
        if ahead <= -block or ahead - block >= reach_range or abs(off) >= eat + block:
            continue
        for k in range(rays):
            gap = block ** 2 - (across[k] - off) * (across[k] - off)
            if gap > 0:
                hit = max(0.0, ahead - np.sqrt(gap))
                if hit < far[k]:
                    far[k], hit_b[k] = hit, b
    return far, hit_b


@njit(cache=True)
def _sees(far, hit_b, look, bright, share, reach):
    seen = np.zeros(2)
    for k in range(far.shape[0]):
        b = hit_b[k]
        if b >= 0 and look[b] >= 0:
            seen[look[b]] += bright[b] * share / (1 + (far[k] / reach) * (far[k] / reach))
    return np.minimum(seen, 1.0)


@njit(cache=True)
def _touching(xy, alive, h0, h1, world, eat):
    sx, sy = _wrap(h1[0] - h0[0], world), _wrap(h1[1] - h0[1], world)
    ss = sx * sx + sy * sy
    out = []
    for b in range(xy.shape[0]):
        if not alive[b]:
            continue
        dx, dy = _wrap(xy[b, 0] - h0[0], world), _wrap(xy[b, 1] - h0[1], world)
        u = min(max((dx * sx + dy * sy) / ss, 0.0), 1.0) if ss > 0.0 else 0.0
        ex, ey = dx - u * sx, dy - u * sy
        if np.sqrt(ex * ex + ey * ey) < eat:
            out.append(b)
    return out


@njit(cache=True)
def _touching_u(xy, alive, h0, h1, world, eat):
    """As _touching, with where along the segment each block is first within reach (0 to 1): the meal's moment."""
    sx, sy = _wrap(h1[0] - h0[0], world), _wrap(h1[1] - h0[1], world)
    ss = sx * sx + sy * sy
    bs, us = [], []
    for b in range(xy.shape[0]):
        if not alive[b]:
            continue
        dx, dy = _wrap(xy[b, 0] - h0[0], world), _wrap(xy[b, 1] - h0[1], world)
        u = min(max((dx * sx + dy * sy) / ss, 0.0), 1.0) if ss > 0.0 else 0.0
        ex, ey = dx - u * sx, dy - u * sy
        e2 = ex * ex + ey * ey
        if e2 < eat * eat:
            # the first point of the segment within reach: the smaller root v of |d - v s| = eat, or 0 if it starts within reach
            # (the checker, 2026-11-06: going back from the clipped closest point gave moments up to a tick early)
            dd, ds = dx * dx + dy * dy, dx * sx + dy * sy
            if dd <= eat * eat or ss <= 0.0:
                v = 0.0
            else:
                v = (ds - math.sqrt(max(0.0, ds * ds - ss * (dd - eat * eat)))) / ss
            bs.append(b)
            us.append(min(max(v, 0.0), 1.0))
    return bs, us


@njit(cache=True)
def _see(xy, alive, look, bright, across, K, scr, hx, hy, fx, fy):
    """Body.sees2's first value as two floats: _look then _sees, in one call, the same arithmetic in the same order. K: the life's
    constants (WLife._consts); scr: scratch, two rows as long as across (how far each ray goes, the block it meets)."""
    world, block, reach_range, eat, share, reach = K[0], K[1], K[2], K[3], K[4], K[5]
    far, hit_b = scr[0], scr[1]
    rays = across.shape[0]
    for k in range(rays):
        far[k], hit_b[k] = reach_range, -1
    for b in range(xy.shape[0]):
        if not alive[b]:
            continue
        dx, dy = _wrap(xy[b, 0] - hx, world), _wrap(xy[b, 1] - hy, world)
        ahead, off = dx * fx + dy * fy, dx * fy + dy * -fx
        if ahead <= -block or ahead - block >= reach_range or abs(off) >= eat + block:
            continue
        for k in range(rays):
            gap = block ** 2 - (across[k] - off) * (across[k] - off)
            if gap > 0:
                hit = max(0.0, ahead - np.sqrt(gap))
                if hit < far[k]:
                    far[k], hit_b[k] = hit, b
    s0, s1 = 0.0, 0.0
    for k in range(rays):
        b = int(hit_b[k])
        if b >= 0 and look[b] >= 0:
            v = bright[b] * share / (1 + (far[k] / reach) * (far[k] / reach))
            if look[b] == 0:
                s0 += v
            else:
                s1 += v
    return min(s0, 1.0), min(s1, 1.0)


@njit(cache=True)
def _move(pos, sp, xy, alive, K, hits, heading, spin, fc, fs, dtau):
    """WLife._advance's motion and the mouth's path, as it computes them: pos and sp in place; returns (heading, spin, cos, sin, hits),
    the hits in hits[0] (where along the path) and hits[1] (the block)."""
    world, eat, D, R = K[0], K[3], K[6], K[7]
    e = math.exp(-D * dtau)
    f = (1 - e) / D if D > 0 else dtau
    h0x, h0y = pos[0] + fc * R, pos[1] + fs * R
    pos[0], pos[1] = _mod(pos[0] + sp[0] * f, world), _mod(pos[1] + sp[1] * f, world)
    heading += spin * f
    sp[0], sp[1] = sp[0] * e, sp[1] * e
    spin *= e
    c, s = math.cos(heading), math.sin(heading)
    n = 0
    if sp[0] * c + sp[1] * s > 0:
        bs, us = _touching_u(xy, alive, (h0x, h0y), (pos[0] + c * R, pos[1] + s * R), world, eat)
        for j in range(len(bs)):
            hits[0, j], hits[1, j] = us[j], bs[j]
        n = len(bs)
    return heading, spin, c, s, n


# numpy's own draw, called from compiled code: every PCG64 generator's next_double is this one C function, given its state's address,
# so the draws are numpy's, in numpy's order, and the Python generator sees them (lab/speed_fingerprint.py checks)
import ctypes as _ct
_NEXT_DOUBLE = _ct.CFUNCTYPE(_ct.c_double, _ct.c_void_p)(_ct.cast(np.random.default_rng(0).bit_generator.ctypes.next_double, _ct.c_void_p).value)


@njit(cache=False)
def _poisson(state, lam):
    """numpy Generator.poisson for 0 <= lam < 10 (random_poisson: 0 with no draw, else the multiplication method)."""
    if lam == 0:
        return 0
    enlam = math.exp(-lam)
    X = 0
    prod = 1.0
    while True:
        prod *= _NEXT_DOUBLE(state)
        if prod > enlam:
            X += 1
        else:
            return X


@njit(cache=False)
def _sense(xy, alive, look, bright, across, K, scr, hx, hy, fx, fy, state, dt, sense, ws0, ws1, out):
    """_step_fast's light and pulses: _see, then for each colour its Poisson count and each pulse's moment, drawn as
    [(rng.random() * dt, wire_s[c], c) for _ in range(rng.poisson(SENSE * seen[c] * dt))] draws them. out rows: moment, eye, colour.
    Returns the count, or -1 if a rate is too high for the method (the caller then draws in Python)."""
    s0, s1 = _see(xy, alive, look, bright, across, K, scr, hx, hy, fx, fy)
    if sense * s0 * dt >= 10 or sense * s1 * dt >= 10:  # before any draw: the caller draws both in Python (out[0, 0], out[0, 1]: the light)
        out[0, 0], out[0, 1] = s0, s1
        return -1
    n = 0
    for c in range(2):
        lam = sense * (s0 if c == 0 else s1) * dt
        X = _poisson(state, lam)
        for _ in range(X):
            out[0, n], out[1, n], out[2, n] = _NEXT_DOUBLE(state) * dt, (ws0 if c == 0 else ws1), c
            n += 1
    return n


@njit(cache=False)
def _tick_b(S, Q, E, I, F, nev, dt, flags, pos, sp, H, xy, alive, K, hits, FB, M, wm0, wm1):
    """_step_fast after the pulses: the brain's step (fast.step), its beats in order of moment (the heap's (moment, index)), each
    fired as WLife.fire fires it, the body moved between them (_move). Returns at the first segment with hits (1: M[3], M[4] its start
    and length; the caller eats them and calls again with M[0] < 0 cleared) or at the tick's end (0). M: 0 the moment reached (-1:
    start), 1 the next beat, 2 the beats, 3, 4 a segment, 5 clear the bounced set, 6 a segment ran with the set non-empty (in: 1 if
    it is non-empty), 7 firings recorded in FB. H: heading, spin, cos, sin."""
    bm, bt, order = I[2], F[0], I[1]
    if M[0] < 0:
        nb = _brain_step(S, Q, E, I, F, nev, dt, flags)
        top = dt * (1 - 1e-12)
        for j in range(nb):                               # clip, then order by (moment, index) as the heap pops
            bt[j] = min(max(bt[j], 0.0), top)
            order[j] = j
        for j in range(1, nb):
            o = order[j]
            k = j - 1
            while k >= 0 and (bt[order[k]] > bt[o] or (bt[order[k]] == bt[o] and order[k] > o)):
                order[k + 1] = order[k]
                k -= 1
            order[k + 1] = o
        M[0], M[1], M[2], M[7] = 0.0, 0, nb, 0
        fl = 1 if (flags[0] or flags[1] or flags[2]) else 0
    else:
        fl = 0
    cur = M[0]
    j = int(M[1])
    nb = int(M[2])
    while True:
        at = bt[order[j]] if j < nb else dt
        if at - cur > 0:
            hd, spn, c, s_, n = _move(pos, sp, xy, alive, K, hits, H[0], H[1], H[2], H[3], at - cur)
            H[0], H[1], H[2], H[3] = hd, spn, c, s_
            if n:
                M[0], M[1], M[3], M[4] = at, j, cur, at - cur
                return 2 * n + fl
            if M[6]:
                M[5], M[6] = 1, 0
        cur = at
        if j >= nb:
            M[0], M[1] = cur, j
            return fl
        m = bm[order[j]]
        for th in range(2):
            if (wm0 if th == 0 else wm1) != m:
                continue
            sp[0], sp[1] = sp[0] + K[8] * H[2], sp[1] + K[8] * H[3]     # Body.fire with gain 1: speed += PUSH * forward
            H[1] = H[1] + K[9] if th == 1 else H[1] + -K[9]             # spin += TURN, or += -TURN
            FB[int(M[7])] = th
            M[7] += 1
        j += 1


class Body:
    """world.Body, its constants the life's. kind: what a block is worth by (read as colour); look: which eye it drives (-1 none, though it still stops a ray); bright: how strongly; alive: whether it exists."""

    def __init__(self, rng, K):
        self.rng, self.K = rng, K
        self.pos = np.array([K.WORLD / 2, K.WORLD / 2])
        self.heading = rng.uniform(0, 2 * math.pi)
        self.speed, self.spin = np.zeros(2), 0.0
        self._fh = None                                  # forward() cached for this heading
        self.kind = np.repeat(np.arange(2), K.BLOCKS)
        self.muscle, self.act, self.kg = False, [0.0, 0.0], [1.0, 1.0]
        self.n = len(self.kind)
        self.look = self.kind.copy()
        self.bright = np.ones(self.n)
        self.alive = np.ones(self.n, dtype=np.bool_)
        self.geometry()
        self.xy = np.array([self.somewhere() for _ in self.kind])

    def geometry(self):
        K = self.K
        rays = int(K.RAYS)
        self.across = -K.EAT + (np.arange(rays) + 0.5) * 2 * K.EAT / rays
        self.share = (2 * K.EAT / rays) / (2 * K.BLOCK)

    def somewhere(self):
        K = self.K
        while True:
            p = self.rng.uniform(0, K.WORLD, 2)
            if np.linalg.norm(self.wrap(p - self.pos)) > 3 * K.EAT + K.BODY:
                return p

    def wrap(self, d):
        w = self.K.WORLD
        return (d + w / 2) % w - w / 2

    def forward(self):
        h = self.heading
        if h != self._fh:
            self._fh, self._fc, self._fs = h, math.cos(h), math.sin(h)
            self._fv = None
        if self._fv is None:
            self._fv = np.array([self._fc, self._fs])
        return self._fv                                 # shared: callers never write into it

    def head_xy(self):
        """head() as two floats: the same arithmetic, element by element."""
        h = self.heading
        if h != self._fh:
            self._fh, self._fc, self._fs, self._fv = h, math.cos(h), math.sin(h), None
        R = self.K.RADIUS
        return (self.pos[0] + self._fc * R, self.pos[1] + self._fs * R)

    def head(self):
        return self.pos + self.forward() * self.K.RADIUS

    def fspeed(self):
        return float(self.speed @ self.forward())

    def sees(self):
        return self.sees2()[0]

    def halves(self):
        """Light at each eye from each half of the corridor (rays across < 0: half 0, the left; > 0: half 1): [half][colour]."""
        K = self.K
        h = self.head_xy()
        far, hit = _look(self.xy, self.alive, h, (self._fc, self._fs), K.WORLD, K.BLOCK, K.RANGE, K.EAT, self.across)
        return [_sees(far, np.where(mask, hit, -1), self.look, self.bright, self.share, K.REACH)
                for mask in (self.across < 0, self.across > 0)]

    def sees2(self, watch=True):
        """(light at each eye as the blocks look, light by each block's kind as world.py would show it): the second is watching only,
        and None when nothing watches."""
        K = self.K
        h = self.head_xy()
        far, hit = _look(self.xy, self.alive, h, (self._fc, self._fs), K.WORLD, K.BLOCK, K.RANGE, K.EAT, self.across)
        seen = _sees(far, hit, self.look, self.bright, self.share, K.REACH)
        if not watch:
            return seen, None
        bykind = np.where(self.kind < 2, self.kind, -1)
        return seen, _sees(far, hit, bykind, np.ones(self.n), self.share, K.REACH)

    def fire(self, thruster, k):
        if self.muscle:                                 # a pulse raises the thruster's activation; its strength k scales its thrust
            while len(self.act) <= thruster:            # the new parts (WLife.extra) are muscles too
                self.act.append(0.0)
                self.kg.append(1.0)
            self.act[thruster] += 1.0
            self.kg[thruster] = k * (EXTRA[thruster // 2 - 1] if thruster >= 2 else 1.0)
            return
        K = self.K
        if thruster >= 2:                               # a new part (WLife.extra): its strength, on its side
            k = k * EXTRA[thruster // 2 - 1]
        self.speed += k * K.PUSH * self.forward()
        self.spin += k * K.TURN if thruster % 2 == 1 else -(k * K.TURN)   # the left one (0) turns it right, the right one left


class WLife:
    """A body, a brain and a world's rules: the same fields as creature.Life, and, with seconds=False, the same draws in the same order.

    Pipeline, each tick: deferred writes, tick, (told, for a told arm), see, pulse, brain.step, fire, move, meal, respawn, score. meals
    holds (tick, colour's name) as Life does; scored holds (tick, bad, amount) per meal: bad = worth < 0, amount = |worth|."""

    dt = units.TICK
    seconds = True
    split = False                                        # a new sense (the user, 2026-11-12): each eye split across the corridor; a pulse's half
                                                         # arrives on line 2 or 3 (wired at random), alive from GROW, to brains with split_lines
    extra = False                                        # new parts (the user, 2026-11-12): two more thrusters a side, at EXTRA strengths, on
                                                         # motor lines 2 to 5 wired at random, alive from a moment drawn each life (GROW)
    muscle = False                                       # the muscle-like body (lab/sigmoid_body.py; the user, 2026-11-11): off by default
    instruments = True                                   # False: nothing recorded for the stage-5 labels (hand worlds already vetted)

    def __init__(self, seed, first, brain, world, stream=None, trace=False, seconds=None):
        if getattr(world, "fn", None) is None or getattr(world, "refused", None):
            raise Refused(f"this world can't be lived: {getattr(world, 'refused', None) or 'compiled only'}")
        self.secs = WLife.seconds if seconds is None else bool(seconds)
        self.dt = WLife.dt
        self.seed, self.world, self.first = seed, world, first
        self.rng = np.random.default_rng(seed)
        self.trng = np.random.default_rng(seed + 31_000_003)   # seconds mode: moments the engine draws (beats a brain gives none for, injected events)
        self.P = COLOURS.index(first)
        self.F = 1 - self.P
        self.poison = self.P
        self.brain = brain(seed)
        self.r = np.random.default_rng(seed + (world.stream if world.stream is not None else 7_000_000 + int(world.canon_stream())))
        self.RADIUS, self.WORLD, self.BODY, self.BLOCKS, self.EAT, self.SENSE, self.REACH, self.RANGE, self.RAYS, self.BLOCK, self.PUSH, self.TURN, self.DRAG = W0.RADIUS, W0.WORLD, W0.BODY, W0.BLOCKS, W0.EAT, W0.SENSE, W0.REACH, W0.RANGE, W0.RAYS, W0.BLOCK, W0.PUSH, W0.TURN, W0.DRAG
        self.COST, self.THRUST = 2.0, 1.0                # the score's: poison's cost, and firings' cost as a multiple of the standard
        self.now = 0.0
        world.fn["consts"](self)
        if not (self.COST > 0 and self.THRUST >= 0 and math.isfinite(self.COST) and math.isfinite(self.THRUST)):
            raise Refused(f"COST {self.COST}, THRUST {self.THRUST} at birth: poison must cost, a firing can't pay")
        self.COST0, self.THRUST0 = float(self.COST), float(self.THRUST)       # fixed at birth: the score uses these
        self.body = Body(self.rng, self)
        self.body.muscle = WLife.muscle
        s, m = (0, 1)[:: self.rng.choice((1, -1))], (0, 1)[:: self.rng.choice((1, -1))]
        self.wire_s, self.wire_m = list(s), list(m)      # colour -> sensor, thruster -> motor
        self.grow_at = None
        if WLife.extra:                                  # the new parts' wiring and growth, from their own stream (base lives unchanged)
            erng = np.random.default_rng(seed + 52_000_003)
            self.wire_m = self.wire_m + [int(2 + i) for i in erng.permutation(2 * len(EXTRA))]   # thrusters 2.. (left, right at each strength)
            self.grow_at = float(erng.uniform(*GROW))
            self.fire_weight = 0.0
        if WLife.split:                                  # the new sense's wiring, growth and draws, from its own stream
            self.srng = np.random.default_rng(seed + 53_000_011)
            self.wire_h = [int(2 + i) for i in self.srng.permutation(2)]          # half -> line
            self.split_at = float(self.srng.uniform(*GROW))
            if self.grow_at is not None:                 # both parts on: one growth event
                self.split_at = self.grow_at
        self.t = 0
        self.meals, self.firings, self.scored = [], [], []
        self.moving = None
        self.raw = None
        self.pending = []
        self._seq = 0
        self.tick_meals = []
        self.ended = False                               # never set: nothing in the language ends a life (instruments.frozen watches for it)
        self.tr = Trace() if trace else None
        self.tell = None                                 # a told arm's hook: called after the tick stage
        self.told_now = None                             # the told rule's value this tick, computed once, outside any brain call
        self._at = None                                  # seconds mode: the moment (within the tick) of the event being run
        self._cmd = None                                 # the brain's motor whose beat is being processed (instruments)
        self._sub = None                                 # seconds mode, while the body is sub-stepped: the heap of this tick's events
        self._bounced = set()
        self._fast = None                                # seconds mode: the streamlined tick (_step_fast), when the world allows it
        self._far = None
        self._K = None
        self._thrusts = []
        self._ipulses = []
        self.inst = Instruments(self) if WLife.instruments else NoInstruments()
        f = world.fn
        self.f_tick, self.f_see, self.f_pulse, self.f_fire, self.f_move, self.f_meal, self.f_respawn, self.f_score = (f.get("on_" + s) for s in ("tick", "see", "pulse", "fire", "move", "meal", "respawn", "score"))
        f["init"](self)
        if "on_birth" in f:
            f["on_birth"](self)
        self.inst.born()

    # ------------------------------------------------ what rules call
    def set_const(self, name, v):
        setattr(self, name, v)
        self._K = None
        if name in ("EAT", "RAYS", "BLOCK"):
            self.body.geometry()

    def later(self, d, fn):
        self._seq += 1
        if not self.secs:
            heapq.heappush(self.pending, (self.t + max(1, int(round(d / self.dt))), self._seq, fn, self._cmd))
            return
        due = self.now + max(0.0, float(d))             # seconds: exactly d after the moment it was scheduled
        t0 = self.t * self.dt
        if self._sub is not None and due < t0 + self.dt:
            heapq.heappush(self._sub, (due - t0, 2, self._seq, ("defer", fn, self._cmd)))
        else:
            heapq.heappush(self.pending, (due, self._seq, fn, self._cmd))

    def _run_overdue(self, t0):
        """Seconds mode, at a tick's start: the deferrals due by now (late ones run now). Those due later in the tick wait for the
        motion's heap (_due_in_tick), so each runs at its own moment (the checker, 2026-11-06: they had all run at the tick's start)."""
        while self.pending and self.pending[0][0] <= t0 + 1e-12:
            due, _, fn, cmd = heapq.heappop(self.pending)
            self.now, self._at = t0, 0.0
            self._run_later(fn, cmd)

    def _due_in_tick(self, ev, t0, dt):
        """Move the deferrals due within this tick into the motion's heap, at their moments."""
        while self.pending and self.pending[0][0] < t0 + dt - 1e-12:
            due, seq, fn, cmd = heapq.heappop(self.pending)
            ev.append((due - t0, 2, seq, ("defer", fn, cmd)))

    def _run_later(self, fn, cmd):
        was = self._cmd
        self._cmd = cmd
        try:
            fn(self)
        except Refused:
            raise
        except Exception as e:
            raise Refused(f"a rule raised a Python error in a deferral: {type(e).__name__}: {e}") from None
        self._cmd = was

    def _one_of_two(self, k, what):
        if isinstance(k, bool) or not isinstance(k, (int, float, np.integer, np.floating)) or k not in (0, 1):
            raise Refused(f"a rule named {what} {k}: only 0 or 1 exist")
        return int(k)

    def inject_pulse(self, eye):
        eye = self._one_of_two(eye, "eye")              # (an index like -1 reached the brain's own state: the checker, 2026-11-06)
        if not self.secs:
            at = self.r.random() * self.dt
            if self.tr is not None:
                self.tr.pulses.append((self.t, eye, -1, at, 1))
            self.brain.stimulate(eye, at)
            self.inst.pulse(eye)
            return
        if self._sub is not None:                        # during the body's motion: now, after the brain's step
            at = self._at
            if self.tr is not None:
                self.tr.pulses.append((self.t, eye, -1, at, 1))
            self.brain.stimulate(eye, at - self.dt)
            self.inst.pulse(eye)
        else:
            self._ipulses.append((self._at if self._at is not None else self.trng.random() * self.dt, eye))

    def inject_thrust(self, th):
        th = self._one_of_two(th, "thruster")
        if not self.secs or self._sub is not None:
            self.fire(th, 1.0, True)
        else:
            self._thrusts.append((self._at if self._at is not None else self.trng.random() * self.dt, th))

    def bset(self, b, x, y):
        w = self.WORLD
        b = int(b)
        old = self.body.xy[b].copy()
        self.body.xy[b] = (x % w, y % w)
        self.inst.placed(b, old)

    def hide(self, b):
        self.body.alive[int(b)] = False

    def show(self, b):
        b = int(b)
        was = bool(self.body.alive[b])
        self.body.alive[b] = True
        if not was:
            self.inst.placed(b, None)

    def respawn_now(self, b):
        b = int(b)
        old = self.body.xy[b].copy()
        if self.f_respawn is not None:
            nx, ny = self.f_respawn(self, b, 0.0, 0.0)
            self.body.xy[b] = (nx, ny)
        else:
            self.body.xy[b] = self.body.somewhere()
        self.inst.placed(b, old)

    def dist(self, x, y):
        w = self.WORLD
        dx, dy = (x - self.body.pos[0] + w / 2) % w - w / 2, (y - self.body.pos[1] + w / 2) % w - w / 2
        return math.sqrt(dx * dx + dy * dy)

    def wdist(self, a, b, c, d):
        w = self.WORLD
        dx, dy = (a - c + w / 2) % w - w / 2, (b - d + w / 2) % w - w / 2
        return math.sqrt(dx * dx + dy * dy)

    def _d2(self):
        B = self.body
        d = B.wrap(B.xy - B.pos)
        return (d * d).sum(1)

    def near(self, c, r):
        """How many live blocks of kind c (-1: any) lie within r of the creature."""
        B = self.body
        m = self._d2() < r * r
        m &= B.alive
        if c >= 0:
            m &= B.kind == c
        return int(m.sum())

    def nearest(self, c):
        """The nearest live block of kind c (-1: any), or -1."""
        B = self.body
        d = self._d2()
        m = B.alive if c < 0 else B.alive & (B.kind == c)
        if not m.any():
            return -1
        d[~m] = 1e18
        return int(np.argmin(d))

    # ------------------------------------------------ the interface by construction
    def _worth(self, w):
        lo, hi = WORTH_RANGE
        if isinstance(w, bool) or not isinstance(w, (int, float, np.floating, np.integer)) or not math.isfinite(w) or (w != 0 and not lo <= abs(w) <= hi):
            raise Refused(f"a meal's worth {w}, outside 0 and +-[{lo}, {hi}]")
        return float(w)

    def _score(self, b, c, worth):
        """A meal's score: its worth, and the score stage's state updates (it can read the worth, not write it)."""
        if self.f_score is not None:
            self.f_score(self, b, c, worth)
        self.scored.append((self.t, worth < 0, abs(worth)))
        if self.tr is not None:
            self.tr.meals.append((self.t, c, worth < 0, abs(worth), b, worth))

    # ------------------------------------------------ one tick
    def fire(self, th, gain, by_rule=False):
        """A thruster fires: it costs the creature whoever made it fire (the brain, or a world rule: a late or spurious thrust is the
        creature's own thruster firing). A command the world drops never reaches the thruster and costs nothing (the user, 2026-11-06:
        the break is between brain and thruster)."""
        if self.moving is None:
            self.moving = self.t
        self.body.fire(th, gain)
        self.firings.append((self.t, THRUSTERS[th % 2]))
        if self.grow_at is not None:                    # a firing costs in proportion to its thruster's strength
            self.fire_weight += 1.0 if th < 2 else EXTRA[th // 2 - 1]
        self.inst.fired(th, self._cmd)
        if self.tr is not None:
            self.tr.firings.append((self.t, th, self.wire_m[th], gain, int(by_rule)))

    def _told(self):
        f = self.world.fn.get("told")
        self.told_now = f(self) if f else self.poison

    def step(self):
        if self.secs:
            if self._fast is None:
                self._fast = (self.f_see is None and self.f_pulse is None and self.f_fire is None and self.f_move is None
                              and self.tr is None and not self.inst.on and not self.body.muscle and not WLife.extra and not WLife.split)
                self._hits = np.zeros((2, 4 * self.body.n + 8))
                if self._fast:
                    from stage2_lang.fast import FastModel
                    src = repr(getattr(self.world, "text", "")) + repr(getattr(self.world, "src", ""))
                    if isinstance(self.brain, FastModel) and not re.search(r"\(\s*(thrust|after)\b", src):
                        self._state = self.rng.bit_generator.ctypes.state_address
                        self._told_fn = self.world.fn.get("told")
                        self._pulses = np.zeros((3, 64))
                        self._H, self._FB, self._M = np.zeros(4), np.zeros(4096, np.int64), np.zeros(8)
                        self.step = self._step_fused
                        return self._step_fused()
                    self.step = self._step_fast                 # from now on, live() calls it directly
            return self._step_fast() if self._fast else self._step_seconds()
        dt = self.dt
        self.now = self.t * dt
        tr = self.tr
        while self.pending and self.pending[0][0] <= self.t:
            _, _, fn, cmd = heapq.heappop(self.pending)
            self._run_later(fn, cmd)
        if self.f_tick is not None:
            self.f_tick(self)
        self._told()
        if self.tell is not None:
            self.tell(self)
        if tr is not None:
            tr.poison.append(self.poison)
            tr.record(self)
        body, rng, brain = self.body, self.rng, self.brain
        seen, bykind = body.sees2(self.inst.on)
        if bykind is not None:
            self.inst.light(bykind)
        if self.f_see is not None:
            self.raw = seen.copy()
            for c in (0, 1):
                seen[c], = self.f_see(self, c, float(seen[c]))
        for c in (0, 1):
            for _ in range(rng.poisson(self.SENSE * seen[c] * dt)):
                eye = self.wire_s[c]
                at = rng.random() * dt
                if self.f_pulse is not None and self.f_pulse(self, eye, c)[0]:
                    if tr is not None:
                        tr.pulses.append((self.t, eye, c, at, 0))
                    continue
                if tr is not None:
                    tr.pulses.append((self.t, eye, c, at, 1))
                brain.stimulate(eye, at)
                self.inst.pulse(eye)
        motors = brain.step()
        if motors:
            for m in motors:
                self.inst.command(m)
            for th in (0, 1):
                m = self.wire_m[th]
                for _ in range(motors.count(m)):
                    gain = 1.0
                    self._cmd = m
                    if self.f_fire is not None:
                        gain, drop = self.f_fire(self, th, m, gain)
                        if drop:
                            if tr is not None:
                                tr.firings.append((self.t, th, m, 0.0, 0))
                            continue
                    self.fire(th, gain)
            self._cmd = None
        taste = self.move()
        self.t_score(taste)

    def move(self):
        """Body.move and then Life's meal loop, in stages (seconds=False)."""
        body = self.body
        dt = self.dt
        h0 = body.head()
        p0 = body.pos.copy()
        body.pos = (body.pos + body.speed * dt) % self.WORLD
        body.heading += body.spin * dt
        if self.f_move is not None:
            self.f_move(self)
        d = math.exp(-self.DRAG * dt)
        body.speed *= d
        body.spin *= d
        self.inst.moved(p0)
        taste = 0.0
        self.tick_meals = []
        if body.speed @ body.forward() <= 0:
            return taste
        eaten = _touching(body.xy, body.alive, h0, body.head(), self.WORLD, self.EAT)
        if not eaten:
            return taste
        kept = []
        for b in eaten:
            c = int(body.kind[b])
            worth = -1.0 if c == self.poison else 1.0
            drop = False
            if self.f_meal is not None:
                worth, drop = self.f_meal(self, b, c, worth)
            if drop:
                continue
            worth = self._worth(worth)
            kept.append((b, c, worth))
            self.respawn_now(b)
        for b, c, worth in kept:
            self.meals.append((self.t, COLOURS[c] if c < 2 else "decoy"))
            self.tick_meals.append((b, c, worth))
            taste += float(np.sign(worth))
        return taste

    def t_score(self, taste):
        """creature.Life's one taste a tick (seconds=False): the meals' signs summed and clipped, food and poison cancelling."""
        tr = self.tr
        if taste != 0.0:
            at = self.rng.random() * self.dt
            value = min(max(taste, -1.0), 1.0)
            if tr is not None:
                tr.tastes.append((self.t, value, at, 0))
            self.brain.taste(value, at)
        for b, c, worth in self.tick_meals:
            self._score(b, c, worth)
        self.inst.tick_end()
        self.t += 1

    # ------------------------------------------------ seconds mode
    def _step_seconds(self):
        dt = self.dt
        t0 = self.t * dt
        tr = self.tr
        self.now = t0
        self._run_overdue(t0)
        self.now, self._at = t0, None
        if self.f_tick is not None:
            self.f_tick(self)
        self._told()
        if self.tell is not None:
            self.tell(self)
        if tr is not None:
            tr.poison.append(self.poison)
            tr.record(self)
        body, rng, brain = self.body, self.rng, self.brain
        seen, bykind = body.sees2(self.inst.on)
        if bykind is not None:
            self.inst.light(bykind)
        if self.f_see is not None:
            self.raw = seen.copy()
            for c in (0, 1):
                seen[c], = self.f_see(self, c, float(seen[c]))
        pulses = [(rng.random() * dt, self.wire_s[c], c) for c in (0, 1) for _ in range(rng.poisson(self.SENSE * seen[c] * dt))]
        pulses += [(at, eye, -1) for at, eye in self._ipulses]
        self._ipulses = []
        for at, eye, c in sorted(pulses):
            self.now, self._at = t0 + at, at
            if c >= 0 and self.f_pulse is not None and self.f_pulse(self, eye, c)[0]:
                if tr is not None:
                    tr.pulses.append((self.t, eye, c, at, 0))
                continue
            if tr is not None:
                tr.pulses.append((self.t, eye, c, at, 1))
            brain.stimulate(eye, at)
            if WLife.split and c >= 0 and getattr(brain, "split_lines", False) and t0 + at >= self.split_at:
                hv = self._halves if getattr(self, "_halves_t", None) == self.t else None
                if hv is None:
                    hv, self._halves_t = body.halves(), self.t
                    self._halves = hv
                sL, sR = hv[0][c], hv[1][c]                # the pulse's half, by each half's share of this colour's light
                half = 0 if self.srng.random() * (sL + sR) < sL else 1
                brain.stimulate(self.wire_h[half], at)
            self.inst.pulse(eye)
        self.now, self._at = t0, None
        motors = brain.step() or []
        beats = getattr(brain, "beats", None)
        if beats is None or sorted(m for m, _ in beats) != sorted(motors):
            beats = [(m, self.trng.random() * dt) for m in motors]
        for m, _ in beats:
            self.inst.command(m)
        ev = [(min(max(at, 0.0), dt * (1 - 1e-12)), 1, i, ("beat", m)) for i, (m, at) in enumerate(beats)]
        ev += [(at, 1, 10_000 + i, ("thrust", th)) for i, (at, th) in enumerate(self._thrusts)]
        self._thrusts = []
        self._due_in_tick(ev, t0, dt)
        heapq.heapify(ev)
        if self.f_move is not None:
            self.f_move(self)
        self.tick_meals = []
        self._sub = ev
        p0 = body.pos.copy()
        cur = 0.0
        while ev or cur < dt:
            if not ev:
                self._advance(cur, dt)
                cur = dt
                continue                                # (a meal in that last stretch may have scheduled one more)
            at, _, _, (kind, *x) = heapq.heappop(ev)
            at = max(at, cur)                           # never back in time: one due before the moment reached runs now
            self._advance(cur, at)
            cur = at
            self.now, self._at = t0 + at, at
            if kind == "beat":
                m = x[0]
                for th in range(len(self.wire_m)):
                    if self.wire_m[th] != m:
                        continue
                    if th >= 2 and t0 + at < self.grow_at:  # not yet grown: the command reaches nothing, and costs nothing
                        continue
                    gain = 1.0
                    self._cmd = m
                    if self.f_fire is not None:
                        gain, drop = self.f_fire(self, th, m, gain)
                        if drop:
                            if tr is not None:
                                tr.firings.append((self.t, th, m, 0.0, 0))
                            continue
                    self.fire(th, gain)
                self._cmd = None
            elif kind == "thrust":
                self.fire(x[0], 1.0, True)
            else:
                self._run_later(x[0], x[1])
        self._sub = None
        self.now, self._at = t0, None
        self.inst.moved(p0)
        self.inst.tick_end()
        self.t += 1

    def _step_fast(self):
        """_step_seconds for a world with no rule at see, pulse, fire or move, nothing traced and no instruments: the same steps in the
        same order with the same draws, its motion and light compiled (lab/speed_fingerprint.py checks it)."""
        dt = self.dt
        t0 = self.t * dt
        self.now = t0
        self._run_overdue(t0)
        self.now, self._at = t0, None
        if self.f_tick is not None:
            self.f_tick(self)
        self._told()
        if self.tell is not None:
            self.tell(self)
        body, rng, brain = self.body, self.rng, self.brain
        hx, hy = body.head_xy()
        K = self._K
        if K is None:
            K = self._K = np.array([self.WORLD, self.BLOCK, self.RANGE, self.EAT, body.share, self.REACH, self.DRAG, self.RADIUS,
                                    self.PUSH, self.TURN], float)
            self._far = np.zeros((2, body.across.shape[0]))
        s0, s1 = _see(body.xy, body.alive, body.look, body.bright, body.across, K, self._far, hx, hy, body._fc, body._fs)
        n0 = rng.poisson(self.SENSE * s0 * dt)
        pulses = [(rng.random() * dt, self.wire_s[0], 0) for _ in range(n0)] if n0 else []
        n1 = rng.poisson(self.SENSE * s1 * dt)
        if n1:
            pulses += [(rng.random() * dt, self.wire_s[1], 1) for _ in range(n1)]
        if self._ipulses:
            pulses += [(at, eye, -1) for at, eye in self._ipulses]
            self._ipulses = []
        if pulses:
            for at, eye, c in sorted(pulses):
                self.now, self._at = t0 + at, at
                brain.stimulate(eye, at)
            self.now, self._at = t0, None
        motors = brain.step() or []
        beats = getattr(brain, "beats", None)
        if beats is None or ((motors or beats) and sorted(m for m, _ in beats) != sorted(motors)):
            beats = [(m, self.trng.random() * dt) for m in motors]
        self.tick_meals = []
        ev = [(min(max(at, 0.0), dt * (1 - 1e-12)), 1, i, ("beat", m)) for i, (m, at) in enumerate(beats)] if beats else []
        if self._thrusts:
            ev += [(at, 1, 10_000 + i, ("thrust", th)) for i, (at, th) in enumerate(self._thrusts)]
            self._thrusts = []
        if self.pending:
            self._due_in_tick(ev, t0, dt)
        heapq.heapify(ev)
        self._sub = ev
        cur = 0.0
        while ev or cur < dt:                           # as _step_seconds: never back in time, nothing added late is lost
            if not ev:
                self._advance_fast(cur, dt)
                cur = dt
                continue
            at, _, _, (kind, *x) = heapq.heappop(ev)
            at = max(at, cur)
            self._advance_fast(cur, at)
            cur = at
            self.now, self._at = t0 + at, at
            if kind == "beat":
                m = x[0]
                for th in (0, 1):
                    if self.wire_m[th] != m:
                        continue
                    self._cmd = m
                    self.fire(th, 1.0)
                self._cmd = None
            elif kind == "thrust":
                self.fire(x[0], 1.0, True)
            else:
                self._run_later(x[0], x[1])
        self._sub = None
        self.now, self._at = t0, None
        self.t += 1

    def _step_fused(self):
        """_step_fast with the light and draws (_sense), and the brain, beats and motion (_tick_b), compiled: the same steps, order and
        draws (lab/speed_fingerprint.py checks). Falls back to _step_fast for a tick with an injected thrust."""
        if self._thrusts or self._ipulses or self.pending or not self.brain._packed:
            return self._step_fast()                    # (a thrust or deferral rule sends the whole life to _step_fast: see step)
        dt = self.dt
        t0 = self.t * dt
        self.now = t0
        self._run_overdue(t0)
        self.now, self._at = t0, None
        if self.f_tick is not None:
            self.f_tick(self)
        f = self._told_fn
        self.told_now = f(self) if f else self.poison  # (_told)
        if self.tell is not None:
            self.tell(self)
        if self._thrusts:
            raise ValueError("the tick stage injected a thrust: not handled by the fused tick")
        body, brain = self.body, self.brain
        h = body.heading                                # (body.head_xy)
        if h != body._fh:
            body._fh, body._fc, body._fs, body._fv = h, math.cos(h), math.sin(h), None
        R = self.RADIUS
        hx, hy = body.pos[0] + body._fc * R, body.pos[1] + body._fs * R
        K = self._K
        if K is None:
            K = self._K = np.array([self.WORLD, self.BLOCK, self.RANGE, self.EAT, body.share, self.REACH, self.DRAG, self.RADIUS,
                                    self.PUSH, self.TURN], float)
            self._far = np.zeros((2, body.across.shape[0]))
        P = self._pulses
        n = _sense(body.xy, body.alive, body.look, body.bright, body.across, K, self._far, hx, hy, body._fc, body._fs, self._state,
                   dt, self.SENSE, self.wire_s[0], self.wire_s[1], P)
        if n < 0:                                       # a rate the compiled draw doesn't cover: numpy's own, in Python, the same order
            s0, s1, rng = float(P[0, 0]), float(P[0, 1]), self.rng
            pulses = [(rng.random() * dt, self.wire_s[0], 0) for _ in range(rng.poisson(self.SENSE * s0 * dt))]
            pulses += [(rng.random() * dt, self.wire_s[1], 1) for _ in range(rng.poisson(self.SENSE * s1 * dt))]
            n = 0
        else:
            pulses = None
        if n or self._ipulses or pulses:
            pulses = (pulses or []) + list(zip(P[0, :n].tolist(), [int(x) for x in P[1, :n]], [int(x) for x in P[2, :n]]))
            if self._ipulses:
                pulses += [(at, eye, -1) for at, eye in self._ipulses]
                self._ipulses = []
            for at, eye, c in sorted(pulses):
                self.now, self._at = t0 + at, at
                brain.stimulate(eye, at)
            self.now, self._at = t0, None
        self.tick_meals = []
        self._sub = []
        H, M = self._H, self._M
        H[0], H[1], H[2], H[3] = body.heading, body.spin, body._fc, body._fs
        M[0], M[6] = -1.0, 1.0 if self._bounced else 0.0
        b = brain
        args = (b._S, b._Q, b._E, b._I, b._F, b._nev, b._dt, b._flags, body.pos, body.speed, H, body.xy, body.alive, K, self._hits,
                self._FB, M, self.wire_m[0], self.wire_m[1])
        k = _tick_b(*args)
        b._nev = 0                                      # fast.FastModel.fast_step's bookkeeping
        S = b._S
        if k & 1:
            if b._flags[0]:
                b.on_at.append(S[0] - dt)
            if b._flags[1]:
                b.trace.append((S[0], S[7]))
            if b._flags[2]:
                S[33] = b._rng_db.standard_normal()
        k >>= 1
        b.t = S[0]
        while True:
            body.heading, body.spin = H[0], H[1]
            body._fh, body._fc, body._fs, body._fv = H[0], H[2], H[3], None
            nf = int(M[7])
            if nf:
                if self.moving is None:
                    self.moving = self.t
                for th in self._FB[:nf].tolist():
                    self.firings.append((self.t, THRUSTERS[th]))
                M[7] = 0
            if M[5]:
                self._bounced = set()
                M[5] = 0
            if k == 0:
                break
            a, dtau = M[3], M[4]
            touched = set()
            hits = self._hits
            for u, blk in sorted(zip(hits[0, :k].tolist(), [int(x) for x in hits[1, :k]])):
                touched.add(blk)
                if blk in self._bounced or not body.alive[blk]:
                    continue
                self._meal(blk, a + u * dtau)
            self._bounced &= touched
            if self._sub:
                raise ValueError("a deferral due inside this tick, from a meal: not handled by the fused tick")
            M[6] = 1.0 if self._bounced else 0.0
            h = body.heading                            # a meal's rule may have moved the body
            if h != body._fh:
                body._fh, body._fc, body._fs, body._fv = h, math.cos(h), math.sin(h), None
            H[0], H[1], H[2], H[3] = h, body.spin, body._fc, body._fs
            k = _tick_b(*args) >> 1
        self._sub = None
        self.now, self._at = t0, None
        self.t += 1

    def _advance_fast(self, a, b):
        """_advance, its motion compiled (_move)."""
        dtau = b - a
        if dtau <= 0:
            return
        body = self.body
        h = body.heading
        if h != body._fh:
            body._fh, body._fc, body._fs, body._fv = h, math.cos(h), math.sin(h), None
        K = self._K
        if K is None:
            K = self._K = np.array([self.WORLD, self.BLOCK, self.RANGE, self.EAT, body.share, self.REACH, self.DRAG, self.RADIUS,
                                    self.PUSH, self.TURN], float)
            self._far = np.zeros((2, body.across.shape[0]))
        hd, sp, c, s, n = _move(body.pos, body.speed, body.xy, body.alive, K, self._hits, h, body.spin, body._fc, body._fs, dtau)
        body.heading, body.spin = hd, sp
        body._fh, body._fc, body._fs, body._fv = hd, c, s, None
        if n:
            touched = set()
            for u, blk in sorted(zip(self._hits[0, :n].tolist(), [int(x) for x in self._hits[1, :n]])):
                touched.add(blk)
                if blk in self._bounced or not body.alive[blk]:
                    continue
                self._meal(blk, a + u * dtau)
            self._bounced &= touched
        elif self._bounced:
            self._bounced = set()

    def _advance(self, a, b):
        """The body from moment a to b of this tick: exactly (drag an exponential) for world.py's body; for the muscle-like body
        (WLife.muscle), in sub-steps of at most MUSCLE_STEP while a thruster's activation lasts, its sigmoid thrust applied at each."""
        body = self.body
        if body.muscle and any(x > 1e-4 for x in body.act):
            import sigmoid_body as SB
            n = max(1, int(math.ceil((b - a) / MUSCLE_STEP - 1e-9)))
            h = (b - a) / n
            fp, ft = SB.F_PUSH * self.PUSH / W0.PUSH, SB.F_TURN * self.TURN / W0.TURN
            dec = math.exp(-h / SB.TAU_A)
            for i in range(n):
                if len(body.act) == 2:
                    f0, f1 = body.kg[0] * SB.f_of(body.act[0]), body.kg[1] * SB.f_of(body.act[1])
                else:                                   # every thruster on its side (even: the left, as thruster 0)
                    f0 = sum(body.kg[j] * SB.f_of(body.act[j]) for j in range(0, len(body.act), 2))
                    f1 = sum(body.kg[j] * SB.f_of(body.act[j]) for j in range(1, len(body.act), 2))
                fw = body.forward()
                body.speed[0] += (f0 + f1) * fp * h * fw[0]
                body.speed[1] += (f0 + f1) * fp * h * fw[1]
                body.spin += (f1 - f0) * ft * h          # the left thruster (0) turns it right, as fire()
                for j in range(len(body.act)):
                    body.act[j] *= dec
                self._advance_exact(a + i * h, a + (i + 1) * h)
            return
        self._advance_exact(a, b)

    def _advance_exact(self, a, b):
        dtau = b - a
        if dtau <= 0:
            return
        body = self.body
        D = self.DRAG
        e = math.exp(-D * dtau)
        f = (1 - e) / D if D > 0 else dtau
        h0 = body.head_xy()
        pos, sp, w = body.pos, body.speed, self.WORLD
        pos[0], pos[1] = (pos[0] + sp[0] * f) % w, (pos[1] + sp[1] * f) % w
        body.heading += body.spin * f
        sp[0], sp[1] = sp[0] * e, sp[1] * e
        body.spin *= e
        touched = set()
        h1 = body.head_xy()
        if sp[0] * body._fc + sp[1] * body._fs > 0:
            bs, us = _touching_u(body.xy, body.alive, h0, h1, self.WORLD, self.EAT)
            for u, blk in sorted(zip(us, bs)):
                touched.add(blk)
                if blk in self._bounced or not body.alive[blk]:
                    continue
                self._meal(blk, a + u * dtau)
        self._bounced &= touched                        # a block left uneaten stays one touch while the contact lasts

    def _meal(self, b, at):
        body = self.body
        t0 = self.t * self.dt
        self.now, self._at = t0 + at, at
        c = int(body.kind[b])
        worth = -1.0 if c == self.poison else 1.0
        if self.f_meal is not None:
            worth, drop = self.f_meal(self, b, c, worth)
            if drop:
                self._bounced.add(b)
                return
        worth = self._worth(worth)
        self.respawn_now(b)
        self.meals.append((self.t, COLOURS[c] if c < 2 else "decoy"))
        self.tick_meals = [(b, c, worth)]               # what an arm's spy reads: this meal
        if worth != 0:
            v = 1.0 if worth > 0 else -1.0
            if self.tr is not None:
                self.tr.tastes.append((self.t, v, at, 0))
            self.brain.taste(v, at - self.dt)           # (the brain has stepped to the tick's end: the meal was dt - at before)
        self._score(b, c, worth)

    # ------------------------------------------------ the score
    def thirds(self, ticks):
        """minimal.spec.thirds, each meal's amount counted: (food, poison, seconds) after moving began, by third, then (0, 0, seconds
        before). Poison weighed by COST as fixed at birth."""
        start = self.moving if self.moving is not None else ticks
        out = []
        k = self.COST0 / 2.0
        for i in range(3):
            a, z = start + i * (ticks - start) / 3, start + (i + 1) * (ticks - start) / 3
            food = sum(am for t, b, am in self.scored if a <= t < z and not b)
            bad = sum(am for t, b, am in self.scored if a <= t < z and b)
            out.append((food, bad * k if k != 1.0 else bad, (z - a) * self.dt))
        return out + [(0, 0, start * self.dt)]


class NoInstruments:
    """Nothing recorded: every hook a no-op (WLife.instruments = False)."""
    on = False
    E = ()
    placed_t = ()

    def __getattr__(self, name):
        return _noop


def _noop(*a, **k):
    return None


class Instruments:
    """Watching only: what lab/stage2_lang/instruments.py needs to label a life's stage-5 kinds, recorded each tick. Nothing feeds back,
    and nothing draws."""

    def __init__(self, W):
        self.W = W
        self.E, self.L, self.C, self.A = [], [], [], []   # per tick: pulses to each eye; light at each eye by kind; beats of each motor; firings of each thruster
        self.disp, self.alive, self.placed_t = [], [], []
        self._e, self._c, self._a, self._l = [0, 0], [0, 0], [0, 0], (0.0, 0.0)
        self.on = True

    def born(self):
        self.wire_s, self.wire_m = list(self.W.wire_s), list(self.W.wire_m)

    def light(self, bykind):
        self._l = (float(bykind[0]), float(bykind[1]))

    def pulse(self, eye):
        self._e[eye] += 1

    def command(self, m):
        self._c[m] += 1

    def fired(self, th, cmd):
        self._a[th] += 1

    def moved(self, p0):
        self._disp = float(np.linalg.norm(self.W.body.wrap(self.W.body.pos - p0)))

    def placed(self, b, old):
        """A block appearing (shown) or moved by more than EAT at once, within the body's own exclusion zone (3 EAT + BODY of the
        creature), which the body's respawn never does."""
        W = self.W
        if not hasattr(W, "body"):
            return
        B = W.body
        if old is not None and np.linalg.norm(B.wrap(B.xy[b] - old)) <= W.EAT:
            return
        if B.alive[b] and np.linalg.norm(B.wrap(B.xy[b] - B.pos)) <= 3 * W.EAT + W.BODY:
            self.placed_t.append(W.t)

    def tick_end(self):
        self.E.append(tuple(self._e))
        self.L.append(self._l)
        self.C.append(tuple(self._c))
        self.A.append(tuple(self._a))
        self.disp.append(getattr(self, "_disp", 0.0))
        self.alive.append(int(self.W.body.alive.sum()))
        self._e, self._c, self._a = [0, 0], [0, 0], [0, 0]


class Trace:
    """Watching only: what an instrument reads, independently of the rule. Nothing here feeds back."""

    def __init__(self):
        self.poison = []
        self.pulses, self.firings, self.tastes, self.meals = [], [], [], []
        self.state = []
        self.pos, self.head, self.alive = [], [], []
        self.K = []

    def record(self, W):
        b = W.body
        self.pos.append((b.pos[0], b.pos[1], b.heading, b.spin, b.speed[0], b.speed[1]))
        self.alive.append(int(b.alive.sum()))
        self.K.append((W.PUSH, W.TURN, W.DRAG, W.EAT, W.SENSE))
