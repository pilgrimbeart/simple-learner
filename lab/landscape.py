"""landscape.py: B's efficiency as each spending knob alone is scaled (others at B), 64 lives of 100 s each, the
same lives for every setting (paired), robustly judged: how strong the signal a self-tuner climbs is."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from minimal.spec import summary
if __name__ == "__main__":
    p, sd = M.from_bench()
    base = summary(M.lives(p, sd, range(60000, 60032)))["efficiency"]
    print("B", round(base, 2))
    for k in ("hold", "bored", "scan", "drive", "run"):
        row = []
        for f in (1 / 3, 0.5, 0.7, 1.4, 2.0, 3.0):
            row.append(round(summary(M.lives(dict(p, **{k: p[k] * f}), sd, range(60000, 60032)))["efficiency"] - base, 2))
        print(f"{k:6s} x1/3..x3:", row, flush=True)
