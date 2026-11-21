"""D176: is the knob's random walk P's own resting noise or its E-gated writers' noise? Frozen arm, red lives only
(a seed's two frozen lives are identical); variance of P's change per tick, binned by the gating E. Also the
engine's own resting noise for P's node, from mixed_feedback's substrate, for comparison. Analyst accounting only.
python diffusion.py -> lab/v/robot_shortfall_20261120/diffusion.json"""
import json, pickle
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
BIG = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"
res = [r for r in pickle.load(open(BIG / "frozen_64x100s.pkl", "rb")) if r["poison"] == "red"]
bins = [0, .02, .1, .3, .6, 1.01]
var = {i: [] for i in range(len(bins) - 1)}
for r in res:
    rows = r["rows"].astype(float)
    for k in (0, 1):
        P, E = rows[:, 2 + k], rows[:, k]
        dP = np.diff(P); free = (P[:-1] > .02) & (P[:-1] < .98) & (P[1:] > .02) & (P[1:] < .98)
        for i in range(len(bins) - 1):
            m = free & (E[:-1] >= bins[i]) & (E[:-1] < bins[i + 1])
            var[i].extend(dP[m].tolist())
import sys; sys.path.insert(0, str(ROOT))
from mixed_feedback import SUBSTRATES
from brains.designed import CP
from units import TICK
rest = SUBSTRATES["biology"][1](CP, 0.0, False, 1.0)        # P's node: no leak, not a memory, at 1 V typical
out = dict(bins=bins, n=[len(var[i]) for i in var], sd_per_tick=[float(np.std(var[i])) if var[i] else None for i in var],
           mean_per_tick=[float(np.mean(var[i])) if var[i] else None for i in var],
           resting_noise_sd_per_tick=float(np.sqrt(rest * TICK) / CP),
           resting_noise_sd_per_100s=float(np.sqrt(rest * 100) / CP))
json.dump(out, open(ROOT / "lab/v/robot_shortfall_20261120/diffusion.json", "w"), indent=1)
print(json.dumps(out, indent=1))
