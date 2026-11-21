"""D178 stage 2 (R7): transfer, omission and operating-region diagnosis on identical saved inputs.
For each informed life (closed-loop capture of the given substrate), replay (a) the full input stream and (b) the same
stream with a fixed 20% of body pulses withheld (pulse index i % 5 == 2, fixed before scoring), in the same substrate,
same seed, so the same noise draws: their difference at the withheld pulses is the pulse's incremental (causal)
effect. Per sensor unit: incremental response within W = 10 ms; associated response; own firing; latency (1 ms);
response by time since its own previous spike (recovery bins). Per motor: incremental spikes within 20 ms of a
withheld pulse (sensor -> motor chain), own rate; left/right own-rate imbalance. Variation across units and lives.
python transfer.py <substrate> [bias=group:I] [arm]  -> lab/v/robot_action_20261120/transfer_<substrate>[...].json
"""
import json, os, pickle, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
OUT = ROOT / "lab/v/robot_action_20261120"
BIG = Path.home() / "nca-scratch-backup/robot_action_20261120"
W = 0.010
WM = 0.020
REC = (0.0, 0.01, 0.02, 0.05, 0.1, np.inf)


def times(spk, col, res=0.001):
    return np.repeat(np.flatnonzero(spk[:, col]), spk[spk[:, col] > 0, col]) * res


def tjob(job):
    tagname, i, substrate, bias = job
    import replay as R
    r = pickle.load(open(BIG / f"{tagname}.pkl", "rb"))[i]
    omit = {j for j in range(len(r["pulses"])) if j % 5 == 2}
    full, _ = R.replay(r, substrate, bias=bias)
    less, _ = R.replay(r, substrate, omit=omit, bias=bias)
    P = r["pulses"]
    out = dict(seed=r["seed"], poison=r["poison"], wiring=r["wiring"], units=[], motors=[])
    Sf = [times(full, k) for k in (0, 1)]
    Sl = [times(less, k) for k in (0, 1)]
    Mf = [times(full, 2 + k) for k in (0, 1)]
    Ml = [times(less, 2 + k) for k in (0, 1)]
    for k in (0, 1):
        idx = [j for j in range(len(P)) if int(P[j, 1]) == k]
        om = [j for j in idx if j in omit]
        inc = [float(((Sf[k] >= P[j, 0]) & (Sf[k] < P[j, 0] + W)).any()) - float(((Sl[k] >= P[j, 0]) & (Sl[k] < P[j, 0] + W)).any())
               for j in om]
        assoc, lat, rec = [], [], {b: [] for b in range(len(REC) - 1)}
        for j in idx:
            t = P[j, 0]
            after = Sf[k][(Sf[k] >= t) & (Sf[k] < t + W)]
            assoc.append(len(after) > 0)
            if len(after):
                lat.append(float(after[0] - t))
            prev = Sf[k][Sf[k] < t]
            gap = t - prev[-1] if len(prev) else np.inf
            b = int(np.searchsorted(REC, gap, side="right") - 1)
            rec[min(b, len(REC) - 2)].append(len(after) > 0)
        own = len(Sf[k]) - sum(assoc)
        mot = {}
        for m in (0, 1):
            mot[m] = [float(((Mf[m] >= P[j, 0]) & (Mf[m] < P[j, 0] + WM)).sum() - ((Ml[m] >= P[j, 0]) & (Ml[m] < P[j, 0] + WM)).sum())
                      for j in om]
        out["units"].append(dict(sensor=k, pulses=len(idx), omitted=len(om), inc_resp=float(np.mean(inc)) if inc else None,
                                 assoc_resp=float(np.mean(assoc)) if assoc else None, spikes=len(Sf[k]),
                                 own_rate=float(max(own, 0) / max(100.0 - len(idx) * W, 1e-9)),
                                 latency_ms=[1000 * float(np.percentile(lat, q)) for q in (10, 50, 90)] if lat else None,
                                 recovery={str(REC[b]): (float(np.mean(v)) if v else None, len(v)) for b, v in rec.items()},
                                 inc_motor={str(m): float(np.mean(mot[m])) if mot[m] else None for m in (0, 1)},
                                 side_motor=r["wiring"][k]["side_motor"]))
    allS = np.sort(np.concatenate(Sf))
    for m in (0, 1):
        if len(allS):
            i0 = np.searchsorted(allS, Mf[m], side="right") - 1
            linked = (i0 >= 0) & ((Mf[m] - allS[np.maximum(i0, 0)]) < W)
        else:
            linked = np.zeros(len(Mf[m]), bool)
        out["motors"].append(dict(motor=m, spikes=len(Mf[m]), own=int((~linked).sum()), own_rate=float((~linked).sum() / 100.0)))
    rates = [x["own_rate"] for x in out["motors"]]
    out["motor_imbalance"] = max(rates) / max(min(rates), 0.01)
    return out


def summarise(res):
    U = [u for r in res for u in r["units"] if u["pulses"] >= 5]
    q = lambda v: [float(np.percentile(v, p)) for p in (10, 25, 50, 75, 90)] if len(v) else None
    inc = [u["inc_resp"] for u in U if u["inc_resp"] is not None]
    S = dict(units=len(U), inc_resp_q=q(inc), inc_resp_mean=float(np.mean(inc)) if inc else None,
             assoc_resp_q=q([u["assoc_resp"] for u in U]), own_rate_q=q([u["own_rate"] for u in U]),
             latency_median_ms_q=q([u["latency_ms"][1] for u in U if u["latency_ms"]]))
    cls = dict(reliable=0, partial=0, dead=0, oscillating=0)
    for u in U:
        c = "oscillating" if u["own_rate"] > 1 else ("dead" if (u["inc_resp"] or 0) < 0.1 else
                                                    "reliable" if (u["inc_resp"] or 0) >= 0.9 else "partial")
        cls[c] += 1
    S["unit_classes"] = cls
    rec = {}
    for b in map(str, REC[:-1]):
        v = [u["recovery"][b] for u in U if u["recovery"][b][1] > 0]
        n = sum(x[1] for x in v)
        rec[b] = (sum(x[0] * x[1] for x in v) / n if n else None, n)
    S["response_by_time_since_own_spike_s"] = rec
    side = [u["inc_motor"][str(u["side_motor"])] for u in U if u["inc_motor"][str(u["side_motor"])] is not None]
    S["incremental_side_motor_spikes_per_pulse_q"] = q(side)
    S["motor_own_rate_q"] = q([m["own_rate"] for r in res for m in r["motors"]])
    S["motor_imbalance_q"] = q([r["motor_imbalance"] for r in res])
    S["lives_with_a_silent_motor"] = int(sum(min(m["own_rate"] for m in r["motors"]) < 0.05 for r in res))
    S["lives_both_sensors_dead_or_osc"] = int(sum(all(((u["inc_resp"] or 0) < 0.1 or u["own_rate"] > 1) for u in r["units"]) for r in res))
    return S


def main():
    sub = sys.argv[1]
    bias = None
    arm = "informed"
    for x in sys.argv[2:]:
        if x.startswith("bias="):
            g, I = x[5:].split(":")
            bias = (g, float(I))
        else:
            arm = x
    tagname = f"{arm}_{sub}_s0-31"
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(tagname, i, sub, bias) for i in range(64)]
    with ProcessPoolExecutor(7, mp_context=multiprocessing.get_context("spawn")) as pool:
        res = list(pool.map(tjob, jobs))
    suffix = "" if bias is None else f"_bias-{bias[0]}{bias[1]:.3g}"
    pickle.dump(res, open(BIG / f"transfer_{arm}_{sub}{suffix}.pkl", "wb"))
    S = summarise(res)
    json.dump(dict(summary=S, lives=res), open(OUT / f"transfer_{arm}_{sub}{suffix}.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    main()
