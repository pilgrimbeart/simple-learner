"""universal_judge.py: the bank of predictors judged once on seeds nothing has touched (55000-55063 x 2 for the first frozen setting, 55100-55163 x 2 for the second), each world against its base, its told target, its
best manual cure and its own row's automatic version; then the plain test and all-food at each length (discrete/NOTEBOOK.md, D29; STORIES.md).
    python lab/universal_judge.py SETTINGS.json [FIRST_SEED]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import table as T
import universal as X
import universal_v
from minimal.spec import efficiency

FRESH = list(range(int(sys.argv[2]) if len(sys.argv) > 2 else 55000, (int(sys.argv[2]) if len(sys.argv) > 2 else 55000) + 64))
ROWS = json.load(open("/home/pilgrim/git/simple-learner/lab/table_settings.json"))
LENGTHS = {"thrusters": (1000.0,), "ageing": (1000.0,), "alternate": (100.0, 400.0), "pattern": (100.0, 400.0), "digest": (100.0, 400.0), "unreliable": (100.0, 400.0), "patchy": (100.0, 400.0), "swap10": (100.0, 400.0), "noisy": (100.0, 400.0), "weak": (100.0, 400.0)}


def pair(a, b):
    d, i = T.paired(a, b)
    return f"{d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]"


if __name__ == "__main__":
    kw = json.load(open(sys.argv[1]))
    print(json.dumps(kw), flush=True)
    for name, r in ROWS.items():
        w = r.get("world", name)
        if w == "plain":
            continue
        for secs in LENGTHS[w]:
            B = T.run(w, "circuit", FRESH, seconds=secs)
            V = T.run(w, "v", FRESH, kw, secs)
            print(f"== {name} {secs:.0f} s: base {efficiency(B):.2f}, bank {efficiency(V):.2f}; bank-base {pair(V, B)}; flips {np.mean([l.flips for l in V]):.1f} grew {np.mean([bool(l.grew) for l in V]):.2f} paused {np.mean([bool(l.on) for l in V]):.2f} |x| {np.mean([abs(l.x or 0) for l in V]):.2f}", flush=True)
            if r.get("target"):
                G = T.run(w, r["target"][0], FRESH, r["target"][1], secs)
                print(f"   told {efficiency(G):.2f}; bank-told {pair(V, G)}", flush=True)
            if r.get("manual"):
                nm, arm, a = r["manual"][0]
                M = T.run(w, arm, FRESH, a, secs)
                print(f"   manual {nm} {efficiency(M):.2f}; bank-manual {pair(V, M)}", flush=True)
            if r.get("auto") and r["auto"][0] != "circuit":
                arm, a = r["auto"]
                A = T.run(w, arm, FRESH, a, secs)
                print(f"   row's own {arm} {efficiency(A):.2f}; bank-row {pair(V, A)}", flush=True)
    for w in ("plain", "allfood"):
        for secs in (100.0, 400.0, 1000.0):
            B, V = T.run(w, "circuit", FRESH, seconds=secs), T.run(w, "v", FRESH, kw, secs)
            print(f"== {w} {secs:.0f} s: base {efficiency(B):.2f}, bank {efficiency(V):.2f}; bank-base {pair(V, B)}; flips {np.mean([l.flips for l in V]):.1f} grew {np.mean([bool(l.grew) for l in V]):.2f} paused {np.mean([bool(l.on) for l in V]):.2f} |x| {np.mean([abs(l.x or 0) for l in V]):.2f}", flush=True)
