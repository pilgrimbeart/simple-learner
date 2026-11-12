"""newparts.py: a brain that takes up new parts (PROGRAMME.md, Next; the user, 2026-11-12). Step G1, the yardstick: is there anything to
gain from the new thrusters (two more a side, at a half and a quarter of the original's strength; sim.WLife.extra)? Hand-designed brains,
told the wiring (a yardstick's privilege), route the starting brain's beats to the new thrusters in obvious ways; for this question the
parts are alive from birth (sim.GROW set to 0). Efficiency in the last third of 300 s lives, as D42, on plain and lopsided bodies, and touching pairs (D41, 2 mm).

Designs: base (the original thrusters only); scanQ (the scan on the same side's quarter thruster at 4 times the rate: a finer sweep at the
same speed); scanH (on the half at twice); driveH (drive and run on the two half thrusters at twice the rate: finer steering, the same
speed); driveQ (the quarters at 4 times); fine (scanQ and driveH). On lopsided bodies every design is also told its balance.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/newparts.py yardstick [PAIRS]"""
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import bodyladder as BL
import ladders as L
import stage3_random as R

SEEDS0 = 102000
D = "(pow 2 (uniform -1 1))"
import pairs as PR
WORLDS = {"plain": "(world)", "pairs2": PR.world(2.0),
          "lopsided": f"(world {BL.M} (let a {D}) (let b {D}) (on fire (set gain (if (= (mod thruster 2) 0) a b))))"}   # per side, every size
DESIGNS = {"base": (None, 1, None, 1), "scanQ": ("Q", 4, None, 1), "scanH": ("H", 2, None, 1),
           "driveH": (None, 1, "H", 2), "driveQ": (None, 1, "Q", 4), "fine": ("Q", 4, "H", 2),
           "splitBig": (None, 1, None, 1, "big"), "splitH": (None, 1, None, 1, "H"), "splitQ": (None, 1, None, 1, "Q"),
           "splitQ+driveH": (None, 1, "H", 2, "Q")}      # (scan size, x, drive size, x[, steer: the split eye's reflex, told the map])


def _init():
    R._init(0.0025, False)
    from stage2_lang import sim
    sim.WLife.extra = True
    sim.WLife.split = True
    sim.GROW = (0.0, 0.0)                               # the yardstick: the parts from birth


STEER_W, STEER_N, STEER_Q, LAG = 0.2, 1, 1, 0.01        # D24's reflex: N or more food pulses from one half in W s, Q or fewer from the
                                                        # other; with the big thruster its partner LAG s later (about 7 degrees)


def steered(cls):
    """D24's steering reflex, told the map: while driving, food pulses mostly from one half turn the body towards it: with the big
    thruster (a drive pair's beat on the turning side, its partner LAG later) or one small kick (a half or a quarter) on that side."""
    class Steered(routed(cls)):
        split_lines = True
        steer, half_of_line, recent, last_c, pend = None, None, None, None, None

        def stimulate(self, sensor, at):
            if sensor >= 2:
                if self.steer and self.last_c == self.food:
                    self.recent.append((self.t + at, self.half_of_line[sensor]))
                return
            self.last_c = sensor
            super().stimulate(sensor, at)

        def step(self):
            out = super().step()
            if not self.steer:
                return out
            beats = list(getattr(self, "beats", None) or [])
            due = [(m, max(0.0, at)) for m, at, t in self.pend if t <= self.t]
            self.pend = [x for x in self.pend if x[2] > self.t]
            driving = self.t - self.last_drive < self.p["hold"]
            self.recent = [x for x in self.recent if x[0] > self.t - STEER_W]
            n = [sum(1 for _, h in self.recent if h == k) for k in (0, 1)]
            h = 0 if n[0] >= STEER_N and n[1] <= STEER_Q and n[0] > n[1] else 1 if n[1] >= STEER_N and n[0] <= STEER_Q and n[1] > n[0] else None
            if driving and h is not None:
                side = 0 if h == 1 else 1                # a block in the right half: the left thruster turns it right
                if self.steer == "big":
                    pair = [b for b in beats if b[0] in (self.big[0], self.big[1])]
                    if pair:
                        keep = [b for b in beats if b[0] != self.big[1 - side]]
                        partner = [b for b in beats if b[0] == self.big[1 - side]]
                        self.pend += [(m, at, self.t + LAG) for m, at in partner]
                        beats = keep
                        self.recent = []
                else:
                    beats = beats + [(self.route[(side, self.steer)], 0.0)]
                    self.recent = []
            beats = beats + due
            self.beats = beats
            return [m for m, _ in beats]
    return Steered


def routed(cls):
    """The starting brain, its beats routed to thrusters of the chosen sizes on the same side (told the wiring: route[(side, size)])."""
    class Routed(cls):
        route, scan_size, drive_size = None, None, None

        def step(self):
            out = super().step()
            beats = list(getattr(self, "beats", None) or [])
            if not beats or self.route is None:
                return out
            both = {m for m, _ in beats} == {0, 1} or (self.t - self.last_drive < self.p["hold"]) or \
                (self.t - self.last_food > self.p["bored"])
            size = self.drive_size if both else self.scan_size
            if size is None:
                return out
            self.beats = [(self.route[(self.side[m], size)], at) for m, at in beats]
            return [m for m, _ in self.beats]
    return Routed


def make(world, design, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    sc, sx, dv, dx = DESIGNS[design][:4]
    steer = DESIGNS[design][4] if len(DESIGNS[design]) > 4 else None
    q = T.numbers(seed, {"sync": 1})
    q["scan"] *= sx
    q["drive"] *= dx
    q["run"] *= dx
    cls = steered(seconds_cls(T.Circuit)) if steer else routed(seconds_cls(T.Circuit))
    lf = WLife(seed, first, (lambda s: cls(s, q)), S.world_of(WORLDS[world]), seconds=True)
    b = lf.brain
    side = {lf.wire_m[th]: th for th in (0, 1)}         # motor line -> side (0 left, 1 right)
    b.side = side
    b.route = {(sd, sz): lf.wire_m[2 * (1 + i) + sd] for sd in (0, 1) for i, sz in enumerate(("H", "Q"))}
    b.scan_size, b.drive_size = sc, dv
    if steer:                                           # told the map: line -> half; and the big thrusters' lines by side
        b.steer, b.recent, b.pend = steer, [], []
        b.half_of_line = {lf.wire_h[h]: h for h in (0, 1)}
        b.big = {sd: lf.wire_m[sd] for sd in (0, 1)}
    if world == "lopsided":                             # told its balance (the strength ratio is the same at every size)
        k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
        right = math.log(k[1] / k[0])
        b.p["g0"], b.p["g1"] = math.exp(right / 2), math.exp(-right / 2)
    return lf


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    world, design, seed, first = j
    lf = make(world, design, seed, first)
    l = S.live(lf, 300.0)
    g = [a - COST * c for a, c, _ in l]
    sp = spent(l)
    return (0.0, 0.0, g[2], sp * l[2][2] / sum(t for _, _, t in l), sum(a for a, _, _ in l), sum(c for _, c, _ in l))


def yardstick(n=10, worlds=None, designs=None):
    I = R.boot(n)
    print(f"== G1, the yardstick: designs told the wiring, the new parts from birth; {n} pairs, 300 s, efficiency in the last third [95%]")
    with ProcessPoolExecutor(7, initializer=_init) as ex:
        for world in worlds or WORLDS:
            ds = designs or list(DESIGNS)
            res = {d: list(ex.map(job, [(world, d, s, c) for s in range(SEEDS0, SEEDS0 + n) for c in L.COL])) for d in ds}
            base = L.scored(res["base"], 300.0, I)
            line = f" {world:8s}"
            for d in ds:
                e = L.scored(res[d], 300.0, I)
                diff = e[1] - base[1]
                line += f" | {d} {e[0]:+.2f}" + (f" ({e[0] - base[0]:+.2f} [{np.percentile(diff, 2.5):+.2f},{np.percentile(diff, 97.5):+.2f}])" if d != "base" else "")
            print(line, flush=True)


if __name__ == "__main__":
    import ledger
    ledger.start()
    a = sys.argv[1:]
    if a[0] == "yardstick":
        yardstick(int(a[1]) if len(a) > 1 else 10, a[2].split(",") if len(a) > 2 else None, a[3].split(",") if len(a) > 3 else None)
