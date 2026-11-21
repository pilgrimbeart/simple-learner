"""Robot-action investigation (D178): the frozen metrics (work order, stage 4; R13), analyst accounting only.
Primary: (food - poison) per 10 s in the FIXED final third of the 100 s life (ticks 6667..9999), including time before
movement and zero-meal lives. Secondary (historical, D176): the same over the last third of the time after moving began.
Food and poison counts and rates separately; no finite ratio when poison is 0. Paired bootstrap over seeds, each seed's
red/blue pair together (seed-mean of its two lives), 4000 resamples, rng 178. All-food: food per 10 s, same seeds.
"""
import numpy as np

TICK = 0.01
N = 10000
FT = (2 * N / 3, N)


def life(r):
    """Per-life measures."""
    poison = r["poison"] if r["arm"] != "allfood" else None
    ft = [c for m, c in r["meals"] if FT[0] <= m < FT[1]]
    start = r["moving"] if r["moving"] is not None else N
    a = start + 2 * (N - start) / 3
    am = [c for m, c in r["meals"] if a <= m < N]
    t_am = (N - a) * TICK
    out = dict(food_ft=sum(c != poison for c in ft), poison_ft=sum(c == poison for c in ft),
               food_am=sum(c != poison for c in am), poison_am=sum(c == poison for c in am), t_am=t_am)
    T = (FT[1] - FT[0]) * TICK
    out["net_ft"] = 10 * (out["food_ft"] - out["poison_ft"]) / T
    out["food_rate_ft"] = 10 * out["food_ft"] / T
    out["poison_rate_ft"] = 10 * out["poison_ft"] / T
    out["net_am"] = 10 * (out["food_am"] - out["poison_am"]) / t_am if t_am > 0 else 0.0
    out["stranded"] = int(not r["meals"])
    if poison is not None:
        fk = r["sensor"]["blue" if poison == "red" else "red"]
        out["P_food_end"] = float(r["rows"][-1, 2 + fk])
        out["P_poison_end"] = float(r["rows"][-1, 3 - fk])
        pf, pp = r["rows"][:, 2 + fk], r["rows"][:, 3 - fk]
        strong = (pf >= 0.8) & (pp <= 0.2)
        out["strong_share"] = float(strong.mean())
        out["strong_ever"] = bool(strong.any())
        out["strong_end"] = bool(strong[-1])
        out["strong_lost"] = bool(strong.any() and not strong[-1])
        out["right_order_end"] = bool(pf[-1] > pp[-1])
        idx = np.flatnonzero(strong)
        out["acquired_s"] = float(idx[0] * TICK) if len(idx) else None
    else:
        out["P_food_end"] = out["P_poison_end"] = None
    if "pos" in r:
        d = np.diff(r["pos"], axis=0)
        out["path"] = float(np.sqrt((d ** 2).sum(1)).sum())
    else:
        out["path"] = float("nan")
    out["motor_rate"] = float(r["rows"][:, 6:8].sum() / 100.0)
    out["sensor_rate"] = float(r["rows"][:, 4:6].sum() / 100.0)
    out["meals_rate"] = 10 * len(r["meals"]) / 100.0
    return out


def per_seed(res, key):
    d = {}
    for r in res:
        d.setdefault(r["seed"], []).append(life(r)[key])
    return {s: float(np.mean(v)) for s, v in sorted(d.items())}


def boot(x, rng=None, n=4000):
    rng = rng or np.random.default_rng(178)
    x = np.asarray(x, float)
    i = rng.integers(0, len(x), (n, len(x)))
    m = x[i].mean(1)
    return [float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def paired(a, b, key="net_ft"):
    A, Bm = per_seed(a, key), per_seed(b, key)
    s = sorted(set(A) & set(Bm))
    return boot([A[k] - Bm[k] for k in s])


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, float(c - h), float(c + h)]


def summary(res):
    L = [life(r) for r in res]
    S = dict(lives=len(res))
    for key in ("net_ft", "food_rate_ft", "poison_rate_ft", "net_am", "motor_rate", "sensor_rate", "meals_rate", "path"):
        S[key] = boot(list(per_seed(res, key).values()))
    S["food_ft"] = int(sum(x["food_ft"] for x in L))
    S["poison_ft"] = int(sum(x["poison_ft"] for x in L))
    S["food_poison_ft"] = (S["food_ft"] / S["poison_ft"]) if S["poison_ft"] else f"{S['food_ft']}:0"
    S["food_am"], S["poison_am"] = int(sum(x["food_am"] for x in L)), int(sum(x["poison_am"] for x in L))
    k = sum(x["stranded"] for x in L)
    S["stranded"] = [k] + wilson(k, len(L))
    S["moved"] = int(sum(r["moving"] is not None for r in res))
    if L and L[0]["P_food_end"] is not None:
        S["right_order_end"] = int(sum(x["right_order_end"] for x in L))
        S["strong_end"] = int(sum(x["strong_end"] for x in L))
        S["strong_ever"] = int(sum(x["strong_ever"] for x in L))
        S["strong_lost"] = int(sum(x["strong_lost"] for x in L))
        S["strong_share_mean"] = float(np.mean([x["strong_share"] for x in L]))
        acq = sorted(x["acquired_s"] for x in L if x["acquired_s"] is not None)
        S["acquired_median_s"] = acq[len(acq) // 2] if acq else None
        S["P_food_end"] = boot([x["P_food_end"] for x in L])
        S["P_poison_end"] = boot([x["P_poison_end"] for x in L])
        S["P_abs_drift_median"] = float(np.median(np.abs(np.concatenate(
            [r["rows"][-1, 2:4] - r["rows"][0, 2:4] for r in res]))))
    return S


def job(S, limits=dict(food_rate=1.0, ratio=3.0, stranded=0.05)):
    """The existing job's limits with their 95% intervals (AGENTS.md, minimal search; spec.py), applied to the primary
    window: food rate >= 1 per 10 s (lower bound), food:poison >= 3 (pooled count; poison-zero counts as passing only if
    food > 0), stranding <= 5% (Wilson upper bound)."""
    fr = S["food_rate_ft"][1] >= limits["food_rate"]
    ratio = (S["food_ft"] >= 3 * S["poison_ft"]) and S["food_ft"] > 0
    st = S["stranded"][3] <= limits["stranded"]
    return dict(food_rate_ok=bool(fr), ratio_ok=bool(ratio), stranded_ok=bool(st), all=bool(fr and ratio and st))
