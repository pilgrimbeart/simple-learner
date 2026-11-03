"""universal.py: a candidate universal correction circuit (discrete/NOTEBOOK.md, D29; STORIES.md), and its judging.

U is story 1's circuit with one set of parts on the taste and the eyes, each off unless its own evidence appears:
  - the bit is a table: a counter that good tastes advance, each position a bit and a tally (length 1 is story 1's circuit);
  - trust T, one node moved by what flips turn out to be: a flip contradicted at once (bounce) raises it, one that ended a run of
    goods and is confirmed lowers it;
  - frustration F: vouched bads no bounce explains; past theta the table grows;
  - pause tally P: vouched bads soon after a taste, less those later; past theta the creature waits after a taste;
  - each eye's threshold is set by its own background rate;
  - the balance jitters only while meals are short.
Ablation: eye=0, trustk=0, growk=0, pausek=0, jit=0 remove a part. open=1: both eyes followed until the first bad.

    python lab/universal.py eval [k=v ...]        every world, training seeds
    python lab/universal.py ablate [k=v ...]      each part removed
    python lab/universal.py search N [k=v ...]    random search, every world
    python lab/universal.py judge FILE            a setting, fresh seeds"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import table as T
from table import RunLimit, Gated, DB, TICK
from table_rows import VALID
from minimal.spec import efficiency


class U(RunLimit, Gated, DB.DriveBal):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        # table
        self.c, self.n, self.bits, self.tally, self.i = 0, 1, [self.food], [0], 0
        self.grew = []
        # trust and flips
        self.Tr, self.watch, self.wgoods, self.run_g, self.long_run = 0.0, False, 0, 0, False
        # frustration
        self.F = 0.0
        # pause
        self.P, self.est, self.ate_at, self.pausing, self.on_at = 0.0, 0.0, -1e9, False, []
        # eyes
        self.cnt, self.tu, self.slow, self.su = [0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]
        # balance
        self.p.setdefault("eta", 0.06)
        self.sd0, w = self.p.get("sd", 0.15), self.p.get("win", 200.0)
        self.rate = self.p.get("gate", 15.0) * w / 32.0 * self.p.get("born", 1.5)
        self.p["sd"] = 0.0
        self.open, self.recent = bool(self.p.get("open", 0)), 0

    # --- the eyes
    def level(self, k):
        return max(1.0, self.p.get("margin_e", 3.0) * self.slow[k] * self.p.get("tau_e", 0.05))

    def stimulate(self, sensor, at):
        p = self.p
        if not p.get("eye", 1):
            self.recent = sensor
            return super().stimulate(sensor, at)
        now = self.t + at
        ts = p.get("tau_s", 10.0)
        self.slow[sensor] = self.slow[sensor] * np.exp(-(now - self.su[sensor]) / ts) + 1.0 / ts
        self.su[sensor] = now
        self.cnt[sensor] = self.cnt[sensor] * np.exp(-(now - self.tu[sensor]) / p.get("tau_e", 0.05)) + 1.0
        self.tu[sensor] = now
        if self.cnt[sensor] >= self.level(sensor):
            self.recent = sensor
            super().stimulate(sensor, at)

    def trust(self):
        p = self.p
        if not p.get("trustk", 1):
            return int(p.get("trust", 1))
        if self.Tr < -p.get("low", 0.37):
            return 0
        return 1 + int(min(p.get("top", 5.0), max(self.Tr, 0.0)))

    # --- the taste
    def taste(self, value, at):
        p = self.p
        gap = self.t - self.ate_at
        self.ate_at = self.t
        if value > 0:
            self.rate += 1.0
        if self.open:
            if value < 0:                               # the first bad: what it just saw is the poison
                self.open = False
                self.food = 1 - self.recent
                self.bits = [self.food] * self.n
            return
        c = self.c
        if self.vouched():
            bounced = False
            if self.watch:
                if value < 0:
                    if gap >= p.get("soon_b", 0.0):
                        self.Tr = min(p.get("top", 5.0), max(self.Tr, 0.0) + p.get("step_b", 2.0))
                    bounced, self.watch = True, False
                else:
                    self.wgoods += 1
                    if self.wgoods == 1 and self.long_run and self.Tr < p.get("veto", 1.0):
                        self.Tr = -1.0
                    self.watch = self.wgoods < p.get("short", 1.0)
            if p.get("pausek", 1):
                soon = gap < p.get("win_p", 1.2)
                if value < 0:
                    if soon:
                        self.P = min(p.get("mtop", 4.0), self.P + 1)
                        self.est = max(self.est, gap * p.get("margin_p", 1.2))
                    else:
                        self.P = max(0.0, self.P - p.get("late", 1.0))
                elif soon:
                    self.P = max(0.0, self.P - (p.get("down_on", 0.0) if self.pausing else p.get("down", 1.0)))
                    self.est *= p.get("shrink", 0.98)
            if value > 0:
                self.run_g += 1
            if value < 0 and not bounced and p.get("growk", 1):
                self.F += 1.0
                if self.F >= p.get("theta_g", 3.0) and self.i + 1 < len(p.get("sizes", (1, 2, 3, 6))) and not self.pausing:
                    self.i += 1
                    n = p.get("sizes", (1, 2, 3, 6))[self.i]
                    self.bits = [self.bits[j % self.n] for j in range(n)]
                    self.tally = [self.tally[j % self.n] for j in range(n)]
                    self.c, self.n, self.F, c = c % n, n, 0.0, c % n
                    self.grew.append((self.t, n))
            if value > 0:
                self.tally[c] = max(-self.trust(), self.tally[c] - 1)
            else:
                self.tally[c] += 1
                if self.tally[c] >= 1:
                    self.bits[c], self.tally[c] = 1 - self.bits[c], 0
                    self.flips.append(self.t)
                    self.watch, self.wgoods, self.long_run = True, 0, self.run_g >= p.get("k", 2.0)
                    self.run_g = 0
        if value > 0:
            self.c = (c + 1) % self.n
        self.food = self.bits[self.c]

    # --- slow nodes
    def step(self):
        p = self.p
        self.Tr *= 1 - TICK / (p.get("tau_b", 1000.0) if self.Tr > 0 else p.get("tau_v", 40.0))
        self.F *= 1 - TICK / p.get("tau_g", 10.0)
        self.P *= 1 - TICK / p.get("tau_p", 150.0)
        w = p.get("win", 200.0)
        self.rate *= 1 - TICK / w
        if p.get("jit", 1):
            p["sd"] = self.sd0 if self.rate * 32.0 / w < p.get("gate", 15.0) else 0.0
        on = self.P >= p.get("theta_p", 2.0) or (self.pausing and self.P > p.get("off", 0.5))
        if on and not self.pausing:
            self.on_at.append(self.t)
        self.pausing = on and bool(p.get("pausek", 1))
        if self.open:
            s = self.seen[0] + self.seen[1]
            self.seen = [0, 0]
            self.seen[self.food] = s
        if self.pausing and self.t - self.ate_at < self.est:
            self.seen = [0, 0]
            super().step()
            return []
        return super().step()


T.ARMS["u"] = U

# (world, the row's best manual cure's number on the final judge, for scale)
BEST = {"thrusters": 2.06, "swap10": 1.15, "alternate": 2.46, "pattern": 2.33, "digest": 1.74, "noisy": 1.87, "unreliable": 0.63, "ageing": 1.76, "weak": 1.85, "patchy": 0.65}
BASE = {}


def base(w, seeds, secs):
    key = (w, seeds[0], len(seeds), secs)
    if key not in BASE:
        BASE[key] = T.run(w, "circuit", seeds, seconds=secs)
    return BASE[key]


def scores(kw, seeds=T.TRAIN, short=None, verbose=False):
    """Each world's recovery: 0 at the base brain, 1 at the row's best manual cure. Then plain and all-food."""
    seeds = list(seeds)
    R = {}
    for w in BEST:
        secs = (short or T.LONG.get(w, 100.0)) if w in T.LONG else 100.0
        B, L = base(w, seeds, secs), T.run(w, "u", seeds, kw, secs)
        R[w] = (efficiency(L) - efficiency(B)) / max(BEST[w] - efficiency(B), 0.05)
        if verbose:
            d, i = T.paired(L, B)
            print(f"  {w}: {efficiency(L):.2f} (base {efficiency(B):.2f}), {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}], recovery {R[w]:.2f}; flips {np.mean([l.flips for l in L]):.1f}, grew {np.mean([bool(l.grew) for l in L]):.2f}, paused {np.mean([bool(l.on) for l in L]):.2f}", flush=True)
    P = T.run("plain", "u", seeds, kw)
    d, i = T.paired(P, base("plain", seeds, 100.0))
    A = T.run("allfood", "u", seeds, kw)
    da = efficiency(A) - efficiency(base("allfood", seeds, 100.0))
    if verbose:
        print(f"  plain: {efficiency(P):.2f}, {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]; flips {np.mean([l.flips for l in P]):.1f}, grew {np.mean([bool(l.grew) for l in P]):.2f}, paused {np.mean([bool(l.on) for l in P]):.2f}", flush=True)
        print(f"  allfood: {efficiency(A):.2f}, {da:+.2f}", flush=True)
    r = np.array([min(v, 1.2) for v in R.values()])
    return float(r.mean() + 0.5 * r.min() + 3 * min(0.0, d) + 1 * min(0.0, da)), R, d, da


def parse(args):
    return {k: (float(v) if v.replace(".", "").replace("-", "").isdigit() else json.loads(v)) for k, v in (a.split("=") for a in args)}


def draw(r):
    return dict(k=float(r.choice([2, 3, 5])), short=float(r.choice([1, 2, 3])), step_b=float(r.choice([1, 2])), top=float(r.choice([3, 5])), tau_b=float(r.choice([300, 1000])),
                tau_v=float(r.choice([20, 40, 80])), veto=float(r.choice([0.5, 1, 2])), theta_g=float(r.choice([3, 4, 5])), tau_g=float(r.choice([5, 10, 20])),
                theta_p=float(r.choice([2, 3])), win_p=float(r.choice([1.2, 1.5, 2])), tau_p=float(r.choice([100, 150, 300])), late=float(r.choice([0.5, 1, 2])), margin_p=float(r.choice([1.1, 1.2, 1.4])),
                margin_e=float(r.choice([2, 3, 4])), tau_s=float(r.choice([10, 20])), gate=float(r.choice([13, 15, 17])), sd=float(r.choice([0.15, 0.2, 0.3])), eta=float(r.choice([0.03, 0.06])))


def search(n, fixed):
    r = np.random.default_rng(29)
    res = []
    for j in range(n):
        kw = {**draw(r), "learn": 1.0, **fixed}
        s, R, d, da = scores(kw, short=400.0)
        res.append((s, kw))
        print(f"{j} score {s:.3f} plain {d:+.3f} allfood {da:+.2f} " + " ".join(f"{w[:4]} {v:.2f}" for w, v in R.items()) + " " + json.dumps(kw), flush=True)
    res.sort(key=lambda x: -x[0])
    finals = sorted(((scores(kw, VALID, short=1000.0)[0], json.dumps(kw)) for _, kw in res[:5]), reverse=True)
    for s, k in finals:
        print(f"validation {s:.3f} {k}", flush=True)
    return json.loads(finals[0][1])


PARTS = ("eye", "trustk", "growk", "pausek", "jit")


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    if cmd == "eval":
        kw = {"learn": 1.0, **parse(rest)}
        print(json.dumps(kw), flush=True)
        print("score", scores(kw, verbose=True)[0], flush=True)
    elif cmd == "ablate":
        kw = {"learn": 1.0, **parse(rest)}
        for part in (None,) + PARTS:
            print(f"== without {part}", flush=True)
            print("score", scores(kw if part is None else {**kw, part: 0.0}, verbose=True)[0], flush=True)
    elif cmd == "search":
        print("best", json.dumps(search(int(rest[0]), parse(rest[1:]))), flush=True)
