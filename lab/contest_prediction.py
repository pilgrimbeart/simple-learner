"""D94: the D93 recorder on D78 stage 1's capped rules (E equal, W weight contest, R event ruler), seq 17,
seeds 142000-142009, each life checked against lab/v/alloc_stage1.json; analysed with D93's combiners
alongside D93's low and high lives.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/contest_prediction.py --run
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/contest_prediction.py --analyse
"""
import json
from pathlib import Path
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C
import room_prediction as RP

BASE = ROOT / "lab/v/contest_prediction"
STAGE1 = ROOT / "lab/v/alloc_stage1.json"
RULES = ("E", "W", "R")
SEEDS = range(142000, 142010)


def one(job):
    from stage2_lang import arms as S
    rule, seed, first = job
    original, out = S.live, {}

    def live(lf, secs):
        rec = RP.Recorder(lf)
        lived = original(lf, secs)
        out.update(rows=rec.rows, fam=rec.fam.tolist())
        return lived
    S.live = live                                    # alloc_compare.one wraps this after installing the rule
    try:
        r = C.one(("seq", rule, 560, seed, first))
    finally:
        S.live = original
    return dict(r, name=rule, **out)


def run():
    t0 = time.monotonic()
    jobs = [(r, s, c) for r in RULES for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    ref = {(l["rule"], l["seed"], l["first"]): l["result"] for l in json.loads(STAGE1.read_text())["families"]["seq"]["lives"]}
    bad = []
    for r in res:
        a, b = json.loads(json.dumps(r["result"])), ref[r["rule"], r["seed"], r["first"]]
        if [v for i, v in enumerate(a) if i not in (5, 7)] != [v for i, v in enumerate(b) if i not in (5, 7)] or abs(a[7] - b[7]) > 1e-12:
            bad.append((r["rule"], r["seed"], r["first"]))
    summary = dict(identity=dict(lives=len(res), mismatches=bad), wall_s=time.monotonic() - t0, G=C.G,
                   reference_sha256=RP.digest(STAGE1), source_sha256={p: RP.digest(ROOT / p) for p in
                   ("lab/contest_prediction.py", "lab/room_prediction.py", "lab/alloc_compare.py", "lab/alloc_rules.py", "lab/grownet.py")})
    BASE.with_suffix(".pkl").write_bytes(pickle.dumps(dict(lives=res, summary=summary)))
    BASE.with_name(BASE.name + "_capture").with_suffix(".json").write_text(json.dumps(summary, indent=1) + "\n")
    print("identity", "PASS" if not bad else f"FAIL {bad}", "wall", summary["wall_s"], flush=True)
    assert not bad


def analyse():
    cap = pickle.loads(BASE.with_suffix(".pkl").read_bytes())
    assert not cap["summary"]["identity"]["mismatches"]
    d93 = pickle.loads(RP.BASE.with_suffix(".pkl").read_bytes())
    lives = [l for l in d93["lives"] if l["name"] in ("low", "high")] + cap["lives"]
    by = {(l["name"], l["seed"], l["first"]): (RP.combiners(l), l) for l in lives}
    order = [(s, c) for s in SEEDS for c in ("red", "blue")]
    k = np.random.default_rng(0).integers(0, 10, (2000, 10))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    arms = ("low", "E", "W", "R", "high")
    comb = ("native mixture", "fresh Bayes, event streams only", "best single stream in hindsight")
    out = dict(per_arm={}, differences={})
    for a in arms:
        rows = [by[a, s, f] for s, f in order]
        out["per_arm"][a] = dict(
            **{f"{c} | {w}": dict(bits=float(sum(x[0][0][c, w]["bits"] for x in rows) / sum(x[0][0][c, w]["n"] for x in rows)),
                                  errors=float(sum(x[0][0][c, w]["errors"] for x in rows) / sum(x[0][0][c, w]["n"] for x in rows)))
               for c in comb for w in ("full", "last_third")},
            event_grown_share=float(np.mean([x[0][1]["event_grown_share"] for x in rows])),
            event_mean_span=float(np.mean([x[0][1]["event_mean_span"] for x in rows])),
            efficiency=float(np.mean([x[0][2] for x in rows])),
            grown=({f: float(np.mean([x[1]["grown"][f] for x in rows])) for f in C.FAM} if "grown" in rows[0][1] else None))
        # event span in the last third only, from the raw rows
        sp = []
        for x in rows:
            l = x[1]
            ev = np.array(l["fam"]) == "event"
            for r in l["rows"]:
                if r["taste_t"] >= 200.:
                    m = ev & np.isfinite(r["q"])
                    sp += list(r["span"][m])
        out["per_arm"][a]["event_mean_span_last_third"] = float(np.mean(sp))
    for a, b in (("W", "high"), ("W", "E"), ("R", "high"), ("W", "R"), ("E", "low")):
        for c in comb:
            for m in ("bits", "errors"):
                va = np.array([by[a, s, f][0][0][c, "last_third"][m] / by[a, s, f][0][0][c, "last_third"]["n"] for s, f in order])
                vb = np.array([by[b, s, f][0][0][c, "last_third"][m] / by[b, s, f][0][0][c, "last_third"]["n"] for s, f in order])
                dd = (va - vb)[idx].mean(1)
                out["differences"][f"{a} - {b} | {c} | last_third | {m}"] = dict(mean=float((va - vb).mean()),
                                                                                  ci95=[float(x) for x in np.quantile(dd, [.025, .975])])
    out["provenance"] = dict(capture=cap["summary"], d93_pickle_sha256=RP.digest(RP.BASE.with_suffix(".pkl")),
                             analysis_sha256=RP.digest(Path(__file__)))
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    for a, v in out["per_arm"].items():
        print(a, json.dumps({k: (round(x["bits"], 3), round(x["errors"], 3)) if isinstance(x, dict) and "bits" in x else x for k, x in v.items()}))
    for k_, v in out["differences"].items():
        print(f"{k_:80s} {v['mean']:+.3f} [{v['ci95'][0]:+.3f},{v['ci95'][1]:+.3f}]")


if __name__ == "__main__":
    {"--run": run, "--analyse": analyse}[sys.argv[1]]()
