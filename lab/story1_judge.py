"""story1_judge.py [SEEDS]: the pilot story's ladder held out, then its detection and its controls (lab/story1.py)."""
import pickle, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from story1 import lives, paired, table, M, ROOT
from minimal.spec import gain
p, spread = M.from_bench()
lo, hi = (int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "50000:50064").split(":"))
seeds = range(lo, hi)
run = lambda n: dict(fstep=9.0, drift=0.0, V_L=0.0, step=0.5, V_H=0.5 * n - 0.25)
ARMS = [("still", "still", {}), ("unwired", "unwired", {}), ("wrong", "wrong", {}), ("told", "told", {}),
        ("bayes", "bayes", {}), ("B", "B", {}),
        ("count2", "B", dict(fstep=0.0, drift=0.0, V_L=0.0, step=0.5, V_H=0.75)),
        ("fade3_5s", "B", dict(fstep=0.0, drift=0.1, V_L=0.0, step=0.5, V_H=1.25)),
        ("tally", "B", dict(fstep=2 * p["step"], drift=0.0, V_H=p["V_L"] + 1.75 * p["step"])),
        ("run1", "B", run(1)), ("run2", "B", run(2)), ("run3", "B", run(3)),
        ("path_block", "path", dict(reverse=0, theta=0.5, cost=1, trust=3, tau=30)),
        ("path_reverse", "path", dict(reverse=1, theta=1.5, cost=1, trust=3, tau=0)),
        ("grow", "grow", {})]
R = {}
for name, arm, g in ARMS:
    R[name] = lives(arm, dict(p, **g), spread, seeds)
    table(name, R[name])
pickle.dump(R, open(f"{ROOT}/lab/v/story1_ladder_{lo}.lives", "wb"))
print("\npaired, efficiency [95%], against told and against B")
for name in R:
    if name in ("told", "B"): continue
    a, ia = paired(R[name], R["told"]); b, ib = paired(R[name], R["B"])
    print(f"  {name}: told {a:+.2f} [{ia[0]:+.2f}, {ia[1]:+.2f}]  B {b:+.2f} [{ib[0]:+.2f}, {ib[1]:+.2f}]")
print("\ndetection: the bit's first flip when born wrong, false flips when born right, share of life right")
for name in ("bayes", "B", "count2", "fade3_5s", "tally", "run1", "run2", "run3"):
    L = R[name]
    w = [l for l in L if not l.born_right]; r = [l for l in L if l.born_right]
    t = [l.flips[0] if l.flips else np.inf for l in w]
    print(f"  {name}: born wrong {len(w)}: median first flip {np.median(t):.1f} s, 90th {np.percentile(t, 90):.1f} s, never {sum(np.isinf(t))}; "
          f"born right {len(r)}: {np.mean([bool(l.flips) for l in r]):.0%} ever flip, {np.mean([len(l.flips) for l in r]):.1f} flips a life; right {np.mean([l.right for l in L]):.1%}")
for name in ("path_block", "path_reverse"):
    L = R[name]
    pe = [l.blocked[l.poison_eye] for l in L]; fe = [l.blocked[1 - l.poison_eye] for l in L]
    t = [x if x is not None else np.inf for x in pe]
    print(f"  {name}: poison eye changed in {sum(x is not None for x in pe)} of {len(L)}, median {np.median(t):.1f} s; food eye changed in {sum(x is not None for x in fe)}")
print("\ncontrols")
for ctl in ("all-food", "random"):
    for name, arm, g in [("unwired", "unwired", {}), ("told", "told", {}), ("B", "B", {}), ("run3", "B", run(3)),
                         ("path_reverse", "path", dict(reverse=1, theta=1.5, cost=1, trust=3, tau=0)), ("still", "still", {})]:
        L = lives(arm, dict(p, **g), spread, seeds, control=ctl)
        extra = f"flips a life {np.mean([len(l.flips) for l in L]):.2f}" if arm == "B" else (f"eyes changed a life {np.mean([sum(x is not None for x in l.blocked) for l in L]):.2f}" if arm == "path" else "")
        table(f"{ctl} {name}", L); print("   ", extra, flush=True)
