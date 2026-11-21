"""D178 stage 1 (R4, R5, R6): substrate comparison on the same development lives, all-food controls, identical-input
replay and the evidence/noise budget, then the predeclared branch.
Windows (frozen from bench.json before scoring, D178 addendum 1): a sensor spike is pulse-locked if it starts within
W = 10 ms after one of that sensor's pulses; a motor spike is sensor-linked if within W after a spike of either sensor
(both sensors drive both motors). Own (quiet) firing = spikes not so linked, per second of unlinked time.
python stage1.py -> lab/v/robot_action_20261120/stage1.json
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
ARMS = ("learn", "frozen", "informed", "allfood")
SUBS = ("biology", "silicon")


def load(arm, sub, s0=0, s1=31, extra=""):
    return pickle.load(open(BIG / f"{arm}_{sub}_s{s0}-{s1}{extra}.pkl", "rb"))


def locked(times, refs, w=W):
    """For each time, whether a ref lies in (time - w, time]."""
    refs = np.sort(np.asarray(refs, float))
    if len(refs) == 0 or len(times) == 0:
        return np.zeros(len(times), bool)
    i = np.searchsorted(refs, times, side="right") - 1
    ok = i >= 0
    out = np.zeros(len(times), bool)
    out[ok] = (times[ok] - refs[i[ok]]) < w
    return out


def covered(refs, w=W, T=100.0):
    refs = np.sort(np.asarray(refs, float))
    if len(refs) == 0:
        return 0.0
    ends = np.minimum(refs + w, np.append(refs[1:], np.inf))
    return float(np.minimum(ends, T).sum() - refs.sum())


def response(spk, pulses, res=0.001, T=100.0):
    """Response measures from 1 ms spike arrays (columns S0, S1, M0, M1)."""
    t = lambda col: np.repeat(np.flatnonzero(spk[:, col]), spk[spk[:, col] > 0, col]) * res
    S = [t(0), t(1)]
    M = [t(2), t(3)]
    out = {}
    for k in (0, 1):
        pk = pulses[pulses[:, 1] == k, 0] if len(pulses) else np.zeros(0)
        hit = [bool(((S[k] >= p) & (S[k] < p + W)).any()) for p in pk]
        lk = locked(S[k], pk)
        out[f"S{k}"] = dict(pulses=len(pk), resp=float(np.mean(hit)) if len(pk) else None, spikes=len(S[k]),
                            locked=int(lk.sum()), own_rate=float((~lk).sum() / max(T - covered(pk), 1e-9)))
    allS = np.concatenate(S)
    for k in (0, 1):
        lk = locked(M[k], allS)
        out[f"M{k}"] = dict(spikes=len(M[k]), linked=int(lk.sum()),
                            own_rate=float((~lk).sum() / max(T - covered(allS), 1e-9)))
    locked_all = out["S0"]["locked"] + out["S1"]["locked"]
    spikes_all = out["S0"]["spikes"] + out["S1"]["spikes"]
    out["sensor_spike_purity"] = locked_all / spikes_all if spikes_all else None
    out["pulses_per_s"] = len(pulses) / T
    out["motor_own_rates"] = [out["M0"]["own_rate"], out["M1"]["own_rate"]]
    return out


def rjob(job):
    tagname, i, target = job
    import replay as R
    r = pickle.load(open(BIG / f"{tagname}.pkl", "rb"))[i]
    spk, P = R.replay(r, target)
    same = None
    if target == r["substrate"]:
        same = bool(np.array_equal(R.per_tick(spk), r["rows"][:, 4:8].astype(np.int64)))
    return dict(tag=tagname, i=i, seed=r["seed"], poison=r["poison"], source=r["substrate"], target=target,
                identical_to_closed_loop=same, resp=response(spk, r["pulses"]))


def credit(r):
    """D176's credit at taste (privileged label: the eaten colour's sensor)."""
    rows = r["rows"]
    out = []
    for m, c in r["meals"]:
        k = r["sensor"][c]
        if m >= len(rows) - 3:
            continue
        E = rows[m, :2]
        out.append(None if (max(E) < 0.05 or E[0] == E[1]) else int(np.argmax(E)) == k)
    return out


def main():
    import metrics as M
    rng = np.random.default_rng(178)
    data = {(a, s): load(a, s) for a in ARMS for s in SUBS}
    out = dict(summary={}, contrasts={}, job={})
    for (a, s), res in data.items():
        out["summary"][f"{a}_{s}"] = M.summary(res)
        out["job"][f"{a}_{s}"] = M.job(out["summary"][f"{a}_{s}"])
    C = out["contrasts"]
    for s in SUBS:
        for a, b in (("learn", "frozen"), ("informed", "frozen"), ("informed", "learn")):
            for key in ("net_ft", "food_rate_ft", "poison_rate_ft", "net_am", "path", "motor_rate"):
                C[f"{a}-{b}_{s}_{key}"] = M.paired(data[(a, s)], data[(b, s)], key)
    for a in ARMS:
        for key in ("net_ft", "food_rate_ft", "poison_rate_ft", "net_am", "path", "motor_rate", "stranded", "meals_rate"):
            C[f"{a}_silicon-biology_{key}"] = M.paired(data[(a, "silicon")], data[(a, "biology")], key)
    # evidence at taste
    ev = {}
    for s in SUBS:
        cr = [x for r in data[("learn", s)] for x in credit(r)]
        known = [x for x in cr if x is not None]
        lived = sum((100.0 - (r["moving"] or 10000) * 0.01) for r in data[("learn", s)])
        ev[s] = dict(tastes=len(cr), absent=sum(x is None for x in cr), credit_share=float(np.mean(known)) if known else None,
                     tastes_per_lived_s=len(cr) / max(lived, 1e-9),
                     writes=len(cr))
    out["evidence_at_taste"] = ev
    # replay: learn and informed lives, each into both substrates
    jobs = [(f"{a}_{s}_s0-31", i, t) for a in ("learn", "informed") for s in SUBS for i in range(64) for t in SUBS]
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(7, mp_context=multiprocessing.get_context("spawn")) as pool:
        rep = list(pool.map(rjob, jobs, chunksize=4))
    pickle.dump(rep, open(BIG / "stage1_replay.pkl", "wb"))
    selfs = [x["identical_to_closed_loop"] for x in rep if x["identical_to_closed_loop"] is not None]
    out["replay_self_identity"] = dict(n=len(selfs), identical=int(sum(selfs)))
    RS = {}
    for a in ("learn", "informed"):
        for src in SUBS:
            for tgt in SUBS:
                X = [x for x in rep if x["tag"] == f"{a}_{src}_s0-31" and x["target"] == tgt]
                resp = [x["resp"][f"S{k}"]["resp"] for x in X for k in (0, 1) if x["resp"][f"S{k}"]["resp"] is not None]
                own = [x["resp"][f"S{k}"]["own_rate"] for x in X for k in (0, 1)]
                mown = [v for x in X for v in x["resp"]["motor_own_rates"]]
                pur = [x["resp"]["sensor_spike_purity"] for x in X if x["resp"]["sensor_spike_purity"] is not None]
                imb = [max(x["resp"]["motor_own_rates"]) / max(min(x["resp"]["motor_own_rates"]), 0.01) for x in X]
                link = [x["resp"][f"M{k}"]["linked"] / max(x["resp"][f"M{k}"]["spikes"], 1) for x in X for k in (0, 1)
                        if x["resp"][f"M{k}"]["spikes"] > 0]
                q = lambda v: [float(np.percentile(v, p)) for p in (10, 50, 90)] if len(v) else None
                RS[f"{a}_inputs-{src}_into-{tgt}"] = dict(
                    lives=len(X), sensor_resp_p10_50_90=q(resp), sensor_resp_mean=float(np.mean(resp)) if resp else None,
                    sensor_own_rate_p10_50_90=q(own), sensor_spike_purity_p10_50_90=q(pur),
                    motor_own_rate_p10_50_90=q(mown), motor_linked_share_p10_50_90=q(link),
                    motor_own_imbalance_ratio_p10_50_90=q(imb),
                    pulses_per_s_mean=float(np.mean([x["resp"]["pulses_per_s"] for x in X])))
        # paired over seeds: silicon - biology on identical inputs
        for src in SUBS:
            def seedmean(tgt, f):
                X = [x for x in rep if x["tag"] == f"{a}_{src}_s0-31" and x["target"] == tgt]
                d = {}
                for x in X:
                    v = f(x)
                    if v is not None:
                        d.setdefault(x["seed"], []).append(v)
                return {k: np.mean(v) for k, v in d.items()}
            for name, f in (("sensor_resp", lambda x: np.nanmean([x["resp"][f"S{k}"]["resp"] if x["resp"][f"S{k}"]["resp"] is not None else np.nan for k in (0, 1)])),
                            ("sensor_own_rate", lambda x: np.mean([x["resp"][f"S{k}"]["own_rate"] for k in (0, 1)])),
                            ("motor_own_rate", lambda x: np.mean(x["resp"]["motor_own_rates"]))):
                A, Bm = seedmean("silicon", f), seedmean("biology", f)
                ks = sorted(set(A) & set(Bm))
                RS[f"{a}_inputs-{src}_silicon-biology_{name}"] = M.boot([A[k] - Bm[k] for k in ks])
    out["replay"] = RS
    # branch (R6)
    J = out["job"]
    d = C["learn_silicon-biology_net_ft"]
    stop = J["informed_silicon"]["all"] and J["learn_silicon"]["all"] and d[1] > 0.10
    out["branch"] = dict(informed_silicon_job=J["informed_silicon"], learn_silicon_job=J["learn_silicon"],
                         learn_silicon_minus_biology_net_ft=d, stop_historical_branch=bool(stop),
                         decision="stages 2-3 not triggered" if stop else "proceed to stage 2")
    json.dump(out, open(OUT / "stage1.json", "w"), indent=1, default=float)
    print(json.dumps(out["branch"], indent=1, default=float))


if __name__ == "__main__":
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    main()
