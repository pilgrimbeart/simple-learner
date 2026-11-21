"""D178 bug fix to stage1.py (logged): its paired silicon-biology sensor-response contrast returned NaN when a seed had
a life with no pulses to either sensor (nanmean of all-NaN). Recomputed here from the saved replays, skipping such
lives (each seed kept if any life has a defined response), plus the sensor-spike purity contrast.
python stage1_resp.py -> lab/v/robot_action_20261120/stage1_resp.json"""
import json, pickle, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics as M
BIG = Path.home() / "nca-scratch-backup/robot_action_20261120"
rep = pickle.load(open(BIG / "stage1_replay.pkl", "rb"))
out = {}
def f_resp(x):
    v = [x["resp"][f"S{k}"]["resp"] for k in (0, 1) if x["resp"][f"S{k}"]["resp"] is not None]
    return float(np.mean(v)) if v else None
f_pur = lambda x: x["resp"]["sensor_spike_purity"]
for a in ("learn", "informed"):
    for src in ("biology", "silicon"):
        for name, f in (("sensor_resp", f_resp), ("sensor_spike_purity", f_pur)):
            sm = {}
            for tgt in ("biology", "silicon"):
                d = {}
                for x in rep:
                    if x["tag"] == f"{a}_{src}_s0-31" and x["target"] == tgt and f(x) is not None:
                        d.setdefault(x["seed"], []).append(f(x))
                sm[tgt] = {k: np.mean(v) for k, v in d.items()}
            ks = sorted(set(sm["silicon"]) & set(sm["biology"]))
            out[f"{a}_inputs-{src}_silicon-biology_{name}"] = M.boot([sm["silicon"][k] - sm["biology"][k] for k in ks]) + [len(ks)]
json.dump(out, open(HERE.parents[1] / "lab/v/robot_action_20261120/stage1_resp.json", "w"), indent=1)
for k, v in out.items(): print(k, [round(x, 3) for x in v])
