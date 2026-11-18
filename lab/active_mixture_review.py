"""D79 lead-agent check of the observer's raw predictions; no simulation.

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python
lab/active_mixture_review.py > lab/v/active_mixture_review.log
"""
import hashlib
import json
import math
from pathlib import Path
import pickle

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "lab/v/active_mixture_audit.pkl"


def weighted_probability(row, families, excluded=()):
    pairs = [(float(w), float(p)) for w, p, family in zip(row["w"], row["q"], families)
             if math.isfinite(p) and family not in excluded]
    return math.fsum(w * p for w, p in pairs) / math.fsum(w for w, _ in pairs)


def loss(p, letter):
    return -math.log2(max(1e-12, min(1-1e-12, p if letter else 1-p)))


def main():
    payload = pickle.loads(RAW.read_bytes())
    summary = json.loads((ROOT / "lab/v/active_mixture_audit.json").read_text())
    result = []
    for life in payload["lives"]:
        if not life["observe"]:
            continue
        ps, fs = life["predictions"], life["families"]
        ts = [t for t in life["tastes"] if t["accepted"] and t["issued"] is not None]
        pre_post, timing, benefit = [], [], []
        max_error = max(abs(weighted_probability(p, fs)-p["p1"]) for p in ps)
        for t in ts:
            p = ps[t["issued"]]
            timing.append(t["t"] - p["t"])
            without = weighted_probability(p, fs, ("clock", "integrator", "rhythm"))
            benefit.append(loss(without, t["letter"])-loss(p["p1"], t["letter"]))
            simultaneous = weighted_probability(t["entry"], fs)
            pre_post.append(loss(simultaneous, t["letter"])-t["actual_scored_bits"])
        recorded = next(r for r in summary["lives"] if (r["rule"], r["first"]) == (life["rule"], life["first"]))
        delta = math.fsum(benefit)
        assert max_error < 1e-12
        assert abs(delta-recorded["windows"][-1]["delta_bits"]["non_event"]["total"]) < 1e-10
        result.append(dict(rule=life["rule"], first=life["first"], accepted=len(ts),
            non_event_delta_bits=delta, reconstruction_max_error=max_error,
            taste_minus_issued_time_s=[min(timing), max(timing)], issued_after_taste_clock=sum(t < 0 for t in timing),
            simultaneous_minus_scored_bits=dict(signed=math.fsum(pre_post),
                absolute=math.fsum(abs(x) for x in pre_post), maximum_absolute=max(abs(x) for x in pre_post))))
    out = dict(raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), lives=result)
    text = json.dumps(out, indent=2) + "\n"
    (ROOT / "lab/v/active_mixture_review.json").write_text(text)
    print(text, end="")
    print("PASS: independent mixture and leave-out arithmetic agrees with the observer summary")


if __name__ == "__main__":
    main()
