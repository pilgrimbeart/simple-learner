"""ladder_final2.py: one brain, Diagnose (short 2, tau_v 40, theta 3, tau 10), on every test, held out on seeds 52000-52063 x 2,
paired with the baseline; which cure each life took (lab/ladder.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from collections import Counter
from ladder import run, line, paired
K = dict(theta=3.0, tau=10.0, short=2.0, tau_v=40.0)
for rule in ("plain", "alternate", "pattern", "swap50", "swap20", "swap10", "swap5", "digest"):
    B, L = run(rule, "circuit", range(52000, 52064)), run(rule, "diagnose", range(52000, 52064), K)
    line(f"{rule}", L)
    d, i = paired(L, B)
    print(f"   against the baseline {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]; final length {sorted(Counter(l.n for l in L).items())}", flush=True)
