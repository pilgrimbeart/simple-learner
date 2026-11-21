"""Action grid analysis (work order sections 6, 8, 9). Analyst-side only; reads saved compact rows.

Conventions (D180's, frozen in PROTOCOL.md): final third [200/3, 100) s; net = (food - poison) * 10 / (100/3);
red and blue lives of a seed averaged first; seed is the resampling unit; 10,000 bootstrap resamples, RNG 182,
percentile intervals. Development intervals are exploratory (selection over 81 settings).
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

B = 10000
RNG = 182
Q95 = (2.5, 97.5)
Q_BONF = (100 * 0.008333333, 100 * 0.991666667)          # 98.333333% two-sided, Bonferroni for three
POISON_ARMS = ("informed", "neutral", "reversed", "no_explore", "no_sensory")
FOOD_ARMS = ("informed_allfood", "neutral_allfood")
ARMS = POISON_ARMS + FOOD_ARMS
FACTORS = dict(sensory_gain=(0.5, 1.0, 2.0), motor_tau_s=(0.0025, 0.005, 0.010),
               exploration_threshold_V=(0.15, 0.225, 0.30), oscillator_speed=(0.75, 1.0, 1.5))
BASE_LEVEL = dict(sensory_gain=1.0, motor_tau_s=0.005, exploration_threshold_V=0.15, oscillator_speed=1.0)


def validate(rows, expected):
    """Refuse duplicate rows and rows outside the frozen key set; return the expected keys missing."""
    seen = set()
    for r in rows:
        k = r["key"]
        if k in seen:
            raise ValueError(f"duplicate ledger row {k}")
        seen.add(k)
    extra = seen - set(expected)
    if extra:
        raise ValueError(f"rows outside the frozen job ledger: {sorted(extra)[:5]}")
    return sorted(set(expected) - seen)


def boot(x, q=Q95, n=B):
    x = np.asarray([v for v in x], float)
    if len(x) == 0:
        return [None, None, None]
    rng = np.random.default_rng(RNG)
    m = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return [float(x.mean()), float(np.percentile(m, q[0])), float(np.percentile(m, q[1]))]


def metric(r, key):
    if key in r["m"]:
        return r["m"][key]
    raise KeyError(key)


def per_seed(rows, f):
    d = {}
    for r in rows:
        d.setdefault(r["seed"], []).append(f(r))
    return {s: float(np.mean(v)) for s, v in sorted(d.items())}


def ok_rows(rows):
    return [r for r in rows if r.get("status") == "ok"]


def paired(a, b, f, q=Q95):
    A, Bm = per_seed(a, f), per_seed(b, f)
    if set(A) != set(Bm):
        return dict(ci=[None, None, None], n=0, note="seed sets differ (missing/invalid rows)")
    return dict(ci=boot([A[s] - Bm[s] for s in A], q), n=len(A))


M_KEYS = ("net", "food_rate_final", "poison_rate_final", "net_first", "net_second", "net_full", "food_rate_full",
          "poison_rate_full", "stranded", "never_moved")


def arm_summary(rows):
    S = dict(lives=len(rows), seeds=len({r["seed"] for r in rows}))
    for k in M_KEYS:
        S[k] = boot(list(per_seed(rows, lambda r, k=k: r["m"][k]).values()))
    S["food_final"] = int(sum(r["m"]["food_final"] for r in rows))
    S["poison_final"] = int(sum(r["m"]["poison_final"] for r in rows))
    S["stranded_lives"] = int(sum(r["m"]["stranded"] for r in rows))
    S["clip_lives"] = int(sum(r["clip_steps"] > 0 for r in rows))
    for k, f in dict(power_W=lambda r: r["power_W"], motor_events=lambda r: r["motor_events"],
                     body_firings=lambda r: r["firings"], motor_energy_J=lambda r: r["motor_energy_J"],
                     circuit_energy_J=lambda r: r["circuit_energy_J"],
                     high_frac=lambda r: (r["motors"]["M0"]["high_s"] + r["motors"]["M1"]["high_s"]) / 200.0,
                     unarmed_frac=lambda r: (r["motors"]["M0"]["unarmed_s"] + r["motors"]["M1"]["unarmed_s"]) / 200.0,
                     longest_unarmed_s=lambda r: max(r["motors"]["M0"]["longest_unarmed_s"],
                                                     r["motors"]["M1"]["longest_unarmed_s"]),
                     see_either_s=lambda r: r["body"]["full"]["see_either_s"],
                     path_m=lambda r: r["body"]["full"]["path_m"], angle_rad=lambda r: r["body"]["full"]["angle_rad"],
                     mean_vis=lambda r: r["body"]["full"]["mean_vis_red"] + r["body"]["full"]["mean_vis_blue"],
                     paired_fraction=lambda r: r["coordination"]["paired_fraction"],
                     near_opposite_fraction=lambda r: r["coordination"]["near_opposite_fraction"],
                     pulses=lambda r: r["pulses"]["n"],
                     fixed_unarmed_at_pulse=lambda r: (r["pulses"]["fixed"] or {}).get("unarmed_before"),
                     fixed_events_0_50=lambda r: (r["pulses"]["fixed"] or {}).get("events_0_50ms"),
                     other_events_0_50=lambda r: (r["pulses"]["other"] or {}).get("events_0_50ms"),
                     fixed_events_50_250=lambda r: (r["pulses"]["fixed"] or {}).get("events_50_250ms"),
                     P_drift_abs_max=lambda r: max(abs(x) for x in r["P_drift"])).items():
        vals = {}
        for r in rows:
            v = f(r)
            if v is not None:
                vals.setdefault(r["seed"], []).append(v)
        S[k] = boot([float(np.mean(v)) for v in vals.values()]) + [sum(len(v) for v in vals.values())]
    return S


def gated_edges(rows):
    """Mean gate factor / open fraction per gated edge and mean source events per edge (labelled proxies)."""
    out = {}
    for r in rows:
        for nm, d in r["edges"].items():
            o = out.setdefault(nm, dict(source=d["source"], gate=d["gate"], src_events=[], gate_mean=[], gate_open=[]))
            o["src_events"].append(d["source_events"])
            if d["gate"] is not None:
                o["gate_mean"].append(d["gate_mean"])
                o["gate_open"].append(d["gate_open_fraction"])
    return {nm: dict(source=o["source"], gate=o["gate"] or "ungated",
                     source_events_mean=float(np.mean(o["src_events"])),
                     gate_mean=None if not o["gate_mean"] else float(np.mean(o["gate_mean"])),
                     gate_open_fraction=None if not o["gate_open"] else float(np.mean(o["gate_open"])))
            for nm, o in out.items()}


def contrasts(by_arm, q=Q95):
    inf = by_arm["informed"]
    net = lambda r: r["m"]["net"]
    C = {f"informed_minus_{a}": paired(inf, by_arm[a], net, q) for a in ("neutral", "reversed", "no_explore", "no_sensory")}
    food = lambda r: r["m"]["food_rate_final"]
    for a in ("neutral", "reversed", "no_explore", "no_sensory"):        # descriptive: with taste withheld, an arm in
        C[f"food_informed_minus_{a}"] = paired(inf, by_arm[a], food, q)  # which P has no effect has net exactly 0
    C["allfood_informed_minus_neutral_food"] = paired(by_arm["informed_allfood"], by_arm["neutral_allfood"],
                                                       lambda r: r["m"]["food_rate_final"], q)
    return C


# ------------------------------------------------------------------------------------------- selection
def rank(table):
    """table: {config: dict(complete, informed_net, informed_food)}. Baseline excluded by the caller.
    Descending net, then descending food, then ascending ID; only complete finite rows."""
    elig = [(c, t) for c, t in table.items() if t["complete"] and math.isfinite(t["informed_net"])
            and math.isfinite(t["informed_food"])]
    return [c for c, _ in sorted(elig, key=lambda ct: (-ct[1]["informed_net"], -ct[1]["informed_food"], ct[0]))]


def ranking_fixture():
    t = dict(b=dict(complete=True, informed_net=0.2, informed_food=0.3),
             a=dict(complete=True, informed_net=0.2, informed_food=0.3),
             c=dict(complete=True, informed_net=0.2, informed_food=0.4),
             d=dict(complete=True, informed_net=0.3, informed_food=0.0),
             e=dict(complete=False, informed_net=9.0, informed_food=9.0),
             f=dict(complete=True, informed_net=float("nan"), informed_food=1.0))
    r = rank(t)
    return dict(ok=r == ["d", "c", "a", "b"], ranked=r)


def factor_tables(cfgs, dev, key="net"):
    """Marginal contrasts (level minus baseline level, same other factors, within seed, then bootstrap) and the six
    two-factor mean tables of informed `key` (seed means of red/blue lives)."""
    seedm = {c: per_seed(dev[c]["informed"], lambda r: r["m"][key]) for c in cfgs if dev[c]["complete"]}
    seeds = sorted(set.intersection(*[set(v) for v in seedm.values()])) if seedm else []
    by = {c["id"]: c for c in cfgs.values()}
    marg = {}
    for f, levels in FACTORS.items():
        for L in levels:
            if L == BASE_LEVEL[f]:
                continue
            diffs = []
            usable = True
            for s in seeds:
                a = [seedm[c][s] for c in seedm if by[c][f] == L]
                b = [seedm[c][s] for c in seedm if by[c][f] == BASE_LEVEL[f]]
                if len(a) != 27 or len(b) != 27:
                    usable = False
                diffs.append(np.mean(a) - np.mean(b))
            marg[f"{f}={L} minus {BASE_LEVEL[f]}"] = dict(ci=boot(diffs), n_seeds=len(seeds), balanced=usable)
    two = {}
    for f1, f2 in itertools.combinations(FACTORS, 2):
        tab = {}
        for l1 in FACTORS[f1]:
            for l2 in FACTORS[f2]:
                cs = [c for c in seedm if by[c][f1] == l1 and by[c][f2] == l2]
                tab[f"{l1}|{l2}"] = float(np.mean([np.mean(list(seedm[c].values())) for c in cs])) if cs else None
        two[f"{f1} x {f2}"] = tab
    return marg, two


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, float(c - h), float(c + h)]


def d180_job(rows):
    """D180 absolute gates (its analyse.job equations): food-rate lower >= 1/10 s; lower bound of food - 3 poison >= 0
    with food positive; seed-level Wilson on 'either life stranded' upper <= 0.05."""
    fr = boot(list(per_seed(rows, lambda r: r["m"]["food_rate_final"]).values()))
    lin = boot(list(per_seed(rows, lambda r: r["m"]["job_linear"]).values()))
    anys = {}
    for r in rows:
        anys[r["seed"]] = max(anys.get(r["seed"], 0), r["m"]["stranded"])
    w = wilson(sum(anys.values()), len(anys))
    food = sum(r["m"]["food_final"] for r in rows)
    g = dict(food_rate=fr, food_rate_ok=fr[1] is not None and fr[1] >= 1.0, job_linear=lin,
             ratio_ok=lin[1] is not None and lin[1] >= 0 and food > 0, stranding_seed_any=[sum(anys.values()), len(anys)] + w,
             stranding_ok=w[2] is not None and w[2] <= 0.05)
    g["all"] = bool(g["food_rate_ok"] and g["ratio_ok"] and g["stranding_ok"])
    return g


def jdump(p, d):
    Path(p).write_text(json.dumps(d, indent=1, default=float) + "\n")
