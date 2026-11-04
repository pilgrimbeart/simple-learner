"""universal_gt.py: H3, generate and test (STORIES.md; discrete/NOTEBOOK.md, D29). One alarm, one trial loop, knowing nothing of the rows.

Every W s the creature nets goods less bads over the window. Alarmed (bads at least `bads`, or goods under `gate`, in a window), it changes one knob at
random for one window and keeps the change only if the net beat the steady baseline by delta. Knobs: table length, trust, pause, balance, each eye's threshold.
Holds: a window's count, a baseline, a little trial state, and all the knobs' own parts.

    python lab/universal_gt.py eval [k=v ...]    every world at lengths 100, 400, 1000, 4000 s
    python lab/universal_gt.py search N [k=v ...]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import table as T
from table import RunLimit, Gated, TICK
import universal as X
from minimal.spec import efficiency


KNOBS = dict(n=(1, 2, 3, 6), trust=(0, 1, 2, 3, 5), pause=(0.0, 0.6, 1.0, 1.5, 2.0), x=(-1.2, -0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2), lev0=(1, 2, 3), lev1=(1, 2, 3))
START = dict(n=1, trust=1, pause=0.0, x=0.0, lev0=1, lev1=1)


class G(RunLimit, Gated):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rng = np.random.default_rng(seed + 919_191)
        self.k = dict(START)
        self.c, self.bits, self.tally = 0, [self.food], [0]
        self.goods, self.bads, self.next, self.base, self.trial, self.tests, self.kept = 0, 0, p.get("W", 32.0), None, None, 0, []
        self.ate_at, self.grew, self.on_at, self.nets = -1e9, [], [], []
        self.cnt, self.tu = [0.0, 0.0], [0.0, 0.0]
        self.open, self.recent = bool(p.get("open", 1)), 0

    def apply(self):
        k = self.k
        n = k["n"]
        if n != len(self.bits):
            old = len(self.bits)
            self.bits = [self.bits[j % old] for j in range(n)]
            self.tally = [self.tally[j % old] for j in range(n)]
            self.c %= n
        self.p["g0"], self.p["g1"] = float(np.exp(k["x"] / 2)), float(np.exp(-k["x"] / 2))

    def stimulate(self, sensor, at):
        now = self.t + at
        self.cnt[sensor] = self.cnt[sensor] * np.exp(-(now - self.tu[sensor]) / self.p.get("tau_e", 0.05)) + 1.0
        self.tu[sensor] = now
        if self.cnt[sensor] >= self.k["lev" + str(sensor)]:
            self.recent = sensor
            super().stimulate(sensor, at)

    def taste(self, value, at):
        self.ate_at = self.t
        if value > 0:
            self.goods += 1
        else:
            self.bads += 1
        if self.open:
            if value < 0:
                self.open = False
                self.food = 1 - self.recent
                self.bits = [self.food] * len(self.bits)
            return
        c = self.c
        if self.vouched():
            if value > 0:
                self.tally[c] = max(-self.k["trust"], self.tally[c] - 1)
            else:
                self.tally[c] += 1
                if self.tally[c] >= 1:
                    self.bits[c], self.tally[c] = 1 - self.bits[c], 0
                    self.flips.append(self.t)
        if value > 0:
            self.c = (c + 1) % len(self.bits)
        self.food = self.bits[self.c]

    def window(self):
        p = self.p
        net = self.goods - p.get("bad_w", 2.0) * self.bads
        self.nets.append(net)
        alarm = self.bads >= p.get("bads", 6.0) or self.goods < p.get("gate", 8.0)
        self.goods, self.bads = 0, 0
        self.next += p.get("W", 32.0)
        if self.trial is not None:
            knob, old = self.trial
            self.trial = None
            if net > self.base + p.get("delta", 2.0):
                self.base = net
                self.kept.append((self.t, knob, self.k[knob]))
                if knob == "n":
                    self.grew.append((self.t, self.k[knob]))
                if knob == "pause" and self.k[knob]:
                    self.on_at.append(self.t)
                return
            self.k[knob] = old
            self.apply()
            return
        self.base = net if self.base is None else self.base + (net - self.base) * p.get("mix", 0.5)
        if alarm:
            knob = str(self.rng.choice(list(KNOBS)))
            vals = KNOBS[knob]
            i = vals.index(self.k[knob])
            j = i + (1 if i == 0 else -1 if i == len(vals) - 1 else int(self.rng.choice([-1, 1])))
            self.trial = (knob, self.k[knob])
            self.k[knob] = vals[j]
            self.tests += 1
            self.apply()

    def step(self):
        if self.t >= self.next:
            self.window()
        if self.open:
            s = self.seen[0] + self.seen[1]
            self.seen = [0, 0]
            self.seen[self.food] = s
        if self.k["pause"] and self.t - self.ate_at < self.k["pause"]:
            self.seen = [0, 0]
            super().step()
            return []
        return super().step()


T.ARMS["g"] = G


def judge(kw, seeds=T.TRAIN, lengths=(100.0, 400.0, 1000.0)):
    seeds = list(seeds)
    for sec in lengths:
        print(f"-- {sec:.0f} s", flush=True)
        for w in list(X.BEST) + ["plain", "allfood"]:
            L, B = T.run(w, "g", seeds, kw, sec), T.run(w, "circuit", seeds, seconds=sec)
            d, i = T.paired(L, B)
            print(f"  {w}: {efficiency(L):.2f} (base {efficiency(B):.2f}), {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]; flips {np.mean([l.flips for l in L]):.1f}, grew {np.mean([bool(l.grew) for l in L]):.2f}, paused {np.mean([bool(l.on) for l in L]):.2f}", flush=True)


def nets(job):
    """One life with the knobs held, each window's net: the signal a trial has to read."""
    w, kw, seed, first, secs = job
    from creature import Life
    q = T.numbers(seed, {"learn": 1.0, "bads": 1e9, "gate": -1.0, **kw})
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: G(s, q))
    b = lf.brain
    for k, v in kw.items():
        if k.startswith("set_"):
            b.k[k[4:]] = v
    b.apply()
    R.setup(lf, seed)
    if hasattr(R, "taste"):
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    done = 0
    while lf.t < int(secs / T.TICK):
        t = lf.t * T.TICK
        lf.poison, R.now = R.poison(t), t
        R.tick(lf, t)
        lf.step()
        while done < len(lf.meals):
            R.ate(lf.meals[done][1])
            done += 1
    return b.nets[2:]


def snr():
    """Each cure's real effect on one window's net against that net's spread: how many windows a trial needs to see it at 2 sd."""
    from concurrent.futures import ProcessPoolExecutor
    cases = [("alternate", {}, {"set_n": 2}), ("digest", {}, {"set_pause": 1.5}), ("unreliable", {}, {"set_trust": 3}), ("swap10", {}, {"set_trust": 0}), ("plain", {}, {"set_trust": 3}), ("plain", {}, {"set_pause": 1.5}), ("noisy", {}, {"set_lev0": 2, "set_lev1": 2})]
    for w, a, b in cases:
        out = []
        for kw in (a, b):
            with ProcessPoolExecutor(8) as ex:
                L = list(ex.map(nets, [(w, kw, s, c, 640.0) for s in T.TRAIN for c in T.COL]))
            v = np.concatenate(L)
            out.append((v.mean(), v.std()))
        eff, sd = out[1][0] - out[0][0], np.hypot(out[0][1], out[1][1])
        print(f"{w} {b}: net a window {out[0][0]:.1f} (sd {out[0][1]:.1f}) -> {out[1][0]:.1f} (sd {out[1][1]:.1f}); effect {eff:+.1f}, difference's sd {sd:.1f}, windows to see it at 2 sd {(2 * sd / max(abs(eff), 1e-6)) ** 2:.0f}", flush=True)


def fair(n):
    """A fair search at long lives on the worlds that say most: settings slower and stricter than the first guess."""
    r = np.random.default_rng(33)
    base = {w: T.run(w, "circuit", T.TRAIN, seconds=1000.0) for w in ("alternate", "digest", "unreliable", "weak", "plain")}
    for j in range(n):
        kw = dict(W=float(r.choice([32, 64, 128])), delta=float(r.choice([2, 4, 8, 16])), bad_w=float(r.choice([1, 2, 4])), bads=float(r.choice([3, 6, 12])), gate=float(r.choice([4, 8])), mix=float(r.choice([0.25, 0.5])))
        out = []
        for w, B in base.items():
            L = T.run(w, "g", T.TRAIN, kw, 1000.0)
            d, i = T.paired(L, B)
            out.append(f"{w[:5]} {efficiency(L):.2f} {d:+.2f}[{i[0]:+.2f},{i[1]:+.2f}]")
        print(json.dumps(kw), "| " + " | ".join(out), flush=True)


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    if cmd == "eval":
        judge(X.parse(rest))
    elif cmd == "snr":
        snr()
    elif cmd == "fair":
        fair(int(rest[0]))
