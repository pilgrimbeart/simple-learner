"""D176: where does the held perfect knob's knowledge get lost in action? On the held arm (P clamped right; analyst
labels from the wiring): (1) how many motor spikes follow a sensor spike (same or previous tick) rather than arising
on their own; (2) how many sensor spikes follow a body pulse (same or previous tick); (3) for each poison meal, the
poison sensor's activity just before (pulses in the last 0.5 s, time since its last), against food meals.
python action.py [arm] -> lab/v/robot_shortfall_20261120/action_<arm>.json"""
import json, pickle, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
BIG = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"
arm = sys.argv[1] if len(sys.argv) > 1 else "held"
res = pickle.load(open(BIG / f"{arm}_64x100s.pkl", "rb"))
TICK = 0.01
mot_caused = mot_all = sen_caused = sen_all = 0
meal = {True: [], False: []}
for r in res:
    rows = r["rows"]; n = len(rows)
    S = rows[:, 4:6].sum(1) > 0
    Sprev = S | np.concatenate([[False], S[:-1]])
    M = rows[:, 6:8].sum(1)
    mot_all += M.sum(); mot_caused += M[Sprev].sum()
    pt = np.zeros(n, bool)
    if len(r["pulses"]):
        pt[np.minimum((r["pulses"][:, 0] / TICK).astype(int), n - 1)] = True
    ptp = pt | np.concatenate([[False], pt[:-1]])
    Sn = rows[:, 4:6].sum(1)
    sen_all += Sn.sum(); sen_caused += Sn[ptp].sum()
    if r["arm"] == "allfood":
        continue
    pois_k = r["sensor"][r["poison"]]
    for m, c in r["meals"]:
        t = (m + 1) * TICK; p = r["pulses"]
        k = r["sensor"][c]
        own = p[(p[:, 1] == k) & (p[:, 0] <= t)][:, 0] if len(p) else np.zeros(0)
        meal[c != r["poison"]].append(dict(recent=int(np.sum(own > t - 0.5)), since=float(t - own[-1]) if len(own) else None))
def summ(v):
    since = [x["since"] for x in v if x["since"] is not None]
    return dict(n=len(v), seen_within_0_5s=float(np.mean([x["recent"] > 0 for x in v])),
                pulses_last_0_5s_median=float(np.median([x["recent"] for x in v])), since_last_median_s=float(np.median(since)))
out = dict(arm=arm, motor_spikes=int(mot_all), motor_after_sensor_spike=float(mot_caused / mot_all),
           sensor_spikes=int(sen_all), sensor_after_body_pulse=float(sen_caused / sen_all))
if meal[True]:
    out.update(food_meals=summ(meal[True]), poison_meals=summ(meal[False]))
json.dump(out, open(ROOT / f"lab/v/robot_shortfall_20261120/action_{arm}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
