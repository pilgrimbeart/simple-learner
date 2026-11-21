"""D176: is the memory knob's steady drift its two writers' current at rest? For each seed's brain (P as memory nodes,
as trace.py -mem), the mismatched writer elements into each P (gated by E, driven by the taste node) are read from the
built arrays; their summed current at rest is predicted (a) with the taste node exactly at 0 V, (b) averaged over the
taste node's own resting voltages, sampled each tick over 20 s of an unstimulated circuit, and compared per knob with
the drift rate measured on the frozen-mem lives (drift-mem.json). Analyst accounting only.
python rest_writers.py -> lab/v/robot_shortfall_20261120/rest_writers.json"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from trace import make_brain
from units import TICK
meas = {(d["seed"], d["k"]): d.get("rate_per_s_per_V") for d in json.load(open(ROOT / "lab/v/robot_shortfall_20261120/drift-mem.json"))["per_knob"]}
Logged = make_brain(True)
rows = []
def current(el, j, T):
    gain, off, slope = el[0, j], el[1, j], el[2, j]
    return gain / (1 + np.exp(-slope * (T - off)))
for seed in range(32):
    b = Logged(seed); c = b.circuit; c._ready()
    t = c.names.index("taste")
    Ts = []
    for _ in range(2000):
        c.run(TICK); Ts.append(c.V[t])
    Ts = np.array(Ts)
    for k in (0, 1):
        P = b.P[k]; cap = c.node_arr[2, P]
        js = [j for j in range(c.link.shape[1]) if c.link[0, j] == P and c.link[1, j] == t]
        at0 = sum(current(c.el_arr, j, 0.0) for j in js) / cap
        avg = sum(np.mean(current(c.el_arr, j, Ts)) for j in js) / cap
        rows.append(dict(seed=seed, k=k, predicted_at_0V=float(at0), predicted_over_rest=float(avg), measured=meas.get((seed, k)),
                         offsets=[float(c.el_arr[1, j]) for j in js], taste_rest_sd=float(Ts.std())))
ok = [r for r in rows if r["measured"] is not None]
m = np.array([r["measured"] for r in ok]); a = np.array([r["predicted_at_0V"] for r in ok]); b_ = np.array([r["predicted_over_rest"] for r in ok])
S = dict(n=len(ok), corr_at_0V=float(np.corrcoef(m, a)[0, 1]), corr_over_rest=float(np.corrcoef(m, b_)[0, 1]),
         median_ratio_measured_over_rest=float(np.median(m / b_)), sign_agree_over_rest=int(np.sum(np.sign(m) == np.sign(b_))),
         taste_rest_sd_median=float(np.median([r["taste_rest_sd"] for r in rows])), rows=rows)
json.dump(S, open(ROOT / "lab/v/robot_shortfall_20261120/rest_writers.json", "w"), indent=1)
print(json.dumps({k: v for k, v in S.items() if k != "rows"}, indent=1))
