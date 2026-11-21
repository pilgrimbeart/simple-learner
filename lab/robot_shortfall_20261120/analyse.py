"""D176 analysis of trace.py's captures: per arm, last-third food:poison and net food per 10 s (paired bootstrap over
seeds), activity, stranded lives; credit at taste (eligibility, last sensor spike, last body pulse); the knob's write at
each taste and its drift between tastes; final knobs; the 1 - H2(a) per-taste bound. Analyst accounting only.
python analyse.py <seconds> [tag-suffix] [arm-suffix]   (arm-suffix -mem: the memory-knob arms)  ->  lab/v/robot_shortfall_20261120/summary_<seconds>s<suffix>.json
"""
import json, pickle, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BIG = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"
OUT = ROOT / "lab/v/robot_shortfall_20261120"
TICK = 0.01
ABSENT = 0.05
ARMS = ("learn", "frozen", "informed", "allfood", "held")


def thirds(r):
    n = int(round(r["seconds"] / TICK))
    start = r["moving"] if r["moving"] is not None else n
    a, b = start + 2 * (n - start) / 3, n
    part = [c for m, c in r["meals"] if a <= m < b]
    if r["arm"] == "allfood":
        return 0, len(part), (b - a) * TICK
    return sum(c == r["poison"] for c in part), sum(c != r["poison"] for c in part), (b - a) * TICK


def h2(a):
    a = min(max(a, 1e-12), 1 - 1e-12)
    return -a * np.log2(a) - (1 - a) * np.log2(1 - a)


def credit(r):
    """Per meal: which sensor ate (privileged label), E at taste, last sensor spike, last body pulse; P change."""
    rows, pulses = r["rows"], r["pulses"]
    out = []
    for m, c in r["meals"]:
        k = r["sensor"][c]
        if m >= len(rows) - 3:
            continue
        E = rows[m, :2]
        if max(E) < ABSENT or E[0] == E[1]:
            e_lab = None
        else:
            e_lab = int(np.argmax(E)) == k
        sp = [np.flatnonzero(rows[: m + 1, 4 + s]) for s in (0, 1)]
        last = [x[-1] if len(x) else -1 for x in sp]
        s_lab = None if max(last) < 0 or last[0] == last[1] else int(np.argmax(last)) == k
        before = pulses[pulses[:, 0] <= (m + 1) * TICK] if len(pulses) else pulses
        p_lab = None if len(before) == 0 else int(before[-1, 1]) == k
        good = c != r["poison"]
        dP = rows[m + 3, 2:4] - rows[m, 2:4]
        out.append(dict(k=k, good=good, e=e_lab, s=s_lab, p=p_lab, E=E.tolist(), dPk=float(dP[k]),
                        dPo=float(dP[1 - k])))
    return out


def boot(x, rng, n=4000):
    x = np.asarray(x, float)
    i = rng.integers(0, len(x), (n, len(x)))
    m = x[i].mean(1)
    return [float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main():
    seconds = int(sys.argv[1])
    suf = sys.argv[2] if len(sys.argv) > 2 else ""
    asuf = sys.argv[3] if len(sys.argv) > 3 else ""
    rng = np.random.default_rng(176)
    data, S = {}, {}
    for arm in ARMS:
        f = BIG / f"{arm}{asuf}_64x{seconds}s{suf}.pkl"
        if f.exists():
            data[arm] = pickle.load(open(f, "rb"))
    net = {}
    for arm, res in data.items():
        th = [thirds(r) for r in res]
        P, F, T = (np.array(v, float) for v in zip(*th))
        per_seed = {}
        for r, (p, f, t) in zip(res, th):
            per_seed.setdefault(r["seed"], []).append(10 * (f - p) / max(t, 1e-9))
        net[arm] = {s: np.mean(v) for s, v in per_seed.items()}
        stranded = sum(1 for r in res if not r["meals"])
        S[arm] = dict(food_poison_last_third=float(F.sum() / max(P.sum(), 1)), food=int(F.sum()), poison=int(P.sum()),
                      net_per_10s=boot(list(net[arm].values()), rng),
                      meals_per_10s_last_third=float(10 * (F + P).sum() / T.sum()), stranded=stranded,
                      lives=len(res), lives_ratio_ge3=int(sum(f >= 3 * p and f > 0 for p, f in zip(P, F))))
        rows = np.stack([r["rows"] for r in res])
        S[arm]["sensor_spikes_per_10s"] = float(rows[:, :, 4:6].sum(1).mean() / seconds * 10)
        S[arm]["motor_spikes_per_10s"] = float(rows[:, :, 6:8].sum(1).mean() / seconds * 10)
        S[arm]["pulses_per_10s"] = float(np.mean([len(r["pulses"]) for r in res]) / seconds * 10)
        S[arm]["E_mean"] = float(rows[:, :, :2].mean())
        if arm == "allfood":
            continue
        food_k = [r["sensor"]["blue" if r["poison"] == "red" else "red"] for r in res]
        pf = np.array([r["rows"][-1, 2 + k] for r, k in zip(res, food_k)])
        pp = np.array([r["rows"][-1, 3 - k] for r, k in zip(res, food_k)])
        S[arm]["final_P_food"], S[arm]["final_P_poison"] = boot(pf, rng), boot(pp, rng)
        S[arm]["final_P_right_order"] = int((pf > pp).sum())
        S[arm]["final_P_learned_0.2"] = int(((pf >= .8) & (pp <= .2)).sum())
        start = np.array([r["rows"][0, 2:4] for r in res])
        end = np.array([r["rows"][-1, 2:4] for r in res])
        S[arm]["P_abs_change_over_life_median"] = float(np.median(np.abs(end - start)))
        S[arm]["P_abs_change_gt_0.3"] = int((np.abs(end - start) > 0.3).sum())
        if arm == "learn":
            cr = [x for r in res for x in credit(r)]
            for lab in ("e", "s", "p"):
                v = [x[lab] for x in cr]
                known = [x for x in v if x is not None]
                a = float(np.mean(known)) if known else None
                S[arm][f"credit_{lab}"] = dict(tastes=len(v), absent=sum(x is None for x in v), right=sum(known),
                                               share_right=a, bits_per_taste_bound=None if a is None else 1 - h2(a))
            e_share = [x["E"][x["k"]] / max(sum(x["E"]), 1e-9) for x in cr]
            S[arm]["competing_trace"] = dict(
                other_E_at_least_half_eaten=float(np.mean([x["E"][1 - x["k"]] >= .5 * x["E"][x["k"]] for x in cr])),
                other_E_above_eaten=float(np.mean([x["E"][1 - x["k"]] > x["E"][x["k"]] for x in cr])),
                other_write_over_eaten_write_median=float(np.median([x["dPo"] / x["dPk"] for x in cr if abs(x["dPk"]) > 1e-3])))
            S[arm]["E_eaten_share_of_sum_mean"] = float(np.mean(e_share))
            right = [np.sign(x["dPk"]) == (1 if x["good"] else -1) for x in cr if abs(x["dPk"]) > 1e-3]
            S[arm]["write_sign_right"] = dict(n=len(right), share=float(np.mean(right)) if right else None)
            S[arm]["write_mean_dP_eaten"] = dict(food=float(np.mean([x["dPk"] for x in cr if x["good"]])),
                                                poison=float(np.mean([x["dPk"] for x in cr if not x["good"]])))
            S[arm]["write_mean_dP_other"] = dict(food=float(np.mean([x["dPo"] for x in cr if x["good"]])),
                                                poison=float(np.mean([x["dPo"] for x in cr if not x["good"]])))
            # drift between tastes: total P change minus the change in the 3 ticks after each taste
            drift = []
            for r in res:
                for kk in (0, 1):
                    p = r["rows"][:, 2 + kk].astype(float)
                    jump = sum(p[m + 3] - p[m] for m, _ in r["meals"] if m < len(p) - 3)
                    drift.append(float(p[-1] - p[0] - jump))
            S[arm]["P_drift_between_tastes_abs_median"] = float(np.median(np.abs(drift)))
    for a, b in (("informed", "frozen"), ("learn", "frozen"), ("informed", "learn"), ("held", "frozen"), ("held", "learn")):
        if a in net and b in net:
            d = [net[a][s] - net[b][s] for s in net[a]]
            S[f"net_{a}_minus_{b}"] = boot(d, rng)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(S, open(OUT / f"summary_{seconds}s{suf}{asuf}.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main()
