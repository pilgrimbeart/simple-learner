"""arena.py: robots that eat each other (the user's idea, 2026-10-30; QUESTIONS.md, the plan, 6). No blocks: N robots,
each the creature's disc (the user's decision, 2026-10-31: the triangle's five colliding discs hooked each other as
robots turned past), radius RB (world.RADIUS), its front half red (the mouth's side) and its rear half blue (the tail), its mouth the front point of
its rim, its two thrusters on its rear rim (world.Body.thrusters; world.Body's physics: a firing adds forward speed and a turn
away from its side). Two eyes (the user's decision, 2026-10-30), each a fan of EYE_RAYS rays from the mouth out to its
own side (FAN), seeing the colour of the half each ray meets first, as the creature's eye did (each ray's hit counts
more the nearer it is), so four sensors: the body draws at random which colour feeds which pair, and which of a pair is the left eye. Two motors
(thruster -> motor at random), one taste.

- Eating takes time: while a robot's mouth touches another's rear (blue) half, energy flows from the bitten to the biter at
  BITE meals a second; the biter tastes +1 each tick of it, the bitten -1 (pain as bad taste, the poison's signal:
  the user's decision, 2026-10-30). Mouth to mouth, nothing happens.
- A belly: born with BELLY meals, drained by resting (spec.NEED per SPAN) and firing (spec.THRUST a firing); empty is
  death, and a newborn (a fresh brain, its own wiring) appears at random at once: N stay alive.
- Slower than the creature (the user's decision, 2026-10-30): each thruster pushes a third as hard (PUSH), so top
  speed is a third, turning as before.
- Collisions: overlapping discs push apart along the line between their centres, a soft spring (K, on speed), slow
  against the tick; frictionless, so a push never spins a robot.

    python arena.py [SEEDS] [seconds=300] [n=10] [kinds=B,told,tracker]   (kinds: each robot's brain, in turn)"""
import math
import sys
import numpy as np
from numba import njit
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import world as W
from discrete import model as M
from minimal.spec import NEED, SPAN, THRUST
from units import MILLI, TICK

RB = W.RADIUS                                           # m: a robot's radius, the creature's
BELLY = 20.0                                            # meals at birth
BITE = 1.0                                              # meals a second through a bite
K = 3000.0                                              # per s^2: a disc's push on speed per m of overlap
PUSH = W.PUSH / 3                                       # m/s a firing adds: a third of the creature's
TOUCH = 0.3 * MILLI                                     # a mouth this near another's rim bites (if on its rear half)
EYE_RAYS = 12
FAN = (math.radians(-5), math.radians(40))              # each eye's rays, from just across the middle out to its side
LEFT = np.linspace(*FAN, EYE_RAYS)                      # (angles from forward, counterclockwise: the left)
HIT = 0.25                                              # a ray's hit at the eye counts this much (4 rays: full)


@njit(cache=True)
def _eyes(P, hd, angles, RB, RANGE, REACH, HIT):
    """Every robot's two fans at once (P: centres, hd: headings), each ray from the mouth stopping at the first disc it
    meets and seeing the colour of the half it meets (front red 0, rear blue 1): (n, eye 0 left 1 right, colour)."""
    n = P.shape[0]
    out = np.zeros((n, 2, 2))
    for i in range(n):
        mx, my = P[i, 0] + RB * math.cos(hd[i]), P[i, 1] + RB * math.sin(hd[i])
        for e in range(2):
            for a in angles:
                a = a if e == 0 else -a
                ux, uy = math.cos(hd[i] + a), math.sin(hd[i] + a)
                best, k = RANGE, -1
                for b in range(n):
                    if b == i:
                        continue
                    dx = (P[b, 0] - mx + 0.03) % 0.06 - 0.03
                    dy = (P[b, 1] - my + 0.03) % 0.06 - 0.03
                    t = dx * ux + dy * uy
                    e2 = dx * dx + dy * dy - t * t
                    if t > -RB and e2 < RB * RB:
                        d = max(0.0, t - math.sqrt(RB * RB - e2))
                        if d < best:            # where it meets the rim, against that robot's centre and heading
                            hx, hy = d * ux - dx, d * uy - dy
                            best = d
                            k = 0 if hx * math.cos(hd[b]) + hy * math.sin(hd[b]) >= 0 else 1
                if k >= 0:
                    out[i, e, k] += HIT / (1 + (best / REACH) ** 2)
    return np.minimum(out, 1.0)


class AdaptB(M.Model):
    """B with two eyes: each colour's pair of sensors summed (which two sensors share a colour is the brain's anatomy),
    so it behaves as B did: it can't steer towards a side."""

    def stimulate(self, sensor, at):
        super().stimulate(sensor // 2, at)


class Tracker(AdaptB):
    """A Braitenberg tracker, hand-built to certify the arena (told its wiring and the colour, learning off): while
    driving, the thruster that turns it towards the side whose eye sees more of a tail fires more."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.L = self.Rt = 0.0

    def stimulate(self, sensor, at):
        if sensor == self.p["left_food"]:
            self.L += 1
        elif sensor == self.p["right_food"]:
            self.Rt += 1
        super().stimulate(sensor, at)

    def step(self):
        p = self.p
        a = TICK / p.get("tau_s", 0.2)
        bias = (self.L - self.Rt) / (self.L + self.Rt + 1e-9)   # + : the tail is to the left
        g = p.get("gain", 0.1) * bias
        turn_left = p["right_motor"]                    # (the right thruster turns it left)
        p["g0"], p["g1"] = (1 + g, 1 - g) if turn_left == 0 else (1 - g, 1 + g)
        self.L *= 1 - a
        self.Rt *= 1 - a
        return super().step()


class Robot:
    def __init__(self, rng, seed, p, spread, t, kind="B"):
        self.body = W.Body(rng)
        self.body.pos = rng.uniform(0, W.WORLD, 2)
        self.body.xy = np.zeros((0, 2))                 # (no blocks of its own)
        pairs, m = (0, 1)[:: rng.choice((1, -1))], (0, 1)[:: rng.choice((1, -1))]
        self.sensor = {}                                # (colour, eye) -> sensor
        for c, pr in zip(W.COLOURS, pairs):
            o = (0, 1)[:: rng.choice((1, -1))]
            self.sensor[(c, "left")], self.sensor[(c, "right")] = 2 * pr + o[0], 2 * pr + o[1]
        self.motor = dict(zip(W.THRUSTERS, m))
        self.kind = kind
        q = M.drawn(p, spread, seed)
        if kind in ("told", "tracker"):                 # told the colour, learning off
            q["step"] = 0.0
        if kind == "tracker":
            q.update(left_food=self.sensor[("blue", "left")], right_food=self.sensor[("blue", "right")],
                     right_motor=self.motor["right"])
        self.brain = (Tracker if kind == "tracker" else AdaptB)(seed, q)
        if kind in ("told", "tracker"):
            self.brain.food = self.sensor[("blue", "left")] // 2
        self.belly, self.born, self.seed = BELLY, t, seed
        self.ate = self.lost = 0.0
        self.firings = 0

    def mouth(self):
        """The front point of its rim."""
        return self.body.head()

    def thrusters(self):
        """Watching only: where its thrusters sit on its rear rim, left then right."""
        return self.body.thrusters()


class Arena:
    def __init__(self, seed, n=10, kinds=("B",)):
        self.rng = np.random.default_rng(seed)
        self.kinds = [kinds[i % len(kinds)] for i in range(n)]
        self.p, self.spread = M.from_bench()
        self.next_seed = seed * 1000
        self.t = 0.0
        self.robots = [self._newborn(k) for k in self.kinds]
        self.dead = []                                  # (robot, t)

    def _newborn(self, kind):
        self.next_seed += 1
        return Robot(self.rng, self.next_seed, self.p, self.spread, self.t, kind)

    def step(self):
        rs = self.robots
        # eyes: each robot's two fans see the others' discs
        hd = np.array([r.body.heading for r in rs])
        P = np.array([r.body.pos for r in rs])
        seen = _eyes(P, hd, LEFT, RB, W.RANGE, W.REACH, HIT)
        counts = self.rng.poisson(W.SENSE * seen * TICK)
        for i, e, k in zip(*np.nonzero(counts)):
            r = rs[i]
            for _ in range(counts[i, e, k]):
                r.brain.stimulate(r.sensor[(W.COLOURS[k], ("left", "right")[e])], self.rng.random() * TICK)
        # brains, thrusters, spending
        for r in rs:
            out = r.brain.step()
            fired = [f for f in W.THRUSTERS for _ in range(out.count(r.motor[f]))]
            for f in fired:
                r.body.fire(f)
                r.body.speed -= (W.PUSH - PUSH) * r.body.forward()   # (a third of the push)
            r.firings += len(fired)
            r.belly -= NEED / SPAN * TICK + THRUST * len(fired)
        # collisions: soft springs between overlapping discs (all pairs at once), along the line of centres
        P = np.array([r.body.pos for r in rs])
        d = W.Body.wrap(P[:, None, :] - P[None, :, :])
        dist = np.hypot(d[..., 0], d[..., 1])
        o = np.where((dist < 2 * RB) & (dist > 0), 2 * RB - dist, 0.0)
        if o.any():
            push = (o[..., None] * d / np.maximum(dist, 1e-12)[..., None]).sum(axis=1)
            for k, r in enumerate(rs):
                r.body.speed += K * push[k] * TICK
        # move (the bodies have no blocks: move() eats nothing)
        for r in rs:
            r.body.move()
        # bites: a mouth touching another's rim on its rear half
        hd = np.array([r.body.heading for r in rs])
        P = np.array([r.body.pos for r in rs])
        F = np.stack([np.cos(hd), np.sin(hd)], 1)
        gap = W.Body.wrap((P + F * RB)[:, None, :] - P[None, :, :])   # mouth i from centre j
        near = (np.hypot(gap[..., 0], gap[..., 1]) < RB + TOUCH) & ((gap * F[None, :, :]).sum(-1) < 0)
        np.fill_diagonal(near, False)
        for i, j in np.argwhere(near):                  # (in the order of the loops over a, then b, as before)
            a, b = rs[i], rs[j]
            e = min(BITE * TICK, max(b.belly, 0.0))
            b.belly -= e
            b.lost += e
            a.belly += e
            a.ate += e
            a.brain.taste(1.0, self.rng.random() * TICK)
            b.brain.taste(-1.0, self.rng.random() * TICK)
        # deaths, and newborns in their place
        for k, r in enumerate(rs):
            if r.belly <= 0:
                self.dead.append((r, self.t))
                rs[k] = self._newborn(r.kind)
        self.t += TICK


def run(job):
    """(seed, seconds, n, kinds) -> per robot that lived 20 s or more: (kind, ate and lost a 10 s, age, believes blue)."""
    seed, seconds, n, kinds = job
    A = Arena(seed, n, kinds)
    for _ in range(int(seconds / TICK)):
        A.step()
    out = []
    for r, died in [(r, A.t) for r in A.robots] + A.dead:
        age = died - r.born
        if age >= 20:
            out.append((r.kind, r.ate / age * 10, r.lost / age * 10, age,
                        r.brain.food == r.sensor[("blue", "left")] // 2))
    return out


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    args = [a for a in sys.argv[1:] if "=" not in a]
    kw = dict(a.split("=") for a in sys.argv[1:] if "=" in a)
    kinds = tuple(kw.get("kinds", "B").split(","))
    seeds = range(*(int(x) for x in (args[0] if args else "0:8").split(":")))
    with ProcessPoolExecutor() as ex:
        rows = [x for res in ex.map(run, [(s, float(kw.get("seconds", 300)), int(kw.get("n", 10)), kinds)
                                          for s in seeds]) for x in res]
    for k in kinds:
        x = [r for r in rows if r[0] == k]
        ate = np.array([r[1] for r in x])
        boot = [ate[np.random.default_rng(i).integers(len(ate), size=len(ate))].mean() for i in range(1000)]
        print(f"{k:8s}: {len(x)} robots, ate {ate.mean():.2f} [{np.percentile(boot, 2.5):.2f}, "
              f"{np.percentile(boot, 97.5):.2f}] a 10 s, lost {np.mean([r[2] for r in x]):.2f}, age "
              f"{np.mean([r[3] for r in x]):.0f} s, believing tails food {np.mean([r[4] for r in x]):.0%}")
