"""D79: independently recompute D78 summaries and inspect D77/D78 recorded counters.

No simulation. Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python lab/alloc_review.py > lab/v/alloc_review.log
"""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ("alloc_confirm", "alloc_stage2_W", "alloc_dilution", "noisy_resource_observe")


def read(name):
    return json.loads((ROOT / f"lab/v/{name}.json").read_text())


def interval(x):
    lo, med, hi = np.quantile(x, [.025, .5, .975])
    return {"median": float(med), "ci95": [float(lo), float(hi)]}


def comparisons(name):
    data = read(name)
    out = {}
    for family, record in data["families"].items():
        lives = record["lives"]
        seeds = sorted({r["seed"] for r in lives})
        order = [(s, c) for s in seeds for c in ("red", "blue")]
        sample = np.random.default_rng(0).integers(0, len(seeds), (2000, len(seeds)))
        indices = np.concatenate((2 * sample, 2 * sample + 1), axis=1)
        by = {(r["rule"], r["seed"], r["first"]): r for r in lives}
        efficiency = {}
        for rule in sorted({r["rule"] for r in lives}):
            arr = np.array([by[rule, s, c]["result"][:5] for s, c in order], float)
            efficiency[rule] = arr[indices, 2].sum(axis=1) / arr[indices, 3].sum(axis=1)
        gap = efficiency["vtold"] - efficiency["circuit"]
        closure = {r: (e - efficiency["circuit"]) / gap for r, e in efficiency.items()
                   if r not in ("vtold", "circuit")}
        names = {"W": "W1000", "none": "design"} if name == "alloc_confirm" else {}
        recomputed = {names.get(r, r): interval(x) for r, x in closure.items()}
        comparison = ("W1000-design", "none") if name == "alloc_confirm" else ("W-E", "E")
        recomputed[comparison[0]] = interval(closure["W"] - closure[comparison[1]])
        for label, values in recomputed.items():
            old = record["summary"][label]
            for field in ("median", "ci95"):
                assert np.max(np.abs(np.array(values[field]) - old[field])) < 1e-12, (name, family, label)
        out[family] = dict(seed_pairs=len(seeds), lives_per_arm=len(order),
                           bootstrap_gap_range=[float(gap.min()), float(gap.max())], recomputed=recomputed)
    return out


def main():
    out = {n: comparisons(n) for n in INPUTS[:2]}
    out["saved_bits_per_stream"] = []
    for life in read("alloc_dilution")["lives"]:
        streams = [s for s in life["streams"] if s["family"] != "default"]
        out["saved_bits_per_stream"].append(dict(
            rule=life["rule"], seed=life["seed"], first=life["first"], streams=len(streams),
            positive=sum(s["saved"] > 0 for s in streams),
            minimum=min(s["saved"] for s in streams), maximum=max(s["saved"] for s in streams),
            positive_streams=[dict(kind=s["kind"], saved=s["saved"]) for s in streams if s["saved"] > 0]))
    out["resource_counter_labels"] = []
    for life in read("noisy_resource_observe")["lives"]:
        counters = life["counters"]
        visits, calls = counters["global_stream_scans"], counters["predict_calls"]
        assert visits == 168 * calls
        out["resource_counter_labels"].append(dict(world=life["world"], P=life["P"], first=life["first"],
            stream_visits_labelled_scans=visits, full_prediction_scans=calls,
            nonleaf_evaluations_labelled_part_reads=counters.get("msg_part_reads", 0)))
    out["provenance"] = dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        hashes={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                for p in ["lab/alloc_review.py"] + [f"lab/v/{n}.json" for n in INPUTS]})
    text = json.dumps(out, indent=2) + "\n"
    (ROOT / "lab/v/alloc_review.json").write_text(text)
    print(text, end="")
    print("PASS: all D78 fresh-comparison medians/intervals reproduced; stream visits equal 168 * prediction calls")


if __name__ == "__main__":
    main()
