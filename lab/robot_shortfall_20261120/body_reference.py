"""D176: what the body allows on the same lives as trace.py's arms (seeds 0-31, red then blue as poison, 100 s): the
best policy of discrete/NOTEBOOK.md D10 (hold and drive: scan 16, drive 40 per s, hold 0.2 s, bored after 3 s, roam
until seen, avoid "drop"), told the answer from birth (oracle: PRIVILEGED, a ruler, not a brain), scored as
analyse.py scores the arms (last third after moving began). python body_reference.py -> lab/v/robot_shortfall_20261120/body_reference.json"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from creature import Life
from discrete.policies import Policy
from units import TICK
P = dict(scan=16, drive=40, hold=0.2, bored=3.0, roam=1.0, roam_rate=40, until_seen=True, avoid="drop",
         learn="toggle", n=10**9, oracle=True)
rows, per_seed = [], {}
for seed in range(32):
    for poison in ("red", "blue"):
        lf = Life(seed, poison, brain=lambda s: Policy(s, "hold_drive", **P))
        lf.brain.good = lf.sensor[next(c for c in lf.sensor if c != poison)]
        n = int(round(100 / TICK))
        while lf.t < n:
            lf.step()
        start = lf.moving if lf.moving is not None else n
        a = start + 2 * (n - start) / 3
        part = [c for m, c in lf.meals if a <= m < n]
        p, f = sum(c == poison for c in part), sum(c != poison for c in part)
        rows.append(dict(seed=seed, poison=poison, food=f, poison_eaten=p, seconds=(n - a) * TICK, stranded=not lf.meals))
        per_seed.setdefault(seed, []).append(10 * (f - p) / max((n - a) * TICK, 1e-9))
rng = np.random.default_rng(176); x = np.array([np.mean(v) for v in per_seed.values()])
m = x[rng.integers(0, len(x), (4000, len(x)))].mean(1)
F, Pn = sum(r["food"] for r in rows), sum(r["poison_eaten"] for r in rows)
S = dict(policy=P, food=F, poison=Pn, food_poison_last_third=F / max(Pn, 1), net_per_10s=[float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))],
         stranded=sum(r["stranded"] for r in rows), lives=len(rows), rows=rows)
json.dump(S, open(ROOT / "lab/v/robot_shortfall_20261120/body_reference.json", "w"), indent=1)
print(json.dumps({k: v for k, v in S.items() if k != "rows"}, indent=1))
