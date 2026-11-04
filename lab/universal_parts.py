"""universal_parts.py: does sharing one body cost anything? For each world on the validation seeds at its own length: base; the row's automatic
version alone; U with only the part that world calls for; U whole; and each difference. Whole minus alone is interference; alone minus the row's own
version is what the shared detector loses. Then plain and all-food for U whole.
    python lab/universal_parts.py SETTINGS.json [ARM]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import universal as X
import universal_v
import table as T
from table_rows import VALID
from minimal.spec import efficiency

ROWS = json.load(open("/home/pilgrim/git/simple-learner/lab/table_settings.json"))
AUTO = {r.get("world", w): r["auto"] for w, r in ROWS.items() if r.get("auto") and r["auto"][0] != "circuit"}
OFF = {"eye": 0.0, "trustk": 0.0, "growk": 0.0, "pausek": 0.0, "jit": 0.0}
ARM = sys.argv[2] if len(sys.argv) > 2 else "u"
if ARM == "v":
    OFF["bankk"] = 0.0
PART = dict(thrusters="jit", ageing="jit", swap10="trustk", unreliable="trustk", patchy="trustk", weak="trustk", alternate="growk", pattern="growk", digest="pausek", noisy="eye")


def only(kw, part):
    if ARM == "v" and part in ("trustk", "growk"):
        part = "bankk"
    return {**kw, **{k: v for k, v in OFF.items() if k != part}}


def pair(a, b):
    d, i = T.paired(a, b)
    return f"{d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]"


if __name__ == "__main__":
    kw = {"learn": 1.0, **json.load(open(sys.argv[1]))}
    seeds = list(VALID)
    for w, part in PART.items():
        secs = T.LONG.get(w, 100.0)
        B = T.run(w, "circuit", seeds, seconds=secs)
        arm, a = AUTO.get(w, ("circuit", {}))
        R = T.run(w, arm, seeds, a, secs)
        O = T.run(w, ARM, seeds, only(kw, part), secs)
        W = T.run(w, ARM, seeds, kw, secs)
        print(f"{w} ({part}) {secs:.0f} s: base {efficiency(B):.2f}, row's own {arm} {efficiency(R):.2f}, part alone {efficiency(O):.2f}, whole {efficiency(W):.2f}", flush=True)
        print(f"   whole-base {pair(W, B)}; whole-row {pair(W, R)}; whole-alone {pair(W, O)}; alone-row {pair(O, R)}; grew {np.mean([bool(l.grew) for l in W]):.2f} paused {np.mean([bool(l.on) for l in W]):.2f} |x| {np.mean([abs(l.x or 0) for l in W]):.2f}", flush=True)
    for w in ("plain", "allfood"):
        for secs in (100.0, 1000.0):
            B, W = T.run(w, "circuit", seeds, seconds=secs), T.run(w, ARM, seeds, kw, secs)
            print(f"{w} {secs:.0f} s: base {efficiency(B):.2f}, whole {efficiency(W):.2f}, {pair(W, B)}; grew {np.mean([bool(l.grew) for l in W]):.2f} paused {np.mean([bool(l.on) for l in W]):.2f}", flush=True)
