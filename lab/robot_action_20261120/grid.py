"""D178 R8.1: rank the eight informed settings on screening seeds 0-7 by net_ft (food rate and stranding shown).
python grid.py <substrate> [eval] -> lab/v/robot_action_20261120/grid_<substrate>.json"""
import json, pickle, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics as M
BIG = Path.home() / "nca-scratch-backup/robot_action_20261120"
OUT = HERE.parents[1] / "lab/v/robot_action_20261120"
sub = sys.argv[1]
rows = []
for f in ("0.5", "0.75", "1.0"):
    for q in ("0", "0.25", "0.5"):
        if (f, q) == ("0.5", "0.5"):
            continue
        res = pickle.load(open(BIG / f"informed_at{f}-{q}_{sub}_s0-7.pkl", "rb"))
        S = M.summary(res)
        rows.append(dict(food_knob=float(f), poison_knob=float(q), net_ft=S["net_ft"], food_rate_ft=S["food_rate_ft"],
                         poison_rate_ft=S["poison_rate_ft"], stranded=S["stranded"][0], lives=S["lives"]))
rows.sort(key=lambda r: -r["net_ft"][0])
out = dict(substrate=sub, screen_seeds="0-7", ranking=rows, selected=rows[0])
json.dump(out, open(OUT / f"grid_{sub}.json", "w"), indent=1)
for r in rows: print(r["food_knob"], r["poison_knob"], [round(x, 3) for x in r["net_ft"]], round(r["food_rate_ft"][0], 3), r["stranded"])
