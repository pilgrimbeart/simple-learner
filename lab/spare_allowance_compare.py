"""PROGRAMME test J (D115): the two issued-credit arms of lab/spare_allowance_experiment.py on seeds 142000-142009.
Imports I's unchanged harness; refuses to run unless every source the lives depend on has I's recorded hash.
    timeout 1800s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/spare_allowance_compare.py --compare
    timeout 240s  env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/spare_allowance_compare.py --analyse
"""
import json
import math
from pathlib import Path
import pickle
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C
import spare_allowance_experiment as X

BASE = ROOT / "lab/v/spare_allowance_compare"
SEEDS = list(range(142000, 142010))
ARMS = ("issued", "issued+gate")
CONDS = ("seq", "time", "allfood")
PILOT_CAPTURE = ROOT / "lab/v/spare_allowance_pilot_capture.json"
PILOT_RAW = ROOT / "lab/v/spare_allowance_pilot.pkl"


def verify_sources():
    cap = json.loads(PILOT_CAPTURE.read_text())
    rec = cap["provenance"]["sha256"]
    now = {p: X.digest(ROOT / p) for p in X.SOURCES}
    assert rec == now, ("sources differ from I's", {p for p in rec if rec[p] != now.get(p)})
    assert X.digest(PILOT_RAW) == cap["raw_sha256"]
    assert cap["G"] == X.G == 258 and cap["cap"] == X.CAP == 2300
    return cap


def jobs_all():
    return [(c, a, s, f) for c in CONDS for a in ARMS for s in SEEDS for f in ("red", "blue")]


def compare():
    cap = verify_sources()
    allj = jobs_all()
    assert len(allj) == 120 and len(set(allj)) == 120
    pilot = {(r["cond"], r["arm"], r["seed"], r["first"]): r for r in pickle.loads(PILOT_RAW.read_bytes())}
    reuse = [j for j in allj if j in pilot]
    assert len(reuse) == 12, len(reuse)
    new = [j for j in allj if j not in pilot]
    assert len(new) == 108
    res = X.run(new, "compare_new", "timeout 1800s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
                                     ".venv/bin/python lab/spare_allowance_compare.py --compare")
    meta = dict(reused_pilot_lives=reuse, new_lives=len(res), pilot_capture_sha256=X.digest(PILOT_CAPTURE), pilot_raw_sha256=cap["raw_sha256"],
                runner_sha256=X.digest(Path(__file__)))
    BASE.with_name(BASE.name + "_meta").with_suffix(".json").write_text(json.dumps(meta, indent=1, default=str) + "\n")


def gate_summary(rr, a):
    out = dict(deletion_transfers=float(np.mean([r["alloc"]["transfers"] for r in rr])))
    if a == "issued+gate":
        out["allowance_only_transfers"] = float(np.mean([r["gate"]["counters"].get("allowance-only transfers", 0) for r in rr]))
        out["births_after"] = float(np.mean([r["gate"]["counters"].get("births_after_allowance_only_transfer", 0) for r in rr]))
    return out


def analyse():
    verify_sources()
    pilot = pickle.loads(PILOT_RAW.read_bytes())
    new = pickle.loads((ROOT / "lab/v/spare_allowance_compare_new.pkl").read_bytes())
    by = {}
    for r in new + [r for r in pilot if (r["cond"], r["arm"], r["seed"], r["first"]) in set(jobs_all())]:
        k = (r["cond"], r["arm"], r["seed"], r["first"])
        assert k not in by, ("duplicate", k)
        by[k] = r
    assert set(by) == set(jobs_all()), set(jobs_all()) ^ set(by)
    fail = []
    for k, r in by.items():
        cr, al = r["credit"], r["alloc"]
        ok = (cr["max_reconstruction_error"] <= 1e-9 and cr["counters"]["completed_accepted_updates"] == r["ntaste"]
              and al["cap"] == 2300 and al["peak"] <= 2300)
        if r["arm"] == "issued+gate":
            g = r["gate"]
            ok = ok and g["counters"].get("transfers with deletion", 0) == al["transfers"] and g["allowance_sum"] == g["allowance_sum_at_install"]
        if not ok:
            fail.append(str(k))
    allfood = {}
    for s in SEEDS:
        for f in ("red", "blue"):
            i, g = by["allfood", "issued", s, f], by["allfood", "issued+gate", s, f]
            same = (X.same_result(i["result"], g["result"]) and i["behaviour"] == g["behaviour"] and i["fingerprint"] == g["fingerprint"]
                    and i["body_fingerprint"] == g["body_fingerprint"] and not g["gate"]["counters"].get("allowance-only transfers"))
            allfood[f"{s} {f}"] = same
            if not same:
                fail.append(f"allfood {s} {f} not identical")
    out = dict(mechanical_failures=fail, allfood_exact=allfood)
    if fail:
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
        raise SystemExit("mechanical checks failed: " + "; ".join(fail[:5]))
    order = [(s, f) for s in SEEDS for f in ("red", "blue")]
    k = np.random.default_rng(0).integers(0, len(SEEDS), (2000, len(SEEDS)))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)

    def boot(vals):
        x = np.array(vals, dtype=float)
        return dict(per_life_mean=float(x.mean()), ci95=[float(v) for v in np.quantile(x[idx].mean(1), [.025, .975])])

    def decide(ci, other=False):
        lo, hi = ci
        if other:
            return "no harm beyond the margin" if lo > -.10 else "harm beyond the margin not excluded"
        if lo > 0:
            return "improvement"
        if lo >= -.10 and hi <= .10:
            return "within margin"
        if hi < 0:
            return "worse"
        return "inconclusive"
    fam = {}
    for c in ("seq", "time"):
        hist, hpath = C.history(c)
        X_ = C.closure_samples({a: (lambda s, f, a=a: by[c, a, s, f]["result"]) for a in ARMS}, hist, SEEDS)
        d = X_["issued+gate"] - X_["issued"]
        ci = C.ci(d)
        secs = X.SECS[c]
        per = {}
        for a in ARMS:
            rr = [by[c, a, s, f] for s, f in order]
            per[a] = dict(gap_closed=C.ci(X_[a]),
                          last_third_efficiency_per_life_mean=float(np.mean([r["result"][2] / r["result"][3] for r in rr])),
                          last_third_efficiency_pooled=float(sum(r["result"][2] for r in rr) / sum(r["result"][3] for r in rr)),
                          gain_per_10s=float(np.mean([r["result"][0] / secs * 10 for r in rr])),
                          food=int(sum(r["food"] for r in rr)), poison=int(sum(r["poison"] for r in rr)),
                          food_last_third=int(sum(r["food_last_third"] for r in rr)), poison_last_third=int(sum(r["poison_last_third"] for r in rr)),
                          reward_gain_mean=float(np.mean([r["result"][0] for r in rr])),
                          material=dict(peak_units=float(np.mean([r["alloc"]["peak"] for r in rr])), final_units=float(np.mean([r["final_units"] for r in rr])),
                                        grown={g: float(np.mean([r["grown"][g] for r in rr])) for g in X.FAMS}),
                          activity=dict(births=float(np.mean([r["births"] for r in rr])), recycled=float(np.mean([r["recycled"] for r in rr])),
                                        cpu_s=float(np.mean([r["cpu_s"] for r in rr]))),
                          communication=(dict(donor_scans=float(np.mean([r["gate"]["counters"].get("donor scans", 0) for r in rr])),
                                              stream_visits=float(np.mean([r["gate"]["counters"].get("stream visits in donor scans", 0) for r in rr])))
                                         if a == "issued+gate" else "not counted in the arm without the adapter"),
                          gate=gate_summary(rr, a))
        sec = {}
        for w in ("last_third", "first_third", "full"):
            for m in ("bits", "errors"):
                def val(r):
                    sel = [(p, y) for t, p, y in r["trace_acc"] if (w == "full") or (w == "last_third" and t >= 2 * secs / 3) or (w == "first_third" and t < secs / 3)]
                    if m == "bits":
                        return sum(-math.log2(min(1 - 1e-12, max(1e-12, p if y else 1 - p))) for p, y in sel) / len(sel)
                    return sum(.5 if p == .5 else float((p > .5) != bool(y)) for p, y in sel) / len(sel)
                sec[f"{w} issued {m} per taste, gate - baseline" + ("" if w == "last_third" else " (diagnostic)")] = boot(
                    [val(by[c, "issued+gate", s, f]) - val(by[c, "issued", s, f]) for s, f in order])
        fam[c] = dict(reference=hpath, gate_minus_baseline_gap_closed=ci, per_arm=per, secondary=sec,
                      per_life={f"{a} {s} {f}": dict(result=by[c, a, s, f]["result"][:5]) for a in ARMS for s, f in order})
    fam["seq"]["decision"] = decide(fam["seq"]["gate_minus_baseline_gap_closed"]["ci95"])
    fam["time"]["decision"] = decide(fam["time"]["gate_minus_baseline_gap_closed"]["ci95"])
    fam["seq"]["no_harm_check_as_other_family"] = decide(fam["seq"]["gate_minus_baseline_gap_closed"]["ci95"], other=True)
    fam["time"]["no_harm_check_as_other_family"] = decide(fam["time"]["gate_minus_baseline_gap_closed"]["ci95"], other=True)
    out.update(families=fam, lives=len(by), meta=json.loads(BASE.with_name(BASE.name + "_meta").with_suffix(".json").read_text()),
               analysis_sha256=X.digest(Path(__file__)))
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    for c in ("seq", "time"):
        f = fam[c]
        print(c, "gate - baseline gap closed", f["gate_minus_baseline_gap_closed"], f["decision"], "| as other family:", f["no_harm_check_as_other_family"])
        for a in ARMS:
            p = f["per_arm"][a]
            print("  ", a, json.dumps({k: p[k] for k in ("gap_closed", "last_third_efficiency_per_life_mean", "last_third_efficiency_pooled",
                                                      "gain_per_10s", "food", "poison", "material", "activity", "gate")}))
        for k_, v in f["secondary"].items():
            print("   ", k_, v)
    print("allfood exact in all", sum(allfood.values()), "of", len(allfood))


if __name__ == "__main__":
    {"--compare": compare, "--analyse": analyse}[sys.argv[1]]()
