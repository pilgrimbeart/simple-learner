"""D176: is the designed circuit's action limited by its neurons or by its structure? A ruler, not a brain: the
designed circuit's wiring with ideal relays and the knob held right (PRIVILEGED: told which sensor sees food). Each
body pulse on sensor s fires s's side motor (a coin toss at birth, as designed.py) and, if s sees food, the other motor
too (p = 1; poison's p = 0). Each motor also fires on its own as a Poisson stream at `own` per second (the designed
circuit's motors fire about 5.8 per s each without a preceding sensor spike, D176 action_held.json; 0 and 2 for
comparison). Variant "measured": each body pulse relayed with probability `keep`, and each sensor also relays
spontaneous events at `spont` per s, as the designed circuit's sensor neurons do on the held arm (action_held.json:
sensor spikes 43.6 per 10 s per sensor, 20% within a tick of a body pulse; body pulses 18 per 10 s per sensor, so
about 0.47 of pulses relayed and 3.5 spontaneous per s). Same lives as trace.py (seeds 0-31, red then blue as poison, 100 s), scored as analyse.py scores.
python relay_reference.py -> lab/v/robot_shortfall_20261120/relay_reference.json"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from creature import Life
from units import TICK

class Relay:
    def __init__(self, seed, own, keep=1.0, spont=0.0):
        self.rng = np.random.default_rng(seed + 31337); self.own, self.keep, self.spont = own, keep, spont
        self.side = [int(self.rng.integers(2)) for _ in (0, 1)]; self.food = None; self.out = []
    def stimulate(self, s, at):
        if self.rng.random() < self.keep:
            self.fire(s)
    def fire(self, s):
        self.out.append(self.side[s])
        if s == self.food:
            self.out.append(1 - self.side[s])
    def taste(self, v, at): pass
    def step(self):
        for s in (0, 1):
            for _ in range(self.rng.poisson(self.spont * TICK)):
                self.fire(s)
        o = self.out + [m for m in (0, 1) for _ in range(self.rng.poisson(self.own * TICK))]; self.out = []; return o
    def drive(self, s): return 1.0 if s == self.food else 0.0

S = {}
for own, keep, spont in ((0.0, 1, 0), (2.0, 1, 0), (5.8, 1, 0), (5.8, 0.47, 0), (5.8, 1, 3.5), (5.8, 0.47, 3.5)):
    rows, per_seed = [], {}
    for seed in range(32):
        for poison in ("red", "blue"):
            lf = Life(seed, poison, brain=lambda s: Relay(s, own, keep, spont))
            lf.brain.food = lf.sensor["blue" if poison == "red" else "red"]
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
    F, P = sum(r[0] for r in rows), sum(r[1] for r in rows)
    S[f"own_{own}_keep_{keep}_spont_{spont}"] = dict(food=F, poison=P, food_poison_last_third=F / max(P, 1),
                           net_per_10s=[float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))],
                           stranded=sum(r[2] for r in rows), lives=len(rows))
    print(own, keep, spont, S[f"own_{own}_keep_{keep}_spont_{spont}"], flush=True)
json.dump(S, open(ROOT / "lab/v/robot_shortfall_20261120/relay_reference.json", "w"), indent=1)
