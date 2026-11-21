"""D176: do each life's measured neuron statistics explain the held-knob brain's action? From the held arm (P clamped
right), per life: each sensor's share of body pulses it relays (a spike in that tick or the next), its spontaneous
spikes per s, each motor's spikes per s not within a tick of a sensor spike, and each sensor-to-motor relay share (a
motor spike in the tick of a sensor spike or the next). A ruler (not a brain) replays those statistics as independent
random events on the same life: "measured" all as measured; then each fixed to ideal in turn: "keep" (every pulse
relayed), "spont" (no spontaneous sensor spike), "own" (motors' own rate the life's mean of both), "relay" (food's sensor
to both motors, poison's to its side only, each surely). Analyst accounting; scored as analyse.py.
python transfer_reference.py -> lab/v/robot_shortfall_20261120/transfer_reference.json"""
import json, pickle, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from creature import Life
from units import TICK
BIG = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"

def stats(r):
    rows = r["rows"]; n = len(rows); T = n * TICK
    pt = np.zeros((n + 1, 2), int)
    for t, k in r["pulses"]:
        pt[min(int(t / TICK), n), int(k)] += 1
    S, M = rows[:, 4:6] > 0, rows[:, 6:8]
    Snext = S | np.vstack([S[1:], [[False, False]]])
    keep = [float(np.sum(Snext[pt[:n, k] > 0, k]) / max(np.sum(pt[:n, k] > 0), 1)) for k in (0, 1)]
    pprev = (pt[:n] > 0) | np.vstack([[[False, False]], pt[:n - 1] > 0])
    spont = [float(np.sum(S[:, k] & ~pprev[:, k]) / T) for k in (0, 1)]
    anyS = S.any(1); anyprev = anyS | np.concatenate([[False], anyS[:-1]])
    own = [float(M[~anyprev, m].sum() / T) for m in (0, 1)]
    Mn = M > 0; Mnext = Mn | np.vstack([Mn[1:], [[False, False]]])
    relay = [[float(np.sum(Mnext[S[:, k], m]) / max(S[:, k].sum(), 1)) for m in (0, 1)] for k in (0, 1)]
    return dict(keep=keep, spont=spont, own=own, relay=relay)

class Replay:
    def __init__(self, seed, st):
        self.rng = np.random.default_rng(seed + 4242); self.st = st; self.out = []
    def stimulate(self, s, at):
        if self.rng.random() < self.st["keep"][s]:
            self.fire(s)
    def fire(self, s):
        for m in (0, 1):
            if self.rng.random() < self.st["relay"][s][m]:
                self.out.append(m)
    def taste(self, v, at): pass
    def step(self):
        for s in (0, 1):
            for _ in range(self.rng.poisson(self.st["spont"][s] * TICK)):
                self.fire(s)
        o = self.out + [m for m in (0, 1) for _ in range(self.rng.poisson(self.st["own"][m] * TICK))]
        self.out = []; return o
    def drive(self, s): return 0.0

held = {(r["seed"], r["poison"]): r for r in pickle.load(open(BIG / "held_64x100s.pkl", "rb"))}
def ideal(st, which, r):
    st = json.loads(json.dumps(st))
    if which in ("keep", "all"): st["keep"] = [1.0, 1.0]
    if which in ("spont", "all"): st["spont"] = [0.0, 0.0]
    if which in ("own", "all"): st["own"] = [float(np.mean(st["own"]))] * 2
    if which in ("relay", "all"):
        food = r["sensor"]["blue" if r["poison"] == "red" else "red"]
        for k in (0, 1):
            side = int(np.argmax(st["relay"][k])) if k != food else None
            st["relay"][k] = [1.0, 1.0] if k == food else [float(m == side) for m in (0, 1)]
    return st
S, per = {}, []
for r in held.values():
    per.append(dict(seed=r["seed"], poison=r["poison"], **stats(r)))
for which in ("measured", "keep", "spont", "own", "relay", "all"):
    rows, per_seed = [], {}
    for (seed, poison), r in held.items():
        st = ideal(stats(r), which, r)
        lf = Life(seed, poison, brain=lambda s: Replay(s, st))
        n = int(round(100 / TICK))
        while lf.t < n:
            lf.step()
        start = lf.moving if lf.moving is not None else n
        a = start + 2 * (n - start) / 3
        part = [c for m, c in lf.meals if a <= m < n]
        p, f = sum(c == poison for c in part), sum(c != poison for c in part)
        rows.append((f, p, not lf.meals)); per_seed.setdefault(seed, []).append(10 * (f - p) / max((n - a) * TICK, 1e-9))
    rng = np.random.default_rng(176); x = np.array([np.mean(v) for v in per_seed.values()])
    m = x[rng.integers(0, len(x), (4000, len(x)))].mean(1)
    F, P = sum(q[0] for q in rows), sum(q[1] for q in rows)
    S[which] = dict(food=F, poison=P, food_poison_last_third=F / max(P, 1),
                    net_per_10s=[float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))],
                    stranded=sum(q[2] for q in rows))
    print(which, S[which], flush=True)
own = np.array([p["own"] for p in per]); keep = np.array([p["keep"] for p in per])
S["per_life_summary"] = dict(own_ratio_max_min_median=float(np.median(own.max(1) / np.maximum(own.min(1), 1e-3))),
                             own_quartiles=np.percentile(own, [10, 50, 90]).tolist(), keep_quartiles=np.percentile(keep, [10, 50, 90]).tolist())
S["per_life"] = per
json.dump(S, open(ROOT / "lab/v/robot_shortfall_20261120/transfer_reference.json", "w"), indent=1)
print(S["per_life_summary"])
