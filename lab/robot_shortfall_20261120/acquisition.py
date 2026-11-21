"""D176: acquisition time, as creature.one_life defines learned (the poison's sensor's knob within 0.2 of 0 and the
food's within 0.2 of 1, checked every 0.5 s after moving began): seconds after moving, per learning arm.
python acquisition.py -> lab/v/robot_shortfall_20261120/acquisition.json"""
import json, pickle
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
BIG = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"
S = {}
for tag in ("learn_64x100s", "learn-mem_64x100s", "learn_64x100s_half", "frozen_64x100s", "learn-mem-thr_64x100s",
            "frozen-mem-thr_64x100s", "learn_64x100s_quarter", "frozen_64x100s_quarter"):
    res = pickle.load(open(BIG / f"{tag}.pkl", "rb")); when = []; ever_left = 0
    for r in res:
        rows = r["rows"]; food = r["sensor"]["blue" if r["poison"] == "red" else "red"]; pois = 1 - food
        t0 = r["moving"]; got = None
        if t0 is not None:
            for t in range(t0, len(rows), 50):
                if rows[t, 2 + pois] <= .2 and rows[t, 2 + food] >= .8:
                    got = (t - t0) * 0.01; break
        if got is not None:
            when.append(got)
            after = rows[int(got / 0.01) + t0:, :]
            ever_left += int(np.any((after[:, 2 + pois] > .2) | (after[:, 2 + food] < .8)))
    S[tag] = dict(lives=len(res), learned=len(when), median_s=float(np.median(when)) if when else None,
                  later_lost_it=ever_left)
    print(tag, S[tag])
json.dump(S, open(ROOT / "lab/v/robot_shortfall_20261120/acquisition.json", "w"), indent=1)
