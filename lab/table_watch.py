"""table_watch.py: each row's automatic version seen through its life, without a display: when its mechanism kicks in, and the efficiency
in each third of life, on 8 fresh seeds x 2 (lab/table_settings.json; discrete/NOTEBOOK.md, D28). Also row 1 with both eyes followed until the first bad."""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import table as T
import universal
from minimal.spec import efficiency, summary

R = json.load(open("/home/pilgrim/git/simple-learner/lab/table_settings.json"))
S = range(54100, 54108)
for name, r in R.items():
    if not r.get("auto") or r["auto"][0] == "circuit":
        continue
    w, (arm, kw) = r["world"], r["auto"]
    for sec in r.get("lengths", [T.LONG.get(w, 100.0)])[-1:]:
        L = T.run(w, arm, S, kw, sec)
        P = T.run("plain", arm, S, kw, sec)
        F = lambda L: [round(float(np.mean([(l.thirds[i].food - l.thirds[i].poison) if hasattr(l, "thirds") else 0 for l in L])), 2) for i in range(3)]
        print(f"{name} {arm} {sec:.0f} s: {efficiency(L):.2f}; flips {np.mean([l.flips for l in L]):.1f} (plain {np.mean([l.flips for l in P]):.1f}); "
              f"first growth at {np.round(np.median([l.grew[0][0] for l in L if l.grew]), 0) if any(l.grew for l in L) else '-'} in {sum(bool(l.grew) for l in L)}/{len(L)} (plain {sum(bool(l.grew) for l in P)}); "
              f"pause on at {np.round(np.median([l.on[0] for l in L if l.on]), 0) if any(l.on for l in L) else '-'} in {sum(bool(l.on) for l in L)}/{len(L)} (plain {sum(bool(l.on) for l in P)}); "
              f"mean |x| {np.mean([abs(l.x or 0) for l in L]):.2f} (plain {np.mean([abs(l.x or 0) for l in P]):.2f}); sweeps {np.mean([l.sweeps for l in L]):.1f} (plain {np.mean([l.sweeps for l in P]):.1f})", flush=True)
OFF = dict(eye=0.0, trustk=0.0, growk=0.0, pausek=0.0, jit=0.0)
kw = dict(OFF, open=1.0)
S2 = list(T.TRAIN) + list(range(53016, 53048))
for w in ("plain", "allfood"):
    A, B = T.run(w, "u", S2, kw), T.run(w, "circuit", S2)
    U = T.run(w, "unwired", S2)
    print(f"row 1, open until the first bad, {w}: {efficiency(A):.2f}; circuit {efficiency(B):.2f}; unwired {efficiency(U):.2f}; against the circuit {T.paired(A, B)}; against unwired {T.paired(A, U)}", flush=True)
