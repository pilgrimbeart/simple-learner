"""SPICE closed-loop lives against the simulator's on the same seeds: the league's measures, and paired differences
(SPICE - simulator, bootstrap over seeds, each seed's pair of lives together)."""
import json, sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal import spec as S
from minimal.spice_life import lived

d = json.load(open("/home/pilgrim/git/simple-learner/minimal/results/spice_life_HR_31p_pol_1.8V.json"))
key = lambda r: (r["seed"], r["poison"] != "red")
seeds = sorted({r["seed"] for r in d["spice"]} & {r["seed"] for r in d["sim"]})
sp = [lived(r, 100.0) for r in sorted(d["spice"], key=key) if r["seed"] in seeds]
si = [lived(r, 100.0) for r in sorted(d["sim"], key=key) if r["seed"] in seeds]
sp_simpower = [lived({**r, "power": q["power"]}, 100.0) for r, q in
               zip(sorted([r for r in d["spice"] if r["seed"] in seeds], key=key),
                   sorted([r for r in d["sim"] if r["seed"] in seeds], key=key))]
print(f"{len(seeds)} seeds, {len(sp)} lives each")
for name, L in (("simulator", si), ("SPICE", sp), ("SPICE, model's power", sp_simpower)):
    v = S.summary(L)
    ci = v["ci"]
    print(f"{name:22s} food {v['food']:.2f} {np.round(ci['food'], 2)}, poison {v['poison']:.2f}, gain {v['gain']:.2f} "
          f"{np.round(ci['gain'], 2)}, eff {v['efficiency']:.2f} {np.round(ci['efficiency'], 2)}, last f:p {v['last']:.1f}, "
          f"stranded {v['stranded']:.1%} {np.round(ci['stranded'], 3)}, firings {v['firings']:.0f}/10s, "
          f"power {v['power'] * 1e9:.0f} nW, job {v['job']}")
idx = S.boot_index(len(seeds))
a, b = S.resampled(S.per_pair(sp_simpower), idx), S.resampled(S.per_pair(si), idx)
a0 = S.resampled(S.per_pair(sp_simpower), np.arange(len(seeds))[None, :])
b0 = S.resampled(S.per_pair(si), np.arange(len(seeds))[None, :])
print("paired, SPICE (model's power) - simulator:")
for k in ("food", "gain", "efficiency", "stranded"):
    diff = a[k] - b[k]
    print(f"  {k:10s} {a0[k][0] - b0[k][0]:+.3f} [{np.nanpercentile(diff, 2.5):+.3f}, {np.nanpercentile(diff, 97.5):+.3f}]")
pw = np.array([r["power"] for r in d["spice"]])
print(f"SPICE supply power: {pw.mean() * 1e6:.2f} uW (range {pw.min() * 1e6:.2f}..{pw.max() * 1e6:.2f}); simulator "
      f"{np.mean([r['power'] for r in d['sim']]) * 1e9:.1f} nW; wall per SPICE life {np.mean([r['wall'] for r in d['spice']]):.0f} s")
