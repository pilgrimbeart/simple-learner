"""stage2_report.py: stage 2a's numbers, after the labels were written. Development, hand-picked: engine proving, not stage 3.
    .venv/bin/python lab/stage2_report.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from stage2_run import table, pdiff, ci_eff, sigma, gs

rows, cost, res = table()
print()
rule = [r for r in rows if r["group"] not in ("control",) and np.isfinite(r["x"]) and r["gap"] > 0.2 and r["name"] != "plain"]
print(f"== the told pass rule, with a gap above .2: {len(rule)} worlds; x > .5: {sum(r['x'] > .5 for r in rule)}; x > .25: {sum(r['x'] > .25 for r in rule)}. Bootstrap the lives, not the worlds: these worlds were picked by hand, so the share means nothing beyond them.")
print("   no gap (told - max(base, 0) <= .2): " + ", ".join(r["name"] for r in rows if not r["gap"] > 0.2))
print("\n== doing no harm: bank minus base, lower 95% bound above -.1?")
for n in ("coin", "allfood", "never", "plain", "mirror", "rarefeast", "costly"):
    d = pdiff(res[n]["bank"], res[n]["base"])
    print(f"   {n:12s} {d[0]:+.3f} [{d[1]:+.3f},{d[2]:+.3f}] {'holds' if d[1] > -.1 else 'BREACHED'}")
print("\n== planted pairs, bank and base, A - B paired on seeds. Duplicates should tie; a lookalike need not")
for a, b, kind in (("swap11", "swap10", "near-duplicate"), ("swapmeals6", "swap10", "lookalike"), ("unreliable22", "unreliable", "near-duplicate"), ("every5th", "unreliable", "lookalike"), ("dim25", "weak", "duplicate in distribution"), ("mirror", "plain", "duplicate in distribution"), ("halfthrust_const", "halfthrust_gain", "the same lives")):
    for arm in ("base", "bank"):
        d = pdiff(res[a][arm], res[b][arm])
        print(f"   {a:18s} {b:16s} {kind:26s} {arm} {d[0]:+.3f} [{d[1]:+.3f},{d[2]:+.3f}]")
s_base = np.array([r["sg"][0] for r in rows])
s_bank = np.array([r["sg"][1] for r in rows])
s_d = np.array([r["sg"][2] for r in rows])
print(f"\n== sigma of a pair's efficiency: base median {np.median(s_base):.2f} range {s_base.min():.2f}-{s_base.max():.2f}; bank median {np.median(s_bank):.2f} range {s_bank.min():.2f}-{s_bank.max():.2f}; paired difference median {np.median(s_d):.2f} range {s_d.min():.2f}-{s_d.max():.2f}")
pe = (s_bank / 0.1) ** 2
print(f"   pairs for se .1 in efficiency, per world: median {np.median(pe):.0f}, 90% {np.percentile(pe, 90):.0f}, max {pe.max():.0f}")
px = np.array([r["pairs_x"] for r in rows if np.isfinite(r["pairs_x"]) and r["gap"] > 0.2])
print(f"   pairs for se .1 in x (gap above .2), per world: median {np.median(px):.0f}, 90% {np.percentile(px, 90):.0f}, max {px.max():.0f}")
wall = {}
for (n, label), (w, c) in cost.items():
    wall.setdefault(label, []).append((w, c))
lives = 100
for label, v in wall.items():
    w = np.array(v)
    print(f"   {label:9s} {w[:, 1].mean():.2f} s of a core a life (worst world {w[:, 1].max():.2f}), {lives / w[:, 0].mean():.1f} lives a second on 7 workers")
b = np.array(wall["bank"])
rate = lives / b[:, 0].mean()
for what, p in (("efficiency", np.median(pe)), ("x", np.median(px)), ("x, each world's own pairs summed", None)):
    n_pairs = p * 300 if p is not None else float(np.mean(px)) * 300
    print(f"   implied for 300 worlds, at se .1 in {what}: {n_pairs:.0f} pairs, {2 * n_pairs:.0f} lives of one circuit, {2 * n_pairs / rate / 3600:.1f} h at {rate:.1f} lives a second; base and told once each besides")
print(f"\ntotal {sum(w for w, _ in cost.values()):.0f} s of wall clock for {len(rows)} worlds")
