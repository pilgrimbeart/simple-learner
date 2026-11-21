"""D178 R8.2: the motor-bias finalist (-1.3 nA) against baseline (-1.6 nA), closed loop, silicon, seeds 0-31, informed
and all-food, paired. python family_eval.py -> lab/v/robot_action_20261120/family_eval.json"""
import json, pickle, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics as M
BIG = Path.home() / "nca-scratch-backup/robot_action_20261120"
out = {}
for a in ("informed", "allfood"):
    base = pickle.load(open(BIG / f"{a}_silicon_s0-31.pkl", "rb"))
    cand = pickle.load(open(BIG / f"{a}_silicon_s0-31_bias-motor-1.3e-09.pkl", "rb"))
    keys = ("net_ft", "food_rate_ft", "poison_rate_ft", "stranded", "path", "motor_rate", "food_ft", "poison_ft")
    out[a] = dict(candidate={k: M.summary(cand)[k] for k in keys}, baseline={k: M.summary(base)[k] for k in keys},
                  diff={k: M.paired(cand, base, k) for k in ("net_ft", "food_rate_ft", "poison_rate_ft", "stranded", "path", "motor_rate")})
json.dump(out, open(HERE.parents[1] / "lab/v/robot_action_20261120/family_eval.json", "w"), indent=1)
for a, v in out.items():
    print(a, "cand", {k: v["candidate"][k] for k in ("net_ft", "stranded", "food_ft", "poison_ft")})
    print(a, "base", {k: v["baseline"][k] for k in ("net_ft", "stranded", "food_ft", "poison_ft")})
    print(a, "diff", {k: [round(x, 3) for x in d] for k, d in v["diff"].items()})
