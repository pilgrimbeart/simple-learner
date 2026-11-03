"""ladder_try3.py: third round, training seeds 0-63 x 2: the sequence memory by length; the tracking clock (lab/ladder.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from ladder import run, line
for rule, arm, kw in [(r, "cycle", dict(cycle=float(n))) for r in ("plain", "alternate", "pattern") for n in (1, 2, 3, 6)] + \
    [(r, "cycle", dict(cycle=float(n), trust=2.0)) for r in ("alternate", "pattern") for n in (2, 3)] + \
    [(r, "rhythm3", {}) for r in ("plain", "swap50", "swap20", "swap10", "swap5")] + [("swap10", "rhythm3", dict(lag=0.5)), ("swap10", "rhythm3", dict(lag=1.5)), ("swap5", "rhythm3", dict(lag=0.5))]:
    line(f"{rule} {arm} {kw}", run(rule, arm, range(0, 64), kw))
