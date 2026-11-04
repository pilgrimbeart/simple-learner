"""universal_read.py: what a random search of the universal circuit says: each world's best and median recovery, which settings help which
world (mean recovery at each value of each knob, and the correlation of log-free values), and whether worlds conflict.
    python lab/universal_read.py LOG"""
import json
import re
import sys
import numpy as np

rows = []
for line in open(sys.argv[1]):
    m = re.match(r"(\d+) score (\S+) plain (\S+) allfood (\S+) (.*?) (\{.*)", line)
    if m:
        toks = m.group(5).split()
        rows.append(dict(i=int(m.group(1)), score=float(m.group(2)), plain=float(m.group(3)), allfood=float(m.group(4)), R=dict(zip(toks[::2], map(float, toks[1::2]))), kw=json.loads(m.group(6))))
worlds = list(rows[0]["R"])
print(len(rows), "settings; score best", max(r["score"] for r in rows), "median", np.median([r["score"] for r in rows]))
print("world: median, best, the top setting's")
top = max(rows, key=lambda r: r["score"])
for w in worlds:
    v = [r["R"][w] for r in rows]
    print(f"  {w}: {np.median(v):.2f} {max(v):.2f} {top['R'][w]:.2f}")
print(f"  plain worst {min(r['plain'] for r in rows):+.3f}, median {np.median([r['plain'] for r in rows]):+.3f}; allfood median {np.median([r['allfood'] for r in rows]):+.2f}")
M = np.array([[r["R"][w] for w in worlds] for r in rows])
print("correlation between worlds' recoveries across settings (negative: they pull apart)")
C = np.corrcoef(M.T)
print("      " + " ".join(f"{w[:4]:>5}" for w in worlds))
for i, w in enumerate(worlds):
    print(f"{w[:5]:5} " + " ".join(f"{C[i, j]:+5.2f}" for j in range(len(worlds))))
print("each knob's mean recovery by value, where it moves a world by at least .1")
for k in rows[0]["kw"]:
    vals = sorted({r["kw"][k] for r in rows})
    if len(vals) < 2:
        continue
    for i, w in enumerate(list(worlds) + ["plain"]):
        y = np.array([r["plain"] if w == "plain" else r["R"][w] for r in rows])
        means = [y[[r["kw"][k] == v for r in rows]].mean() for v in vals]
        if max(means) - min(means) >= (.03 if w == "plain" else .15):
            print(f"  {k:9} {w[:6]:6} " + "  ".join(f"{v:g}:{m:+.2f}" for v, m in zip(vals, means)))
