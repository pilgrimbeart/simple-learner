"""D180 frozen metrics and analysis (work order section 8). Physical time in seconds. Analyst-side only.

Per life (from its compact ledger row): primary reward (food - poison) * 10 / (100/3) in the FIXED window
[200/3, 100) s (a meal at tick t happens in [t*TICK, (t+1)*TICK); in the window iff t*TICK >= 200/3), including
pre-movement time and zero-meal lives; food and poison counts and rates per window (first third, second third,
final third, full life); stranded = no meal in the whole life; never-moved separately. Acquisition of the bit
(P_food >= 0.8 V_TYP and P_poison <= 0.2 V_TYP) and the weaker right order (P_food > P_poison), from per-tick P.

Across lives: red/blue lives of a seed averaged first, then 10,000 bootstrap resamples of seeds, analysis RNG 180,
95% percentile intervals; contrasts paired per seed before resampling. All-food: one life per seed.
"""
from __future__ import annotations

import math

import numpy as np

TICK = 0.01
LIFE = 100.0
W0, W1 = 200 / 3, 100.0
WINDOWS = dict(first=(0.0, 100 / 3), second=(100 / 3, 200 / 3), final=(W0, W1), full=(0.0, LIFE))
B = 10000
V_TYP = 0.3
HI, LO = 0.8 * V_TYP, 0.2 * V_TYP


def counts(meals, poison, a, b):
    """meals: list of (tick, colour). Food and poison in [a, b) seconds."""
    inside = [c for t, c in meals if a <= t * TICK < b]
    return sum(c != poison for c in inside), sum(c == poison for c in inside)


def acquisition(pf, pp):
    """pf, pp: per-tick P of the food and poison sensors (end of each tick). Entry/exit accounting of the bit."""
    pf, pp = np.asarray(pf, float), np.asarray(pp, float)
    ok = (pf >= HI) & (pp <= LO)
    d = np.diff(ok.astype(int))
    entries = np.flatnonzero(d == 1) + 1
    exits = np.flatnonzero(d == -1) + 1
    first = (0.0 if ok[0] else (float((entries[0] + 1) * TICK) if len(entries) else None)) if len(ok) else None
    order = pf > pp
    out = dict(acq_first_s=first, acq_fraction=float(ok.mean()) if len(ok) else 0.0,
               acq_entries=int(len(entries) + (1 if len(ok) and ok[0] else 0)), acq_exits=int(len(exits)),
               acq_reentries=int(max(len(entries) + (1 if len(ok) and ok[0] else 0) - 1, 0)),
               acq_final=bool(ok[-1]) if len(ok) else False,
               order_fraction=float(order.mean()) if len(ok) else 0.0, order_final=bool(order[-1]) if len(ok) else False,
               order_first_s=(float((np.argmax(order) + 1) * TICK) if order.any() else None))
    both = np.concatenate([pf, pp])
    out.update(P_min=float(both.min()), P_max=float(both.max()),
               P_outside_s=float(((pf < 0) | (pf > V_TYP)).sum() * TICK + ((pp < 0) | (pp > V_TYP)).sum() * TICK))
    return out


def life_metrics(r):
    """r: a ledger row (dict) with meals, poison, moving, P traces etc. Returns per-life measures."""
    poison = r["poison"]
    out = {}
    for w, (a, b) in WINDOWS.items():
        f, p = counts(r["meals"], poison, a, b)
        T = b - a
        out[f"food_{w}"], out[f"poison_{w}"] = f, p
        out[f"food_rate_{w}"], out[f"poison_rate_{w}"] = 10 * f / T, 10 * p / T
        out[f"net_{w}"] = 10 * (f - p) / T
    out["net"] = out["net_final"]
    out["job_linear"] = out["food_rate_final"] - 3 * out["poison_rate_final"]
    out["stranded"] = int(len(r["meals"]) == 0)
    out["never_moved"] = int(r["moving"] is None)
    if poison is not None and r.get("Pf") is not None:
        out.update(acquisition(r["Pf"], r["Pp"]))
    return out


def per_seed(rows, key):
    d = {}
    for r in rows:
        d.setdefault(r["seed"], []).append(r["m"][key])
    return {s: float(np.mean(v)) for s, v in sorted(d.items())}


def boot(x, n=B):
    x = np.asarray(x, float)
    if len(x) == 0:
        return [None, None, None]
    rng = np.random.default_rng(180)
    i = rng.integers(0, len(x), (n, len(x)))
    m = x[i].mean(1)
    return [float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def paired(a, b, key="net"):
    """Seed-paired contrast a - b of a per-life measure (seed means first)."""
    A, Bm = per_seed(a, key), per_seed(b, key)
    s = sorted(set(A) & set(Bm))
    assert set(A) == set(Bm), "contrast arms must have the same seeds"
    return boot([A[k] - Bm[k] for k in s])


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, float(c - h), float(c + h)]


def stranding(rows):
    """Conservative seed-level gate: Wilson on 'either life of the seed stranded'; life fraction and seed-cluster
    bootstrap descriptive."""
    seeds = per_seed(rows, "stranded")
    any_ = {}
    for r in rows:
        any_[r["seed"]] = max(any_.get(r["seed"], 0), r["m"]["stranded"])
    k = sum(any_.values())
    lives = [r["m"]["stranded"] for r in rows]
    return dict(seed_any=[k, len(any_)] + wilson(k, len(any_)), life_fraction=[int(sum(lives)), len(lives)],
                life_rate_cluster=boot(list(seeds.values())))


def summary(rows):
    S = dict(lives=len(rows), seeds=len({r["seed"] for r in rows}))
    for key in ("net", "food_rate_final", "poison_rate_final", "job_linear", "net_first", "net_second", "net_full",
                "food_rate_full", "poison_rate_full"):
        S[key] = boot(list(per_seed(rows, key).values()))
    S["food_final"] = int(sum(r["m"]["food_final"] for r in rows))
    S["poison_final"] = int(sum(r["m"]["poison_final"] for r in rows))
    S["food_poison_pooled"] = (S["food_final"] / S["poison_final"]) if S["poison_final"] else f"{S['food_final']}:0"
    S["stranding"] = stranding(rows)
    S["never_moved"] = int(sum(r["m"]["never_moved"] for r in rows))
    S["no_meal_fraction"] = S["stranding"]["life_fraction"][0] / max(len(rows), 1)
    if rows and "acq_fraction" in rows[0]["m"]:
        M = [r["m"] for r in rows]
        firsts = sorted(m["acq_first_s"] for m in M if m["acq_first_s"] is not None)
        S["acquisition"] = dict(
            ever=sum(m["acq_first_s"] is not None for m in M), final=sum(m["acq_final"] for m in M),
            first_s_median=firsts[len(firsts) // 2] if firsts else None, first_missing=len(M) - len(firsts),
            fraction_mean=float(np.mean([m["acq_fraction"] for m in M])),
            exits=int(sum(m["acq_exits"] for m in M)), reentries=int(sum(m["acq_reentries"] for m in M)),
            order_final=sum(m["order_final"] for m in M), order_fraction_mean=float(np.mean([m["order_fraction"] for m in M])),
            P_min=float(min(m["P_min"] for m in M)), P_max=float(max(m["P_max"] for m in M)),
            P_outside_s_mean=float(np.mean([m["P_outside_s"] for m in M])))
    for key in ("power_W", "motor_events", "clip_steps", "write_charge_abs_C"):
        if rows and key in rows[0]:
            S[key] = boot(list({s: v for s, v in _seedmean(rows, key).items()}.values()))
    return S


def _seedmean(rows, key):
    d = {}
    for r in rows:
        d.setdefault(r["seed"], []).append(r[key])
    return {s: float(np.mean(v)) for s, v in sorted(d.items())}


def job(S):
    """Absolute job gates: food-rate lower >= 1; lower bound of food - 3 poison >= 0 with food positive; seed-level
    Wilson stranding upper <= 0.05."""
    fr = S["food_rate_final"][1] is not None and S["food_rate_final"][1] >= 1.0
    lin = S["job_linear"][1] is not None and S["job_linear"][1] >= 0 and S["food_final"] > 0
    st = S["stranding"]["seed_any"][4] is not None and S["stranding"]["seed_any"][4] <= 0.05
    return dict(food_rate=bool(fr), ratio_linear=bool(lin), stranding=bool(st), all=bool(fr and lin and st))


def validate_ledger(rows, expected):
    """expected: list of job keys (lives.key). Refuses duplicate rows; returns the keys missing (incomplete rows)."""
    from lives import key
    seen = {}
    for r in rows:
        k = key(r)
        if k in seen:
            raise ValueError(f"duplicate ledger row {k}")
        seen[k] = r
    unexpected = sorted(set(seen) - set(expected))
    if unexpected:
        raise ValueError(f"rows outside the frozen job ledger: {unexpected[:5]}")
    return sorted(set(expected) - set(seen))


GATE_EPS = 0.01                 # a writer counts as eligible when its gate E/V_TYP exceeds the memory driver's 1% deadband


def evidence(learned, withheld):
    """R6 evidence accounting, computed BEFORE any reward contrast. Observer labels (which sensor is food) are used
    only here, by the analyst. learned: taste delivered; withheld: same lives' neutral arm without taste."""
    def acc(rows):
        per_life, after, Ef, Ep, both, one, none_, dPc, dPw, n_t = [], [], [], [], 0, 0, 0, [], [], 0
        for r in rows:
            meals = r["E_at_meal"]
            per_life.append(len(meals) / LIFE)
            if r["moving"] is not None:
                after.append(len(meals) / max(LIFE - r["moving"] * TICK, 1e-9))
            fk = r["food_sensor"]
            for t, c, e0, e1, d0, d1 in meals:
                E = (e0, e1)
                ef, ep = E[fk], E[1 - fk]
                Ef.append(ef); Ep.append(ep); n_t += 1
                g = [x / V_TYP > GATE_EPS for x in E]
                both += all(g); one += (sum(g) == 1); none_ += (not any(g))
                sign = -1 if c == r["poison"] else 1
                dP = (d0, d1)
                # correct credit: food raises P_food, poison lowers P_poison; anything else is incorrect credit
                if sign > 0:
                    dPc.append(dP[fk]); dPw.append(dP[1 - fk])
                else:
                    dPc.append(-dP[1 - fk]); dPw.append(-dP[fk])
        q = lambda x: [float(np.percentile(x, p)) for p in (10, 50, 90)] if len(x) else None
        return dict(tastes_per_s_fixed_life=boot(per_life), tastes_per_s_after_moving=boot(after),
                    tastes=n_t, E_food_sensor_at_taste_q10_50_90=q(Ef), E_poison_sensor_at_taste_q10_50_90=q(Ep),
                    eligible_both=both, eligible_one=one, eligible_none=none_,
                    correct_dP_per_taste_q10_50_90=q(dPc), other_sensor_signed_dP_per_taste_q10_50_90=q(dPw),
                    correct_dP_sum_mean_per_life=float(np.sum(dPc) / max(len(rows), 1)),
                    other_dP_sum_mean_per_life=float(np.sum(dPw) / max(len(rows), 1)))
    out = dict(learned=acc(learned), taste_withheld=acc(withheld))
    # substrate noise of a write: silicon shot noise of the writer current over its ~12 ms, sigma = sqrt(q I tau)/C
    I, tau, C = 3e-10, 0.012, 5e-12
    out["writer_shot_sigma_V_full_gate"] = float(math.sqrt(1.602e-19 * I * tau) / C)
    out["nominal_write_full_gate_V"] = float(I * tau / C)
    out["needed_from_neutral_V"] = dict(food_up=0.8 * V_TYP - V_TYP / 2, poison_down=V_TYP / 2 - 0.2 * V_TYP)
    out["bits"] = ("Unknown: one binary colour valence, balanced prior (1 bit). Evidence: this arm's own causal "
                   "sensor/taste history. The informed arm is told the bit (an opportunity reference, not a bound). "
                   "The optimal same-senses history model is unknown; no per-taste bit sum is claimed.")
    out["explorers"] = "two independent exploratory sources (one oscillator per motor); credit overlap measured from E"
    return out
