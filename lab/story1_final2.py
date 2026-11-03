"""story1_final2.py: story 1 re-judged with the run's 1 s limit in every arm (the baseline since 2026-11-02), the settings
as chosen without it: rates recaptured on training seeds; the ladder on 50000-50063 x 2; the final on 50200-50327 x 2."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from story1 import lives, paired, table, stats, M, ROOT
from minimal.spec import gain, efficiency
p0, spread = M.from_bench()
RM = 1.0
RATES2 = ROOT + "/lab/v/story1_rates_limit.json"
stats(range(0, 64), extra=dict(run_max=RM), path=RATES2)
p = dict(p0, run_max=RM, rates=RATES2)
run = lambda n: dict(fstep=9.0, drift=0.0, V_L=0.0, step=0.5, V_H=0.5 * n - 0.25)
print("ladder, 50000-50063 x 2", flush=True)
S = range(50000, 50064)
for name, arm, g in [("still", "still", {}), ("unwired", "unwired", {}), ("told", "told", {}), ("bayes", "bayes", {}), ("B", "B", {}),
                     ("count2", "B", dict(fstep=0.0, drift=0.0, V_L=0.0, step=0.5, V_H=0.75)), ("run1", "B", run(1)), ("run2", "B", run(2)), ("run3", "B", run(3)),
                     ("fade3_5s", "B", dict(fstep=0.0, drift=0.1, V_L=0.0, step=0.5, V_H=1.25)),
                     ("tally", "B", dict(fstep=2 * p0["step"], drift=0.0, V_H=p0["V_L"] + 1.75 * p0["step"])),
                     ("path_block", "path", dict(reverse=0, theta=0.5, cost=1, trust=3, tau=30)),
                     ("path_reverse", "path", dict(reverse=1, theta=1.5, cost=1, trust=3, tau=0)),
                     ("circuit", "gated", dict(use=0, trust=1))]:
    table(name, lives(arm, dict(p, **g), spread, S))
print("final, 50200-50327 x 2", flush=True)
S = range(50200, 50328)
R = {}
for n, arm, g in [("unwired", "unwired", {}), ("told", "told", {}), ("bayes", "bayes", {}), ("B", "B", {}), ("circuit", "gated", dict(use=0, trust=1))]:
    R[n] = lives(arm, dict(p, **g), spread, S); table(n, R[n])
for a, b in [("circuit", "told"), ("circuit", "bayes"), ("circuit", "B"), ("circuit", "unwired"), ("bayes", "told"), ("B", "told")]:
    for lab, f in (("efficiency", efficiency), ("gain", gain)):
        d, i = paired(R[a], R[b], f)
        print(f"{a} - {b} {lab}: {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]")
for n in ("bayes", "B", "circuit"):
    L = R[n]; w = [l for l in L if not l.born_right]; r = [l for l in L if l.born_right]
    t = [l.flips[0] if l.flips else np.inf for l in w]
    print(f"{n}: born wrong {len(w)}: first flip median {np.median(t):.1f} s, 90th {np.percentile(t, 90):.1f} s, never {sum(np.isinf(t))}; born right {len(r)}: {np.mean([bool(l.flips) for l in r]):.1%} ever flip; right {np.mean([l.right for l in L]):.1%}")
g = dict(p, use=0, trust=1)
for c in ("all-food", "random"):
    L = lives("gated", g, spread, S, control=c); table(f"{c} circuit", L); print(f"   flips a life {np.mean([len(l.flips) for l in L]):.2f}", flush=True)
    table(f"{c} told", lives("told", p, spread, S, control=c))
    table(f"{c} unwired", lives("unwired", p, spread, S, control=c))
