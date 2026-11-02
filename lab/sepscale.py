"""sepscale.py K [K ...]: D14's open question, robustness built: the tuned sepb with every node's capacitance and
every current into it scaled by K (resistances by 1/K: the same dynamics, a node's noise down about sqrt(K), its power
up K), except the inputs (S0, S1, T: the body's pulses are fixed charges) and BT (already at the 50 pF limit).
Judged held out with each substrate's noise."""
import sys, json, copy
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from sepb import spec
from minimal.spec import score, summary, parts, violations
from discrete.poison import show

import os
KEEP = ("S0", "S1", "T", "BT")
ONLY = tuple(os.environ["ONLY"].split(",")) if os.environ.get("ONLY") else None   # ONLY=a,b: scale just these
final = json.load(open("/home/pilgrim/git/simple-learner/lab/v/sep_search_silicon.json"))["final"]


def scaled(k):
    s, names = spec(**final)
    s = copy.deepcopy(s)
    sc = [k if (n in ONLY if ONLY else n not in KEEP) else 1.0 for n in names]
    for i, nd in enumerate(s["nodes"]):
        nd[1] *= sc[i]                                  # bias current
        if nd[2] is not None:
            nd[2] /= sc[i]
        nd[3] *= sc[i]
    for el in s["elements"]:
        el[3] *= sc[el[0]]                              # current into the node it drives
    return s


if __name__ == "__main__":
    subs = ("silicon", "biology", "biology x2")
    for k in (float(a) for a in sys.argv[1:]):
        s = scaled(k)
        print(f"K={k:g} ONLY={ONLY}", parts(s), "violations:", violations(s), flush=True)
        for sub in subs:
            print(show(f"  K={k:g} held out, {sub}", summary(score([s], range(50000, 50032), substrate=sub)[0])), flush=True)
