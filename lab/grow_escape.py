"""grow_escape.py: recruitment in the arena, case: escape from bites (the user, 2026-10-30), with the tracker as the
brain evolution built (arena.Tracker: told the colour and its wiring). Beside it the generic grower, told nothing of
what it is for:

- predict: each sensor a fading tag of its pulses (tau_tag), and a running rate (tau_p) of bad tastes' onsets while
  it is tagged, beside the running rate at any time: what follows this sensor, more than what comes anyway?
- the gap: frustration, a leaky count (tau_f) of bad tastes no sensor predicted (no tagged sensor's rate above `k`
  times the rate at any time);
- grow: frustration past `nf` grows one recruit on the taste's pathway to the motors (the declared primitive): on a
  bad taste's onset it fires, for `dur` s at `rate` a second, one of the generic operations: nothing, motor 0, motor 1,
  both;
- experiment: each operation for `trial` s, judged by the taste summed over it a second (+ while biting, - while
  bitten: what bites put into the belly and take out), then the best is kept (every operation once);
  bite=1, judged bite by bite instead: at each bite's onset (none being judged) the operations compete, each its
  running mean (its value) plus its own noise, sd / sqrt(1 + its tries), and the winner responds; the taste of the
  next `win` s, a tick, is its outcome, moving its value by max(1 / tries, `alpha`).

    python grow_escape.py [SEEDS] [seconds=300] [k=v ...]   (k: trial, nf, tau_f, k, tau_p, rate, dur; nf=1e9: never grows; random=1: the control;
    knob=1: no menu: the recruit two knobs w, firing motor k at rate * sigmoid(w_k + e_k) for dur s after a bite's
    onset (its beats added to the brain's own), e_k its own noise (sd_k, 2) drawn afresh each bite; the taste of the next `win` s a tick, against its running
    mean (tau_b bites), moves each knob by eta (3) (outcome - mean) e_k (node perturbation); knobs start at w0 (-2)
    t_scan, t_hold, ...: every robot's standing policy (B's knobs) scaled, e.g. the disc arena's tuned tracker
    phantom=1: the control, pain no response can stop: the grower's bad tastes replaced by phantom ones, onsets at
    random (p_rate a second), each lasting p_len s (its real bites still drain its belly, unfelt)
    bite=1 (the default; bite=0: timed trials): judged bite by bite, with win, sd, alpha)
    half the arena the grower, half plain trackers (invasion), paired by arena on the net (eaten - lost)"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import arena as AR
from units import TICK

OPS = ("none", "m0", "m1", "both")
GROW = {"bite": 1.0, "win": 0.25, "sd": 0.1}                # (bite=0: the timed trials)


class Grower(AR.Tracker):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.tagv = np.zeros(4)
        self.pred = np.zeros(4)                         # each sensor's rate of pain onsets (a tick) while tagged
        self.base = 0.0                                 # the rate at any time
        self.fr = 0.0
        self.hurting = False
        self.last_pain, self.fphase = -1e9, 0.0
        self.recruit, self.op, self.grew = None, "none", None
        self.pain_now = False
        self.onsets = self.unpredicted = 0              # watching
        self.rng = np.random.default_rng(seed + 7_070_707)   # (the control's own draw)

    def stimulate(self, sensor, at):
        self.tagv[sensor] += 1.0
        super().stimulate(sensor, at)

    def taste(self, value, at):
        if value < 0 and GROW.get("phantom"):
            return
        super().taste(value, at)
        if value < 0:
            self.pain_now = True
        if self.recruit is not None:
            self.recruit["got"] += value

    def step(self):
        g = GROW
        out = super().step()
        if g.get("phantom"):
            if self.rng.random() < g.get("p_rate", 0.6) * TICK:
                self.phantom_until = self.t + g.get("p_len", 0.3)
            if self.t < getattr(self, "phantom_until", -1.0):
                self.pain_now = True
                if self.recruit is not None:
                    self.recruit["got"] -= 1.0
        onset = self.pain_now and not self.hurting      # a bad taste's onset
        w = np.minimum(self.tagv, 1.0)
        if onset:
            self.onsets += 1
            if not ((w > 0.5) & (self.pred > g.get("k", 2.0) * self.base)).any():
                self.unpredicted += 1
                self.fr += 1.0
            self.last_pain = self.t
        a = TICK / g.get("tau_p", 20.0)
        self.pred += a * w * (float(onset) - self.pred)
        self.base += a * (float(onset) - self.base)
        self.hurting, self.pain_now = self.pain_now, False
        self.tagv *= 1 - TICK / g.get("tau_tag", 0.5)
        self.fr *= 1 - TICK / g.get("tau_f", 50.0)
        if self.recruit is None and self.fr > g.get("nf", 2.0):
            self.grew = self.t
            self.recruit = dict(i=0, start=self.t, got=0.0, score={})
            if g.get("knob"):
                self.recruit = dict(i=0, got=0.0, w=np.full(2, g.get("w0", -2.0)), e=np.zeros(2), b=None, pend=None,
                                    score=dict.fromkeys(range(len(OPS)), 0))
            elif g.get("bite"):
                self.recruit = dict(i=0, got=0.0, v=np.zeros(len(OPS)), n=np.zeros(len(OPS)), pend=None,
                                    score=dict.fromkeys(range(len(OPS)), 0))
            elif g.get("random"):                         # the control: one operation at random, kept, no judging
                self.recruit = dict(i=int(self.rng.integers(len(OPS))), start=self.t, got=0.0, score=dict.fromkeys(range(len(OPS)), 0))
        r = self.recruit
        if r is not None and g.get("knob"):
            win = g.get("win", 0.25)
            if r["pend"] is not None and self.t - r["pend"] >= win:
                x = r["got"] * TICK / win
                if r["b"] is None:
                    r["b"] = x
                r["w"] += g.get("eta", 3.0) * (x - r["b"]) * r["e"]
                r["b"] += (x - r["b"]) / g.get("tau_b", 10.0)
                r["pend"] = None
            if onset and r["pend"] is None:
                r["e"] = g.get("sd_k", 2.0) * self.rng.standard_normal(2)
                r["pend"], r["got"] = self.t, 0.0
            if self.t - self.last_pain < g.get("dur", 0.5):
                rates = g.get("rate", 50.0) / (1 + np.exp(-(r["w"] + r["e"])))
                self.kphase = getattr(self, "kphase", np.zeros(2)) + rates * TICK
                k = self.kphase.astype(int)
                self.kphase -= k
                return out + [0] * int(k[0]) + [1] * int(k[1])   # (its beats added to the brain's own)
            f = 1 / (1 + np.exp(-r["w"]))               # watching: what it now does, noise aside
            self.kept = ("none" if f.max() < 0.25 else "both" if f.min() > 0.25 else "m0" if f[0] > f[1] else "m1")
            self.knobs = f
            return out
        if r is not None and g.get("bite"):
            win = g.get("win", 1.0)
            if r["pend"] is not None and self.t - r["pend"] >= win:
                i = r["i"]
                r["n"][i] += 1
                r["v"][i] += max(1 / r["n"][i], g.get("alpha", 0.1)) * (r["got"] * TICK / win - r["v"][i])
                r["pend"] = None
            if onset and r["pend"] is None:
                noise = g.get("sd", 0.3) / np.sqrt(1 + r["n"]) * self.rng.standard_normal(len(OPS))
                r["i"], r["pend"], r["got"] = int(np.argmax(r["v"] + noise)), self.t, 0.0
            self.kept = OPS[int(np.argmax(r["v"]))]
        elif r is not None and len(r["score"]) < len(OPS) and self.t - r["start"] >= g.get("trial", 15.0):
            r["score"][r["i"]] = r["got"] / (self.t - r["start"])
            r["start"], r["got"] = self.t, 0.0
            r["i"] = r["i"] + 1 if len(r["score"]) < len(OPS) else max(r["score"], key=r["score"].get)
        if r is not None:
            self.op = OPS[r["i"]]
        if self.op != "none" and self.t - self.last_pain < g.get("dur", 0.5):
            self.fphase += g.get("rate", 50.0) * TICK
            k = int(self.fphase)
            self.fphase -= k
            ms = [0, 1] if self.op == "both" else [int(self.op[1])]
            return [m for m in ms for _ in range(k)]
        return out


_init = AR.Robot.__init__


def _robot(self, rng, seed, p, spread, t, kind="B"):
    _init(self, rng, seed, p, spread, t, "tracker" if kind == "grow" else kind)
    if kind == "grow":
        food = self.brain.food
        self.brain = Grower(seed, dict(self.brain.p))
        self.brain.food = food
        self.kind = "grow"
    for k in ("scan", "hold", "drive", "run", "bored"):    # t_<knob>=f: every robot's standing policy scaled (evolution's)
        if f"t_{k}" in GROW and hasattr(self.brain, "p"):
            self.brain.p[k] *= GROW[f"t_{k}"]


AR.Robot.__init__ = _robot


def run(job):
    seed, seconds, kw = job
    GROW.update(kw)
    A = AR.Arena(seed, 10, ("grow", "tracker"))
    for _ in range(int(seconds / TICK)):
        A.step()
    out = []
    for r, d in [(r, A.t) for r in A.robots] + A.dead:
        age = d - r.born
        if age >= 20:
            b = r.brain
            out.append(dict(kind=r.kind, ate=r.ate / age * 10, lost=(r.lost + AR.THRUST * r.firings) / age * 10, age=age,
                            grew=getattr(b, "grew", None), op=getattr(b, "kept", getattr(b, "op", None)),
                            done=getattr(b, "recruit", None) is not None and len(b.recruit["score"]) == len(OPS),
                            onsets=getattr(b, "onsets", 0), unpred=getattr(b, "unpredicted", 0)))
    return out


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    args = [a for a in sys.argv[1:] if "=" not in a]
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
    seconds = kw.pop("seconds", 300.0)
    seeds = range(*(int(x) for x in (args[0] if args else "0:16").split(":")))
    with ProcessPoolExecutor() as ex:
        res = list(ex.map(run, [(s, seconds, kw) for s in seeds]))
    net = lambda r, k: np.mean([x["ate"] - x["lost"] for x in r if x["kind"] == k])
    d = np.array([net(r, "grow") - net(r, "tracker") for r in res])
    import pickle
    tag = "esc" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items())) + f"_{seeds.start}-{seeds.stop}"
    pickle.dump(d, open(f"/home/pilgrim/git/simple-learner/lab/v/{tag}.d", "wb"))
    boot = [d[np.random.default_rng(i).integers(len(d), size=len(d))].mean() for i in range(2000)]
    rows = [x for r in res for x in r]
    for k in ("grow", "tracker"):
        x = [r for r in rows if r["kind"] == k]
        print(f"{k:8s}: {len(x)} robots, ate {np.mean([r['ate'] for r in x]):.3f}, lost {np.mean([r['lost'] for r in x]):.3f}"
              f" a 10 s, age {np.mean([r['age'] for r in x]):.0f} s", flush=True)
    g = [r for r in rows if r["kind"] == "grow"]
    done = [r for r in g if r["done"]]
    print(f"  grew in {sum(r['grew'] is not None for r in g)} of {len(g)} (median at {np.median([r['grew'] for r in g if r['grew'] is not None] or [0]):.0f} s); "
          f"bites unpredicted {sum(r['unpred'] for r in g)} of {sum(r['onsets'] for r in g)}; finished {len(done)}, kept "
          + ", ".join(f"{o} {sum(r['op'] == o for r in done)}" for o in OPS))
    print(f"{kw}: net (eaten - lost), grow - tracker {d.mean():+.3f} [{np.percentile(boot, 2.5):+.3f}, {np.percentile(boot, 97.5):+.3f}]")
