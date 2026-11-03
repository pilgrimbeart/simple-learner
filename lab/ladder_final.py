"""ladder_final.py: every test's final judgement, on seeds 52000-52063 x 2, which chose nothing, and longer lives on 52100-52131
x 2: baseline, target, the manual interventions and the automated circuits (settings chosen on training seeds; lab/ladder.py)."""
import pickle, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from collections import Counter
from ladder import run
from ladder import line, paired
G = dict(theta=3.0, tau=10.0)
T = {"plain": [("baseline", "circuit", {}), ("target", "told", {}), ("grow", "grow", G), ("cycle 6", "cycle", dict(cycle=6.0)), ("volatile", "volatile", dict(tau=40.0)), ("learnpause", "learnpause", {})],
     "alternate": [("baseline", "circuit", {}), ("target", "told", {}), ("flip", "flip", {}), ("alteye", "alteye", {}), ("cycle 2", "cycle", dict(cycle=2.0)), ("cycle 6", "cycle", dict(cycle=6.0)), ("grow", "grow", G)],
     "pattern": [("baseline", "circuit", {}), ("target", "told", {}), ("cycle 3", "cycle", dict(cycle=3.0)), ("cycle 6", "cycle", dict(cycle=6.0)), ("grow", "grow", G)],
     "swap50": [("baseline", "circuit", {}), ("target", "told", {}), ("no trust", "circuit", dict(trust=0)), ("volatile", "volatile", dict(tau=40.0)), ("clock", "rhythm3", {}), ("grow", "grow", G)],
     "swap20": [("baseline", "circuit", {}), ("target", "told", {}), ("no trust", "circuit", dict(trust=0)), ("volatile", "volatile", dict(tau=40.0)), ("clock", "rhythm3", {}), ("grow", "grow", G)],
     "swap10": [("baseline", "circuit", {}), ("target", "told", {}), ("no trust", "circuit", dict(trust=0)), ("volatile", "volatile", dict(tau=40.0)), ("clock", "rhythm3", {}), ("grow", "grow", G)],
     "swap5": [("baseline", "circuit", {}), ("target", "told", {}), ("no trust", "circuit", dict(trust=0)), ("volatile", "volatile", dict(tau=40.0)), ("clock", "rhythm3", {}), ("grow", "grow", G)],
     "digest": [("baseline", "circuit", {}), ("target", "pause", dict(told=1.0, pause=1.0)), ("pause, bit learned", "pause", dict(pause=1.0)), ("learned", "learnpause", {})]}
S = range(52000, 52064)
for rule, arms in T.items():
    R = {}
    for name, arm, kw in arms:
        R[name] = run(rule, arm, S, kw)
        line(f"{rule}: {name}", R[name])
        if arm == "grow":
            print("   final length", sorted(Counter(l.n for l in R[name]).items()), "first growth", np.median([l.grew[0][0] for l in R[name] if l.grew] or [0]), flush=True)
        if arm == "learnpause":
            print("   on in", sum(bool(l.on_at) for l in R[name]), "of", len(R[name]), "median at", np.median([l.on_at[0] for l in R[name] if l.on_at] or [0]), flush=True)
    for name in R:
        if name in ("baseline", "target"):
            continue
        a, ia = paired(R[name], R["baseline"]); b, ib = paired(R[name], R["target"])
        print(f"   {rule} {name}: baseline {a:+.2f} [{ia[0]:+.2f}, {ia[1]:+.2f}]  target {b:+.2f} [{ib[0]:+.2f}, {ib[1]:+.2f}]", flush=True)
print("\nlonger lives, 400 s, 52100-52131 x 2", flush=True)
S = range(52100, 52132)
for rule, arms in {"alternate": [("target", "told", {}), ("grow", "grow", G), ("cycle 2", "cycle", dict(cycle=2.0))], "pattern": [("target", "told", {}), ("grow", "grow", G), ("cycle 3", "cycle", dict(cycle=3.0))],
                   "digest": [("target", "pause", dict(told=1.0, pause=1.0)), ("learned", "learnpause", {})], "plain": [("target", "told", {}), ("grow", "grow", G), ("learnpause", "learnpause", {})]}.items():
    R = {}
    for name, arm, kw in arms:
        R[name] = run(rule, arm, S, kw, seconds=400.0)
        line(f"{rule} 400 s: {name}", R[name])
    for name in R:
        if name != "target":
            b, ib = paired(R[name], R["target"])
            print(f"   {name} against target {b:+.2f} [{ib[0]:+.2f}, {ib[1]:+.2f}]", flush=True)
