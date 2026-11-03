"""story1.py: the interventions phase's pilot story (PARTS.md; discrete/NOTEBOOK.md, D25). X = which colour is food, in
the block model, standard bodies, tolerances drawn.

    python lab/story1.py stats [SEEDS]        # what the brain can sense, right and wrong: rates of each kind of taste
    python lab/story1.py judge ARM... [SEEDS] [--control all-food|random] [k=v ...]    # lives of an arm, then its table

Arms (each one brain, on the same lives):
  still      fires nothing (the best any brain can do that never uses taste, by symmetry: food = poison otherwise)
  unwired    B without learning: either eye starts a drive (lab/grow.py)
  told       B told the colour, learning off (the ceiling for B's movements); wrong: told it backwards
  B          doubt a bounded tally, as benched; variants by k=v (fstep=0, drift=0, V_H, V_L)
  bayes      B's movements, the bit held by the exact likelihood ratio of what it senses, from `stats`' rates
  path       no bit: each eye's pathway its own tally of the tastes during drives that eye started; below -theta the
             eye no longer starts a drive (op=block) or ends one (op=reverse); a tally recovers while blocked (tau)
  gated      the bit's tally written only by tastes the eyes vouch for (use, trust, window)
  grow       D17's grower, all=1 (lab/grow.py)

--control: all-food, both colours food (nothing to learn); random, each meal food or poison by a coin (nothing
predicts it: nothing can be learned, and the best is not to eat)."""
import json
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

ROOT = "/home/pilgrim/git/simple-learner"
sys.path.insert(0, ROOT + "/lab")
sys.path.insert(0, ROOT)
from discrete import model as M  # noqa: E402
from units import TICK  # noqa: E402
import grow as G  # noqa: E402

RATES = ROOT + "/lab/v/story1_rates.json"
WINDOW = 0.3                                            # s: "this eye pulsed just now"


class Still(M.Model):
    def step(self):
        self.seen = [0, 0]
        self.t += TICK
        return []


class Watched(M.Model):
    """B's movements, logging each taste's kind: its sign, and which of the followed and other eye pulsed just now."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.last = [-1e9, -1e9]
        self.log = []

    def kind(self, value):
        f, o = self.food, 1 - self.food
        return (int(value > 0), int(self.t - self.last[f] < WINDOW), int(self.t - self.last[o] < WINDOW))

    def taste(self, value, at):
        self.log.append(self.kind(value))
        super().taste(value, at)

    def step(self):
        for k in (0, 1):
            if self.seen[k]:
                self.last[k] = self.t
        return super().step()


class Bayes(Watched):
    """The bit held by the likelihood ratio that it is wrong, from what it senses: each taste's kind has its rate with
    the bit right and with it wrong (a point process: an event adds the log of their ratio, silence the difference of
    their total rates), so the log-odds is exact given the rates. Holding the likelier bit needs no exploring: a taste
    informs whichever bit is held."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.L = 0.0
        self.llr = p["llr"]
        self.drift_ = p["silence"]

    def taste(self, value, at):
        self.L += self.llr[str(self.kind(value))]
        if self.L > 0:
            self.food, self.L = 1 - self.food, -self.L
            self.flips.append(self.t)

    def step(self):
        self.L -= self.drift_ * TICK
        if self.L > 0:                                  # (silence can only favour right or wrong by its rates)
            self.food, self.L = 1 - self.food, -self.L
            self.flips.append(self.t)
        return Watched.step(self)


class Gated(Watched):
    """The bit's tally written only by tastes the eyes vouch for: use=0, while driving (a signal B already has: the
    followed eye pulsed within the hold, and the other not since); use=1, the followed eye pulsed within the window and
    the other not. A poison steps it up, a food down, bounded below by -trust (a whole number of steps); at +1 the bit
    flips and the tally starts again at 0, so an unbacked bit flips on the first vouched poison."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.L = 0

    def vouched(self):
        p = self.p
        if p.get("use", 0):
            w = p["window"]
            return self.t - self.last[self.food] < w <= self.t - self.last[1 - self.food]
        return self.t - self.last_drive < p["hold"]

    def taste(self, value, at):
        if not self.vouched():
            return
        self.L = max(-int(self.p.get("trust", 2)), self.L + (1 if value < 0 else -1))
        if self.L >= 1:
            self.food, self.L = 1 - self.food, 0
            self.flips.append(self.t)


class RunLimit:
    """Mixed into any arm with run_max in its numbers: a run lasts at most run_max s, then boredom starts again, so it
    scans onto a new heading (the user's sighting: only a food pulse ended a run, so a run along a closed line of the
    torus could go on for an hour). Every arm's baseline since 2026-11-02."""

    run_from = None

    def step(self):
        p = self.p
        running = self.t - self.last_drive >= p["hold"] and self.t - self.last_food > p["bored"]
        if not running:
            self.run_from = None
        elif self.run_from is None:
            self.run_from = self.t
        elif self.t - self.run_from > p["run_max"]:
            self.last_food, self.run_from = self.t, None
        return super().step()


class Timed(RunLimit, Gated):
    pass


class Path(G.Unwired):
    """Each eye's own tally of the tastes during drives it started; it stops driving below -theta."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.w = [0.0, 0.0]
        self.owner = None
        self.blocked_at = [None, None]
        self.bad = "reverse" if p.get("reverse") else "block"

    def taste(self, value, at):
        p = self.p
        if self.owner is None or self.t - self.last_drive >= p["hold"] + p.get("after", 0.1):
            return
        k = self.owner
        self.w[k] = min(p.get("trust", 2.0), self.w[k] + (1.0 if value > 0 else -p.get("cost", 1.0)))
        if self.w[k] < -p.get("theta", 1.5) and self.op[k] == "drive":
            self.op[k] = self.bad
            self.blocked_at[k] = self.t

    def step(self):
        p = self.p
        for k in (0, 1):
            if self.op[k] == "drive" and self.seen[k] and self.t - self.last_drive >= p["hold"]:
                self.owner = k                          # the eye that starts a drive owns it
            if self.op[k] != "drive" and p.get("tau", 0) and self.t - self.blocked_at[k] > p["tau"]:
                self.op[k], self.w[k] = "drive", 0.0    # a blocked eye gets another try
        return super().step()


ARMS = {"still": Still, "unwired": G.Unwired, "told": M.Model, "wrong": M.Model, "B": M.Model, "bayes": Bayes,
        "watch_right": Watched, "watch_wrong": Watched, "path": Path, "gated": Gated, "timed": Timed, "grow": G.Grow}


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison, control = job
    q = M.drawn(p, spread, seed)
    if arm == "bayes":
        q |= json.load(open(q.get("rates", RATES)))
    if arm == "grow":
        q["all"] = 1
    cls = ARMS[arm]
    if "run_max" in q and arm != "still" and not issubclass(cls, RunLimit):
        cls = type("Limited", (RunLimit, cls), {})
    lf = Life(seed, poison if control != "all-food" else None, brain=lambda s: cls(s, q))
    b = lf.brain
    pe = lf.sensor[poison]                              # (in a control, the eye of the colour that would be poison)
    if arm in ("told", "watch_right"):
        b.food, b.p["V_H"] = 1 - pe, 99.0
    if arm in ("wrong", "watch_wrong"):
        b.food, b.p["V_H"] = pe, 99.0
    born_right = getattr(b, "food", None) != pe
    ticks = int(round(seconds / TICK))
    coin = np.random.default_rng(seed + 424_243)
    colours = ("red", "blue")
    bad = []
    right_at = []
    while lf.t < ticks:
        n = len(lf.meals)
        if control == "random":
            lf.poison = colours[int(coin.integers(2))]
        lf.step()
        if control == "random" and len(lf.meals) > n:   # scored by the taste the coin gave
            for i in range(n, len(lf.meals)):
                t, c = lf.meals[i]
                lf.meals[i] = (t, "red" if c == lf.poison else "blue")
        right_at.append(getattr(b, "food", 0) != pe)
    pois = "red" if control == "random" else (poison if control != "all-food" else None)
    l = Lived(thirds(lf.meals, lf.moving, ticks, pois))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.flips, l.born_right = list(getattr(b, "flips", [])), bool(born_right)
    l.right = float(np.mean(right_at))
    l.log = list(getattr(b, "log", [])) if arm.startswith("watch") else []
    l.ops = list(getattr(b, "op", []))
    l.poison_eye = pe
    l.blocked = list(getattr(b, "blocked_at", []))
    l.events = list(getattr(b, "events", []))
    l.seconds = seconds
    return l


def lives(arm, p, spread, seeds, seconds=100.0, control=None, workers=8):
    jobs = [(arm, p, spread, s, seconds, c, control) for s in seeds for c in ("red", "blue")]
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(life, jobs, chunksize=4))


def stats(seeds, seconds=100.0, extra=None, path=RATES):
    """The rate of each kind of taste, per s, with the bit right and with it wrong; each kind's log ratio, and what
    silence says. Pseudo-counts so that a kind never seen doesn't give an infinite step."""
    p, spread = M.from_bench()
    p |= extra or {}
    kinds = [str((s, f, o)) for s in (0, 1) for f in (0, 1) for o in (0, 1)]
    out = {}
    for arm in ("watch_right", "watch_wrong"):
        L = lives(arm, p, spread, seeds, seconds)
        T = len(L) * seconds
        n = {k: 0.5 for k in kinds}
        for l in L:
            for e in l.log:
                n[str(e)] += 1
        out[arm] = {k: v / T for k, v in n.items()}
    r, w = out["watch_right"], out["watch_wrong"]
    llr = {k: float(np.log(w[k] / r[k])) for k in kinds}
    silence = sum(w.values()) - sum(r.values())
    for k in kinds:
        print(f"  sign,followed,other {k}: right {r[k]:.3f}/s  wrong {w[k]:.3f}/s  evidence {llr[k] / np.log(2):+.2f} bits")
    kl = sum(w[k] * llr[k] - w[k] + r[k] for k in kinds) / np.log(2)
    klr = sum(r[k] * -llr[k] - r[k] + w[k] for k in kinds) / np.log(2)
    print(f"  evidence rate: if wrong {kl:.2f} bits/s towards wrong; if right {klr:.2f} bits/s towards right")
    json.dump({"llr": llr, "silence": silence, "right": r, "wrong": w, "kl_wrong": kl, "kl_right": klr},
              open(path, "w"), indent=1)


def table(name, L, ref=None):
    """One line: the measures; and, for a learner, when and how often its bit moved."""
    from discrete.poison import show
    from minimal.spec import summary
    s = summary(L)
    print(show(name, s), flush=True)
    return s


def paired(A, B, f=None, boot=2000, seed=0):
    from minimal.spec import efficiency, interval
    f = f or efficiency
    rng = np.random.default_rng(seed)
    n = len(A) // 2
    d = []
    for _ in range(boot):
        k = rng.integers(0, n, n)
        ia = [l for i in k for l in (A[2 * i], A[2 * i + 1])]
        ib = [l for i in k for l in (B[2 * i], B[2 * i + 1])]
        d.append(f(ia) - f(ib))
    return f(A) - f(B), interval(d)


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args.pop(0)
    kw = [a for a in args if "=" in a]
    control = None
    if "--control" in args:
        i = args.index("--control")
        control = args[i + 1]
        del args[i:i + 2]
    rest = [a for a in args if "=" not in a]
    seeds = range(50000, 50064)
    if rest and ":" in rest[-1]:
        lo, hi = rest.pop().split(":")
        seeds = range(int(lo), int(hi))
    if cmd == "stats":
        stats(seeds)
    else:
        p, spread = M.from_bench()
        k = {a.split("=")[0]: float(a.split("=")[1]) for a in kw}
        seconds = k.pop("seconds", 100.0)
        for arm in rest:
            L = lives(arm, dict(p, **k), spread, seeds, seconds, control)
            tag = f"{arm}_{seeds.start}" + (f"_{control}" if control else "") + "".join(
                f"_{a}{b:g}" for a, b in sorted(k.items())) + (f"_s{seconds:g}" if seconds != 100 else "")
            pickle.dump(L, open(f"{ROOT}/lab/v/story1_{tag}.lives", "wb"))
            table(tag, L)
