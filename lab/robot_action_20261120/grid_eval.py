"""D178 R8.1: the screen's selected setting on seeds 8-31 against nominal (1, 0) on the same lives (development).
python grid_eval.py -> lab/v/robot_action_20261120/grid_eval.json"""
import json, pickle, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics as M
BIG = Path.home() / "nca-scratch-backup/robot_action_20261120"
out = {}
for sub, sel in (("silicon", "1.0-0.5"), ("biology", "0.75-0.25")):
    nom = [r for r in pickle.load(open(BIG / f"informed_{sub}_s0-31.pkl", "rb")) if r["seed"] >= 8]
    s = pickle.load(open(BIG / f"informed_at{sel}_{sub}_s8-31.pkl", "rb"))
    out[sub] = dict(selected=sel, selected_summary={k: M.summary(s)[k] for k in ("net_ft", "food_rate_ft", "poison_rate_ft", "stranded", "path")},
                    nominal_summary={k: M.summary(nom)[k] for k in ("net_ft", "food_rate_ft", "poison_rate_ft", "stranded", "path")},
                    diff_net_ft=M.paired(s, nom), diff_food_rate=M.paired(s, nom, "food_rate_ft"),
                    diff_poison_rate=M.paired(s, nom, "poison_rate_ft"), diff_stranded=M.paired(s, nom, "stranded"))
json.dump(out, open(HERE.parents[1] / "lab/v/robot_action_20261120/grid_eval.json", "w"), indent=1)
print(json.dumps(out, indent=1))
