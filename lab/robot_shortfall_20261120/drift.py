"""D176: what moves the designed circuit's knob P between tastes? On the frozen arm (no taste ever reaches the
brain), for each knob while unclamped (0.02 < P < 0.98): regress the change per tick on the eligibility E that gates
its writers (directed drift) and compare the steady part with the random part (diffusion). Also the final knobs'
distribution in the informed arm (pinned at the rails or spread). Analyst accounting only.
python drift.py [arm-suffix]  ->  lab/v/robot_shortfall_20261120/drift<suffix>.json
"""
import json, pickle, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BIG = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"
OUT = ROOT / "lab/v/robot_shortfall_20261120"


def main():
    suf = sys.argv[1] if len(sys.argv) > 1 else ""
    res = pickle.load(open(BIG / f"frozen{suf}_64x100s.pkl", "rb"))
    per_knob = []
    for r in res:
        if r["poison"] != "red":            # the blue life is the same brain and world but for which taste: frozen
            continue                        # lives get no taste, so a seed's two lives are identical; count once
        rows = r["rows"].astype(float)
        for k in (0, 1):
            P, E = rows[:, 2 + k], rows[:, k]
            dP = np.diff(P)
            free = (P[:-1] > .02) & (P[:-1] < .98) & (P[1:] > .02) & (P[1:] < .98)
            if free.sum() < 500:
                per_knob.append(dict(seed=r["seed"], k=k, free_ticks=int(free.sum()), P0=P[0], P1=P[-1]))
                continue
            x, y = E[:-1][free], dP[free]
            slope = float(np.sum(x * y) / np.sum(x * x))            # dP per tick per volt of E, through 0
            resid = y - slope * x
            n = len(y)
            directed = abs(slope * x.sum())                          # the steady part over the free time
            random = float(np.sqrt(np.sum(resid ** 2)))              # the random part's typical total (sqrt n sigma)
            halves = [float(np.sum(y[: n // 2])), float(np.sum(y[n // 2:]))]
            per_knob.append(dict(seed=r["seed"], k=k, free_ticks=int(n), P0=P[0], P1=P[-1],
                                 rate_per_s_per_V=slope * 100, directed=directed, random=random,
                                 half_changes=halves, E_mean=float(x.mean())))
    ok = [d for d in per_knob if "directed" in d]
    inf = pickle.load(open(BIG / f"informed{suf}_64x100s.pkl", "rb"))
    fin = np.array([r["rows"][-1, 2:4] for r in inf]).ravel()
    S = dict(knobs=len(per_knob), knobs_free=len(ok),
             pinned_at_rail_before_500_free_ticks=len(per_knob) - len(ok),
             directed_over_random_median=float(np.median([d["directed"] / d["random"] for d in ok])),
             directed_gt_random=int(sum(d["directed"] > d["random"] for d in ok)),
             halves_same_sign=int(sum(np.sign(d["half_changes"][0]) == np.sign(d["half_changes"][1]) for d in ok)),
             rate_per_s_per_V_abs_median=float(np.median([abs(d["rate_per_s_per_V"]) for d in ok])),
             rate_up=int(sum(d["rate_per_s_per_V"] > 0 for d in ok)),
             E_mean_median=float(np.median([d["E_mean"] for d in ok])),
             informed_final_P_at_rail=int(((fin < .02) | (fin > .98)).sum()), informed_final_P_n=len(fin),
             informed_final_P_quartiles=np.percentile(fin, [25, 50, 75]).tolist(), per_knob=per_knob)
    json.dump(S, open(OUT / f"drift{suf}.json", "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in S.items() if k != "per_knob"}, indent=1))


if __name__ == "__main__":
    main()
